import re
from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """Base class for accessibility category analyzers."""

    def __init__(self, soup, raw_html, url):
        self.soup = soup
        self.raw_html = raw_html
        self.url = url

    @abstractmethod
    def analyze(self):
        """Return {"score": float (0-10), "details": [str, ...]}"""
        pass

    def count_elements(self, selector):
        return len(self.soup.select(selector))

    def get_all_text(self, tags=("p", "li", "td", "dd")):
        elements = self.soup.find_all(tags)
        return " ".join(el.get_text(strip=True) for el in elements)

    def get_all_styles_text(self):
        styles = self.soup.find_all("style")
        return " ".join(s.get_text() for s in styles)

    def has_skip_link(self):
        body = self.soup.find("body")
        if not body:
            return False
        for child in list(body.children)[:20]:
            if hasattr(child, "find_all"):
                links = child.find_all("a") if child.name != "a" else [child]
                for a in links:
                    href = a.get("href", "")
                    text = a.get_text(strip=True).lower()
                    if href.startswith("#") and any(
                        kw in text for kw in ("skip", "main", "content", "navigation")
                    ):
                        return True
        return False

    def clamp_score(self, score):
        return round(min(10.0, max(0.0, score)), 1)
