"""
Context-Collapse: Smart Tech News Synthesizer
Phase 1: The Ingestion & Engine
"""
import requests
import feedparser
import json
import sqlite3
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

DB_PATH = "feeds.db"
RAW_FEEDS_PATH = "raw_feeds.json"


def fetch_hackernews(limit=30):
    """Fetch top stories from Hacker News Firebase API."""
    try:
        top_ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=15
        ).json()

        stories = []
        for item_id in top_ids[:limit]:
            try:
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                    timeout=10
                ).json()
                if item and item.get("url"):
                    stories.append({
                        "platform": "Hacker News",
                        "title": item.get("title", ""),
                        "url": item["url"],
                        "discussion_url": f"https://news.ycombinator.com/item?id={item_id}",
                        "author": item.get("by", ""),
                        "score": item.get("score", 0),
                        "comments": item.get("descendants", 0),
                        "time": datetime.fromtimestamp(
                            item.get("time", 0), tz=timezone.utc
                        ).isoformat(),
                        "engagement_metrics": f"{item.get('score', 0)} points | {item.get('descendants', 0)} comments"
                    })
            except Exception as e:
                print(f"HN item {item_id} error: {e}")
                continue
        return stories
    except Exception as e:
        print(f"HN fetch error: {e}")
        return []


def fetch_reddit(subreddit="programming", limit=25):
    """Fetch hot posts from Reddit via JSON endpoint."""
    try:
        headers = {
            "User-Agent": "ContextCollapseBot/1.0 (Personal Intelligence Dashboard)"
        }
        resp = requests.get(
            f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}",
            headers=headers,
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()

        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            url = post.get("url_overridden_by_dest") or post.get("url", "")
            if not url or url.startswith("/r/"):
                continue
            posts.append({
                "platform": "Reddit",
                "subreddit": subreddit,
                "title": post.get("title", ""),
                "url": url,
                "discussion_url": f"https://www.reddit.com{post.get('permalink', '')}",
                "author": post.get("author", ""),
                "score": post.get("ups", 0),
                "comments": post.get("num_comments", 0),
                "time": datetime.fromtimestamp(
                    post.get("created_utc", 0), tz=timezone.utc
                ).isoformat(),
                "engagement_metrics": f"{post.get('ups', 0)} upvotes | {post.get('num_comments', 0)} comments"
            })
        return posts
    except Exception as e:
        print(f"Reddit r/{subreddit} error: {e}")
        return []


def fetch_rss(feed_url, platform_name):
    """Fetch and parse an RSS feed."""
    try:
        feed = feedparser.parse(feed_url)
        entries = []
        for entry in feed.entries[:10]:
            published = entry.get("published", "")
            try:
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    published = dt.isoformat()
            except Exception:
                published = datetime.now(timezone.utc).isoformat()

            entries.append({
                "platform": platform_name,
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "discussion_url": entry.get("link", ""),
                "author": entry.get("author", ""),
                "summary": entry.get("summary", "")[:500],
                "time": published,
                "engagement_metrics": "RSS Feed"
            })
        return entries
    except Exception as e:
        print(f"RSS {feed_url} error: {e}")
        return []


def normalize_url(url):
    """Strip tracking params and normalize URL for dedup."""
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except Exception:
        return url


def deduplicate_items(items):
    """Remove duplicates based on normalized URL."""
    seen = set()
    unique = []
    for item in items:
        norm = normalize_url(item["url"])
        if norm not in seen:
            seen.add(norm)
            unique.append(item)
    return unique


def save_raw_feeds(items):
    """Save raw feeds to JSON and SQLite."""
    with open(RAW_FEEDS_PATH, "w") as f:
        json.dump({
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(items),
            "items": items
        }, f, indent=2)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS raw_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        title TEXT,
        url TEXT UNIQUE,
        discussion_url TEXT,
        author TEXT,
        score INTEGER,
        comments INTEGER,
        time TEXT,
        engagement_metrics TEXT,
        fetched_at TEXT
    )""")

    for item in items:
        c.execute("""INSERT OR IGNORE INTO raw_items 
            (platform, title, url, discussion_url, author, score, comments, time, engagement_metrics, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (item.get("platform"), item.get("title"), item.get("url"),
             item.get("discussion_url"), item.get("author"),
             item.get("score", 0), item.get("comments", 0),
             item.get("time"), item.get("engagement_metrics"),
             datetime.now(timezone.utc).isoformat()))

    conn.commit()
    conn.close()


def run_ingestion():
    """Full ingestion pipeline."""
    print("Starting ingestion...")
    all_items = []

    print("  Fetching Hacker News...")
    all_items.extend(fetch_hackernews(30))

    print("  Fetching Reddit r/programming...")
    all_items.extend(fetch_reddit("programming", 25))

    print("  Fetching Reddit r/webdev...")
    all_items.extend(fetch_reddit("webdev", 15))

    print("  Fetching Figma Blog...")
    all_items.extend(fetch_rss("https://www.figma.com/blog/feed/", "Figma Blog"))

    print("  Fetching Vercel Blog...")
    all_items.extend(fetch_rss("https://vercel.com/blog/rss", "Vercel Blog"))

    print("  Fetching Pragmatic Engineer...")
    all_items.extend(fetch_rss("https://newsletter.pragmaticengineer.com/feed", "Pragmatic Engineer"))

    all_items = deduplicate_items(all_items)
    save_raw_feeds(all_items)

    print(f"Ingested {len(all_items)} unique items")
    return all_items


if __name__ == "__main__":
    run_ingestion()
