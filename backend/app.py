"""
Context-Collapse: Smart Tech News Synthesizer
Phase 3: The API Endpoint
"""
import os
import json
import sqlite3
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS

from aggregator import run_ingestion
from synthesizer import run_synthesis

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

DB_PATH = "feeds.db"
STORIES_FILE = "stories.json"

# --- Helper: Load stories from JSON ---
def load_stories():
    try:
        with open(STORIES_FILE, "r") as f:
            data = json.load(f)
            return data.get("stories", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- Helper: Save stories to JSON ---
def save_stories(stories):
    with open(STORIES_FILE, "w") as f:
        json.dump({
            "synthesized_at": datetime.now(timezone.utc).isoformat(),
            "count": len(stories),
            "stories": stories
        }, f, indent=2)

# --- Helper: Archive tracking in SQLite ---
def init_archive_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS archived_stories (
        story_id TEXT PRIMARY KEY,
        archived_at TEXT
    )""")
    conn.commit()
    conn.close()

def is_archived(story_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM archived_stories WHERE story_id = ?", (story_id,))
    result = c.fetchone() is not None
    conn.close()
    return result

def archive_story(story_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO archived_stories (story_id, archived_at) VALUES (?, ?)",
              (story_id, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

# --- Routes ---

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

@app.route("/api/sync", methods=["POST"])
def sync():
    """Trigger scraper + LLM synthesis pipeline."""
    try:
        raw_items = run_ingestion()
        if not raw_items:
            return jsonify({"error": "No items ingested"}), 500

        stories = run_synthesis(raw_items)
        return jsonify({
            "success": True,
            "items_ingested": len(raw_items),
            "stories_synthesized": len(stories),
            "stories": stories
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stories", methods=["GET"])
def get_stories():
    """Return aggregated, AI-clustered story events."""
    min_score = request.args.get("min_score", type=int, default=1)
    include_archived = request.args.get("include_archived", "false").lower() == "true"

    stories = load_stories()

    # Filter by min impact score
    stories = [s for s in stories if s.get("impact_score", 0) >= min_score]

    # Filter out archived unless requested
    if not include_archived:
        stories = [s for s in stories if not is_archived(s.get("id", ""))]

    # Mark archived status
    for s in stories:
        s["is_archived"] = is_archived(s.get("id", ""))

    return jsonify({
        "count": len(stories),
        "stories": stories
    })

@app.route("/api/stories/<story_id>/archive", methods=["POST"])
def archive(story_id):
    """Mark a story as read/archived."""
    archive_story(story_id)
    return jsonify({"success": True, "story_id": story_id, "archived": True})

@app.route("/api/stories/<story_id>/unarchive", methods=["POST"])
def unarchive(story_id):
    """Unarchive a story."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM archived_stories WHERE story_id = ?", (story_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "story_id": story_id, "archived": False})

@app.route("/api/stats", methods=["GET"])
def stats():
    """Dashboard stats."""
    stories = load_stories()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM archived_stories")
    archived_count = c.fetchone()[0]
    conn.close()

    return jsonify({
        "total_stories": len(stories),
        "archived": archived_count,
        "unread": len(stories) - archived_count,
        "avg_impact": round(sum(s.get("impact_score", 0) for s in stories) / max(len(stories), 1), 1),
        "last_sync": stories[0].get("timestamp", "Never") if stories else "Never"
    })

# --- Init ---
init_archive_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)