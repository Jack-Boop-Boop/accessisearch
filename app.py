import json as json_mod
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, Response, jsonify, render_template, request, stream_with_context

from analyzers import analyze_page
from utils.fetcher import extract_rich_snippet, fetch_page_html
from utils.scoring import CATEGORY_IDS, compute_overall_score, sort_results_by_score

app = Flask(__name__, static_folder="public", static_url_path="/public")


# --- Page Routes ---

@app.route("/")
def index():
    return render_template("index.html")


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

    try:
        search_results = google_custom_search(query)
    except ValueError as e:
        return jsonify({"error": str(e)}), 503

    if not search_results:
        return jsonify({"results": [], "query": query, "total": 0})

    analyzed = analyze_results_parallel(search_results)
    sorted_results = sort_results_by_score(analyzed, active_filters)

    return jsonify({
        "results": sorted_results,
        "query": query,
        "total": len(sorted_results),
    })


@app.route("/api/search/stream")
def api_search_stream():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    filters_param = request.args.get("filters", "all")
    active_filters = (
        set(filters_param.split(",")) if filters_param != "all" else {"all"}
    )

    def generate():
        try:
            search_results = google_custom_search(query)
        except ValueError as e:
            yield f"data: {json_mod.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return

        if not search_results:
            yield f"data: {json_mod.dumps({'type': 'done', 'total': 0, 'query': query})}\n\n"
            return

        completed = []

        def process_one(item):
            html = fetch_page_html(item["link"])
            if html:
                item["scores"] = analyze_page(html, item["link"])
                item["analysis_status"] = "complete"
                rich = extract_rich_snippet(html)
                if rich:
                    item["rich_snippet"] = rich
            else:
                item["scores"] = get_neutral_scores()
                item["analysis_status"] = "failed"
            item["overall_score"] = compute_overall_score(item["scores"], active_filters)
            return item

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_one, item): item for item in search_results}
            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception:
                    original = futures[future]
                    original["scores"] = get_neutral_scores()
                    original["analysis_status"] = "error"
                    original["overall_score"] = 0.0
                    result = original
                completed.append(result)
                yield f"data: {json_mod.dumps({'type': 'result', 'result': result})}\n\n"

        yield f"data: {json_mod.dumps({'type': 'done', 'total': len(completed), 'query': query})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def google_custom_search(query, num=5):
    """Call Brave Search API."""
    import requests as req
    from urllib.parse import urlparse

    api_key = os.environ.get("BRAVE_API_KEY", "")
    if not api_key:
        raise ValueError(
            "Brave API key not configured. Set BRAVE_API_KEY environment variable."
        )

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {"q": query, "count": num, "result_filter": "web"}

    try:
        resp = req.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 401:
            raise ValueError("Brave API key rejected (401). Check BRAVE_API_KEY.")
        if resp.status_code == 429:
            raise ValueError("Brave API quota exceeded (429). Try again later.")
        resp.raise_for_status()
        data = resp.json()
        results = data.get("web", {}).get("results", [])
        return [
            {
                "title": it.get("title", "Untitled"),
                "link": it.get("url", ""),
                "display_link": urlparse(it.get("url", "")).netloc,
                "snippet": it.get("description", ""),
            }
            for it in results
        ]
    except ValueError:
        raise
    except Exception:
        return []


def analyze_results_parallel(search_results):
    """Fetch and analyze pages concurrently."""

    def process_one(item):
        html = fetch_page_html(item["link"])
        if html:
            item["scores"] = analyze_page(html, item["link"])
            item["analysis_status"] = "complete"
            rich = extract_rich_snippet(html)
            if rich:
                item["rich_snippet"] = rich
        else:
            item["scores"] = get_neutral_scores()
            item["analysis_status"] = "failed"
        return item

    analyzed = []
    with ThreadPoolExecutor(max_workers=5) as executor:
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
