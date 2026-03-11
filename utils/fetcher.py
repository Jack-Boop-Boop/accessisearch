import requests

FETCH_TIMEOUT = 8
MAX_CONTENT_LENGTH = 2_000_000


def fetch_page_html(url):
    """Fetch a URL's HTML content server-side. Returns HTML string or None."""
    try:
        resp = requests.get(
            url,
            timeout=FETCH_TIMEOUT,
            headers={
                "User-Agent": "AccessiSearch/1.0 (accessibility analyzer)",
                "Accept": "text/html",
            },
            allow_redirects=True,
        )
        if resp.status_code != 200:
            return None

        content_type = resp.headers.get("content-type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return None

        html = resp.text
        if len(html) > MAX_CONTENT_LENGTH:
            html = html[:MAX_CONTENT_LENGTH]

        return html
    except Exception:
        return None
