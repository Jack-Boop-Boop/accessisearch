# AccessiSearch

A web search engine that ranks results by accessibility score. Enter a query, select disability categories, and get results re-ranked so the most accessible pages appear first.

**Live demo:** [accessisearch.vercel.app](https://accessisearch.vercel.app) <!-- update with actual URL -->

---

## What It Does

Standard search engines rank by relevance — they have no way to tell you whether a result actually works for a screen reader, a keyboard-only user, or someone who needs simplified language. AccessiSearch adds accessibility as a ranking dimension.

**Pipeline:**
1. Query → Google Custom Search API (top 5 results)
2. Each result URL is fetched server-side and its HTML is parsed
3. Eight analyzers score the page across disability categories (0–10)
4. Results are re-ranked by score and streamed back as they finish
5. Users can switch filters and results re-sort instantly in the browser

---

## Accessibility Categories

| Category | What It Checks |
|---|---|
| **Simplified Language** | Flesch Reading Ease score, paragraph structure, list usage |
| **Dyslexia-Friendly** | Font families, line spacing, paragraph length, justified text |
| **Low Vision** | Relative font units, zoom support, contrast media queries |
| **Screen Reader** | Alt text, semantic landmarks, heading hierarchy, skip links, form labels |
| **Motor / Keyboard** | Keyboard navigability, focus indicators, skip nav, no drag-only interactions |
| **Deaf / Hard of Hearing** | Video captions, audio transcripts, autoplay prevention |
| **Color Blindness** | Link underlines, non-color error indicators, contrast declarations |
| **Cognitive Load** | Navigation structure, heading hierarchy, no auto-refresh, no modals/carousels |

Each result card shows:
- Letter grade (A+ → F)
- Overall score bar
- Weakest category callout
- Full breakdown expandable per category
- Rich snippet from actual page content

---

## Stack

- **Backend:** Python / Flask
- **Search:** Google Custom Search JSON API
- **HTML parsing:** BeautifulSoup4
- **Frontend:** Vanilla JS, inline CSS (no build step)
- **Streaming:** Server-Sent Events (SSE) — results appear progressively
- **Deployment:** Vercel (`@vercel/python`)

---

## Running Locally

**Requirements:** Python 3.10+

```bash
git clone https://github.com/Jack-Boop-Boop/accessisearch.git
cd accessisearch
pip install -r requirements.txt
```

Create `.env`:
```
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CX=your_search_engine_id_here
```

```bash
python app.py
# → http://localhost:3457
```

### Getting API Keys

**Google API Key:**
1. Go to [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
2. Create Credentials → API key
3. Enable **Custom Search API** in APIs & Services → Library
4. Set Application Restrictions to **None**

**Google CX (Search Engine ID):**
1. Go to [programmablesearchengine.google.com](https://programmablesearchengine.google.com)
2. Create a search engine
3. Under Basics, enable **Search the entire web**
4. Copy the Search engine ID

Free tier: 100 queries/day.

---

## Deploying to Vercel

```bash
vercel deploy
```

Set environment variables in Vercel dashboard → Settings → Environment Variables:
- `GOOGLE_API_KEY`
- `GOOGLE_CX`

---

## Project Structure

```
accessisearch/
├── app.py                  # Flask app, Google Search, SSE streaming
├── analyzers/
│   ├── base.py             # BaseAnalyzer ABC
│   ├── simplified_language.py
│   ├── dyslexia_friendly.py
│   ├── low_vision.py
│   ├── screen_reader.py
│   ├── motor_keyboard.py
│   ├── deaf_hoh.py
│   ├── color_blindness.py
│   └── cognitive_load.py
├── utils/
│   ├── fetcher.py          # HTTP fetch + rich snippet extraction
│   └── scoring.py          # Score aggregation and sorting
├── templates/
│   └── index.html          # Single-page UI (CSS + JS inline)
└── vercel.json
```

---

## Limitations

- Analyzers parse **static HTML only** — JavaScript-rendered content (React, Vue, Angular) may be partially or fully missed
- Scores are **heuristic estimates**, not certified WCAG audits
- Google Custom Search API is limited to **100 free queries/day**
- Some sites block server-side fetching — these receive a neutral fallback score of 5.0

---

## Ethics Context

Built as a final project for an ethics course. The core argument: accessibility is a dimension of search result quality, not just a legal checkbox. Over 96% of popular websites have detectable WCAG failures ([WebAIM Million, 2024](https://webaim.org/projects/million/)). Disabled users receive the same ranked list as everyone else, even when many results are functionally inaccessible to them.

AccessiSearch makes the accessibility gap visible at the moment it matters — before a user clicks.
