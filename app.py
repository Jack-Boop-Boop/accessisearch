import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, render_template, request, jsonify, send_from_directory

from analyzers import analyze_page
from utils.fetcher import fetch_page_html
from utils.scoring import compute_overall_score, sort_results_by_score, CATEGORY_IDS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder="public", static_url_path="/static")


# --- Page Routes ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, "public"), filename)


# --- API Routes ---

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    filters_param = request.args.get("filters", "all")
    active_filters = (
        set(filters_param.split(",")) if filters_param != "all" else {"all"}
    )

    # Step 1: Google Custom Search
    search_results = google_custom_search(query)
    if not search_results:
        return jsonify({"results": [], "query": query, "total": 0})

    # Step 2: Fetch and analyze pages in parallel
    analyzed = analyze_results_parallel(search_results)

    # Step 3: Sort by score
    sorted_results = sort_results_by_score(analyzed, active_filters)

    return jsonify({
        "results": sorted_results,
        "query": query,
        "total": len(sorted_results),
    })


def google_custom_search(query, num=10):
    """Call Google Custom Search JSON API."""
    import requests as req

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    cx = os.environ.get("GOOGLE_CX", "")
    if not api_key or not cx:
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": num}

    try:
        resp = req.get(url, params=params, timeout=10)
        if resp.status_code in (403, 429):
            return []
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        return [
            {
                "title": it.get("title", "Untitled"),
                "link": it.get("link", ""),
                "display_link": it.get("displayLink", it.get("link", "")),
                "snippet": it.get("snippet", ""),
            }
            for it in items
        ]
    except Exception:
        return []


def analyze_results_parallel(search_results, max_workers=3):
    """Fetch and analyze pages concurrently."""

    def process_one(item):
        html = fetch_page_html(item["link"])
        if html:
            item["scores"] = analyze_page(html, item["link"])
            item["analysis_status"] = "complete"
        else:
            item["scores"] = get_neutral_scores()
            item["analysis_status"] = "failed"
        return item

    analyzed = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_one, item): item
            for item in search_results
        }
        for future in as_completed(futures):
            try:
                analyzed.append(future.result())
            except Exception:
                original = futures[future]
                original["scores"] = get_neutral_scores()
                original["analysis_status"] = "error"
                analyzed.append(original)
    return analyzed


def get_neutral_scores():
    return {
        cat: {"score": 5.0, "details": ["Unable to analyze page"]}
        for cat in CATEGORY_IDS
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    app.run(debug=True, port=3457)
