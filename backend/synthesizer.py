"""
Context-Collapse: Smart Tech News Synthesizer
Phase 2: The AI Synthesizer
"""
import os
import json
import re
from datetime import datetime, timezone

try:
    import google.generativeai as genai
except ImportError:
    genai = None

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

STORY_SCHEMA = {
    "type": "object",
    "properties": {
        "stories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "unified_title": {
                        "type": "string",
                        "description": "A punchy, editorial headline that captures the essence of the story event"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["Frontend", "Backend", "AI/ML", "DevOps", "Security", "Mobile", "Database", "Career", "Release", "Other"],
                        "description": "The technical domain this story belongs to"
                    },
                    "impact_score": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "1 = pure marketing fluff, 10 = breaking change / must-learn tech"
                    },
                    "tldr": {
                        "type": "string",
                        "description": "Exactly 2 sentences. First sentence: what happened. Second sentence: why a developer should care or what action to take. Be cynical and direct."
                    },
                    "source_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Indices of the original articles that belong to this story event (0-based, from the input array)"
                    },
                    "key_terms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "3-5 technical keywords or tags extracted from the story"
                    }
                },
                "required": ["unified_title", "category", "impact_score", "tldr", "source_indices", "key_terms"],
                "additionalProperties": False
            }
        }
    },
    "required": ["stories"],
    "additionalProperties": False
}

SYSTEM_PROMPT = """You are an elite, cynical Senior Software Engineer and Principal Architect. 
Your job is to analyze a batch of technical news headlines and metadata, then group articles that talk about the exact same topic or release into unified "Story Events".

Rules:
- Group aggressively. If two articles mention the same framework release, security vulnerability, or company announcement, they belong to the same Story Event.
- If an article stands completely alone, it gets its own Story Event.
- Write punchy, editorial headlines. No corporate speak.
- The TL;DR must be exactly 2 sentences. First: what happened. Second: developer impact or recommended action.
- Impact Score: 1-3 = marketing fluff / minor update, 4-6 = useful but not urgent, 7-8 = significant, 9-10 = breaking change / must-learn / security critical.
- Be critical. Call out hype. Flag vaporware. Praise genuinely important work.
- Return ONLY valid JSON matching the provided schema. No markdown, no explanations, no conversational text."""

def synthesize_with_gemini(items):
    """Send items to Gemini API for clustering and summarization."""
    if not GEMINI_API_KEY or not genai:
        print("Warning: Gemini API not configured. Using fallback synthesis.")
        return fallback_synthesis(items)

    genai.configure(api_key=GEMINI_API_KEY)

    input_items = []
    for i, item in enumerate(items):
        input_items.append({
            "index": i,
            "platform": item.get("platform", ""),
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "engagement": item.get("engagement_metrics", "")
        })

    user_prompt = f"""Analyze these {len(input_items)} technical news items and group them into Story Events.

Input Articles:
{json.dumps(input_items, indent=2)}

Return JSON matching this exact schema:
{json.dumps(STORY_SCHEMA, indent=2)}"""

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": STORY_SCHEMA
            }
        )

        response = model.generate_content([
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_prompt}]}
        ])

        result = json.loads(response.text)
        return result.get("stories", [])
    except Exception as e:
        print(f"Gemini synthesis error: {e}")
        return fallback_synthesis(items)

def fallback_synthesis(items):
    """Fallback: create individual story events without LLM clustering."""
    stories = []
    for i, item in enumerate(items[:30]):
        stories.append({
            "unified_title": item.get("title", "Untitled"),
            "category": "Other",
            "impact_score": 5,
            "tldr": f"{item.get('title', 'News item')}. Check the original source for details.",
            "source_indices": [i],
            "key_terms": []
        })
    return stories

def build_story_payloads(raw_items, synthesized_stories):
    """Merge synthesized stories with original source metadata."""
    payloads = []
    timestamp = datetime.now(timezone.utc).isoformat()

    for idx, story in enumerate(synthesized_stories):
        story_id = f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{idx+1:03d}"

        sources = []
        for si in story.get("source_indices", []):
            if 0 <= si < len(raw_items):
                src = raw_items[si]
                sources.append({
                    "platform": src.get("platform", ""),
                    "title": src.get("title", ""),
                    "url": src.get("url", ""),
                    "discussion_url": src.get("discussion_url", src.get("url", "")),
                    "engagement_metrics": src.get("engagement_metrics", "")
                })

        payloads.append({
            "id": story_id,
            "unified_title": story.get("unified_title", "Untitled"),
            "impact_score": story.get("impact_score", 5),
            "category": story.get("category", "Other"),
            "tldr": story.get("tldr", ""),
            "sources": sources,
            "key_terms": story.get("key_terms", []),
            "timestamp": timestamp,
            "is_read": False
        })

    payloads.sort(key=lambda x: x["impact_score"], reverse=True)
    return payloads

def run_synthesis(raw_items):
    """Full synthesis pipeline."""
    print("Starting AI synthesis...")
    stories = synthesize_with_gemini(raw_items)
    payloads = build_story_payloads(raw_items, stories)

    with open("stories.json", "w") as f:
        json.dump({
            "synthesized_at": datetime.now(timezone.utc).isoformat(),
            "count": len(payloads),
            "stories": payloads
        }, f, indent=2)

    print(f"Synthesized {len(payloads)} story events")
    return payloads

if __name__ == "__main__":
    test_items = [
        {"platform": "Hacker News", "title": "React 19 is now stable", "url": "https://react.dev", "engagement_metrics": "450 points"},
        {"platform": "Vercel Blog", "title": "How to deploy React 19 Server Components today", "url": "https://vercel.com/blog/react-19", "engagement_metrics": "RSS"},
        {"platform": "Reddit", "title": "Rust 1.85 released with async closures", "url": "https://rust-lang.org", "engagement_metrics": "2.3k upvotes"},
    ]
    result = run_synthesis(test_items)
    print(json.dumps(result, indent=2))