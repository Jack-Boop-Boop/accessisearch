import re
from .base import BaseAnalyzer


class LowVisionAnalyzer(BaseAnalyzer):
    """Low Vision: contrast, relative font units, zoom, high-contrast support, sizing."""

    def analyze(self):
        score = 0.0
        details = []
        styles_text = self.get_all_styles_text()

        # Color contrast indicators (up to 2.5)
        has_contrast_vars = any(
            kw in styles_text
            for kw in ("--color-", "contrast", "prefers-contrast")
        )
        inline_colors = self.soup.select("[style*='color']")
        if has_contrast_vars:
            score += 2.5
            details.append("CSS variables or contrast-aware styles detected")
        elif len(inline_colors) < 5:
            score += 1.5
            details.append("Minimal inline color styling (likely uses stylesheet)")
        else:
            score += 0.5
            details.append(
                f"{len(inline_colors)} inline color styles (harder to ensure contrast)"
            )

        # Relative text units (up to 2.5)
        px_font_sizes = re.findall(r"font-size\s*:\s*\d+px", styles_text)
        rem_em_sizes = re.findall(
            r"font-size\s*:\s*[\d.]+(?:rem|em|%)", styles_text
        )
        if len(rem_em_sizes) > 0 and len(px_font_sizes) == 0:
            score += 2.5
            details.append("All font sizes use relative units (rem/em/%)")
        elif len(rem_em_sizes) >= len(px_font_sizes):
            score += 1.5
            details.append("Mix of relative and fixed font sizes")
        elif len(px_font_sizes) > 0:
            score += 0.5
            details.append(f"{len(px_font_sizes)} fixed px font sizes found")
        else:
            score += 1.5
            details.append("No explicit font sizes (browser defaults)")

        # Viewport zoom (up to 2.0)
        meta = self.soup.find("meta", attrs={"name": "viewport"})
        viewport = meta.get("content", "") if meta else ""
        if "user-scalable=no" in viewport or "maximum-scale=1" in viewport:
            details.append("Warning: zoom disabled -- major low vision barrier")
        else:
            score += 2.0
            details.append("Zoom not restricted by viewport meta")

        # High-contrast support (up to 1.5)
        if "prefers-contrast" in styles_text or "high-contrast" in styles_text:
            score += 1.5
            details.append("High contrast mode / prefers-contrast detected")
        elif "prefers-color-scheme" in styles_text:
            score += 0.8
            details.append("Dark mode support detected (partial contrast help)")
        else:
            details.append("No contrast/dark mode media queries found")

        # Large text / target sizing hints (up to 1.5)
        large_text_indicators = 0
        if re.search(
            r"font-size\s*:\s*(?:1\.[2-9]|[2-9]\.?\d*)(?:rem|em)", styles_text
        ):
            large_text_indicators += 1
        if "min-height: 44px" in styles_text or "min-height:44px" in styles_text:
            large_text_indicators += 1
        if "min-width: 44px" in styles_text or "min-width:44px" in styles_text:
            large_text_indicators += 1

        if large_text_indicators >= 2:
            score += 1.5
            details.append("Large text and touch targets detected")
        elif large_text_indicators == 1:
            score += 0.8
            details.append("Some large sizing indicators")
        else:
            score += 0.3
            details.append("No explicit large sizing found")

        return {"score": self.clamp_score(score), "details": details}
