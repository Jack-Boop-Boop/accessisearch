import re
from .base import BaseAnalyzer


class MotorKeyboardAnalyzer(BaseAnalyzer):
    """Motor / Keyboard-Only: keyboard nav, mouse-only handlers, focus, zoom, drag."""

    def analyze(self):
        score = 0.0
        details = []

        # Keyboard navigability (up to 3.0)
        mouse_only = len(self.soup.select("[onmouseover], [onmousedown]"))
        div_clicks = len(self.soup.select("div[onclick], span[onclick]"))
        pos_tabindex = sum(
            1 for el in self.soup.select("[tabindex]")
            if el.get("tabindex", "").lstrip("-").isdigit()
            and int(el.get("tabindex", "0")) > 0
        )

        kb_score = 3.0
        if div_clicks > 0:
            kb_score -= min(1.5, div_clicks * 0.3)
            details.append(f"{div_clicks} non-semantic click handlers")
        if mouse_only > 0:
            kb_score -= min(1.0, mouse_only * 0.2)
            details.append(f"{mouse_only} mouse-only handlers")
        if pos_tabindex > 0:
            kb_score -= min(0.5, pos_tabindex * 0.1)
            details.append(f"{pos_tabindex} positive tabindex values")
        if kb_score >= 2.5:
            details.append("Good keyboard navigability indicators")
        score += max(0, kb_score)

        # Skip navigation (up to 2.0)
        if self.has_skip_link():
            score += 2.0
            details.append("Skip navigation present")
        else:
            details.append("No skip navigation")

        # Focus indicators (up to 2.0)
        styles_text = self.get_all_styles_text()
        has_focus_style = bool(
            re.search(r"(:focus-visible|:focus)\s*\{", styles_text)
        )
        has_outline_none = bool(
            re.search(r"outline\s*:\s*(none|0)", styles_text)
        )

        if has_focus_style:
            score += 2.0
            details.append("Custom focus styles defined")
        else:
            score += 0.5
            details.append("Using browser default focus (no custom styles)")
        if has_outline_none:
            score -= 1.0
            details.append("Warning: outline:none detected")

        # Zoom / target size (up to 1.5)
        meta = self.soup.find("meta", attrs={"name": "viewport"})
        viewport = meta.get("content", "") if meta else ""
        if "user-scalable=no" in viewport or "maximum-scale=1" in viewport:
            details.append("Warning: zoom disabled via viewport meta")
        else:
            score += 1.5
            details.append("Zoom not restricted")

        # Drag-only (up to 1.5)
        drag_handlers = len(
            self.soup.select("[ondrag], [ondragstart], [ondrop]")
        )
        if drag_handlers == 0:
            score += 1.5
            details.append("No drag-only interactions")
        else:
            details.append(f"{drag_handlers} drag handlers found")

        return {"score": self.clamp_score(score), "details": details}
