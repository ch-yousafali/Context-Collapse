# Context-Collapse

> **Smart Tech News Synthesizer** — A self-hosted, AI-powered intelligence dashboard for developers.

![Status](https://img.shields.io/badge/status-vibe--coded-brightgreen)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20Flask%20%2B%20Gemini-blue)

## What It Does

Context-Collapse eliminates information overload by:

1. **Scraping** disparate technical sources (Hacker News, Reddit, Engineering Blogs)
2. **Deduplicating** and clustering related articles into unified "Story Events"
3. **Synthesizing** punchy TL;DRs and "Developer Impact Scores" via Gemini AI
4. **Presenting** everything in a beautiful, scannable dark-mode editorial dashboard

## Architecture

+------------------+     +-------------------+     +------------------+
|   Target APIs    |     |   Scraper Engine  |     |  Local DB/Cache  |
|                  |     |                   |     |                  |
|  Hacker News     |---->|  aggregator.py    |---->|  feeds.db        |
|  Reddit          |     |  - HN Firebase    |     |  raw_feeds.json  |
|  RSS Feeds       |     |  - Reddit JSON    |     |  stories.json    |
|                  |     |  - feedparser     |     |                  |
+------------------+     +-------------------+     +------------------+
                                                            |
                                                            v
+------------------+     +-------------------+     +------------------+
|   React Frontend |<<----|  Flask API Server |<<----|  LLM Synthesizer |
|                  |     |                   |     |                  |
|  App.jsx         |     |  app.py           |     |  synthesizer.py  |
|  - Hero Panel    |<<----|  - /api/sync      |<<----|  - Gemini 2.5    |
|  - Impact Filter |    |  - /api/stories   |     |  - JSON Schema   |
|  - Archive       |     |  - /api/archive   |     |  - Clustering    |
|  - Source Drawer |     |  - CORS enabled   |     |  - TL;DR Gen     |
+------------------+     +-------------------+     +------------------+
         ^
         |
   User clicks "Sync Now" or opens dashboard

   
## Data Sources

- **Hacker News** (Firebase API) — Top stories
- **Reddit** (JSON endpoint) — r/programming, r/webdev
- **RSS Feeds** — Figma Blog, Vercel Blog, Pragmatic Engineer

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com/app/apikey) (optional — falls back to no-AI mode)

### 1. Clone & Configure
```bash
cd context-collapse
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Run Everything
```bash
./start.sh
```

Or manually:

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 3. Open
- **Dashboard:** http://localhost:5173
- **API:** http://localhost:5001

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/sync` | Trigger scraper + AI synthesis |
| `GET` | `/api/stories?min_score=1&include_archived=false` | Get clustered stories |
| `POST` | `/api/stories/<id>/archive` | Mark story as read |
| `POST` | `/api/stories/<id>/unarchive` | Unarchive story |
| `GET` | `/api/stats` | Dashboard stats |
| `GET` | `/api/health` | Health check |

## Frontend Features

- 🌑 **Premium dark mode** — Slate-900 terminal aesthetic
- ⚡ **Hero panel** — Highest impact story featured prominently
- 📊 **Impact scoring** — 1-10 color-coded badges
- 🔍 **Impact filter** — Slider to show only high-signal stories (7+)
- 📁 **Archive** — Mark stories as read to hide them
- 🔗 **Source aggregation** — Click any card to see all original sources
- 🏷️ **Key terms** — Auto-extracted technical keywords

## Project Structure

```
context-collapse/
├── backend/
│   ├── app.py              # Flask API server
│   ├── aggregator.py       # Scraper engine (HN, Reddit, RSS)
│   ├── synthesizer.py      # Gemini AI clustering & summarization
│   ├── requirements.txt    # Python deps
│   ├── feeds.db            # SQLite archive tracking (auto-created)
│   ├── raw_feeds.json      # Raw ingestion cache (auto-created)
│   └── stories.json        # Synthesized output (auto-created)
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main dashboard application
│   │   ├── main.jsx        # React entry point
│   │   └── index.css       # Tailwind + custom styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── .env.example
├── start.sh
└── README.md
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | No* | Google Gemini API key for AI synthesis |
| `VITE_API_URL` | No | Override backend URL (default: `http://localhost:5001`) |

\* Without Gemini, the system falls back to individual story events with default scores.

## Tech Stack

- **Frontend:** React 19, Vite, Tailwind CSS, Lucide Icons
- **Backend:** Flask, Flask-CORS, SQLite
- **AI:** Google Gemini 2.5 Flash (JSON schema mode)
- **Scraping:** requests, feedparser

## License

MIT — Built for developers, by developers.
# Context-Collapse
