import re
from .base import BaseAnalyzer


class DyslexiaFriendlyAnalyzer(BaseAnalyzer):
    """Dyslexia-Friendly: fonts, line spacing, paragraph length, alignment, zoom."""

    GOOD_FONTS = [
        "arial", "verdana", "tahoma", "trebuchet", "helvetica",
        "open sans", "opendyslexic", "comic sans", "lexie readable",
        "system-ui", "sans-serif", "segoe ui", "roboto", "inter",
    ]

    def analyze(self):
        score = 0.0
        details = []
        styles_text = self.get_all_styles_text()

        # Font families (up to 2.5)
        found_fonts = re.findall(r"font-family\s*:\s*([^;}{]+)", styles_text)
        if not found_fonts:
            score += 1.5
            details.append(
                "No custom fonts detected (browser defaults likely sans-serif)"
            )
        else:
            good_count = sum(
                1 for f in found_fonts
                if any(gf in f.lower() for gf in self.GOOD_FONTS)
            )
            if good_count > 0:
                score += 2.5
                details.append(
                    f"Dyslexia-friendly fonts detected ({good_count} declarations)"
                )
            else:
                score += 0.5
                details.append(
                    "Custom fonts used but none are known dyslexia-friendly"
                )

        # Line height (up to 2.5)
        line_heights = re.findall(r"line-height\s*:\s*([\d.]+)", styles_text)
        valid_lh = [float(lh) for lh in line_heights if float(lh) < 10]
        if valid_lh:
            max_lh = max(valid_lh)
            if max_lh >= 1.5:
                score += 2.5
                details.append(f"Good line spacing (line-height: {max_lh})")
            elif max_lh >= 1.3:
                score += 1.5
                details.append(f"Adequate line spacing (line-height: {max_lh})")
            else:
                score += 0.5
                details.append(f"Tight line spacing (line-height: {max_lh})")
        else:
            score += 1.5
            details.append("No line-height declared (browser default ~1.2)")

        # Paragraph length (up to 2.0)
        paragraphs = self.soup.find_all("p")
        if paragraphs:
            word_counts = [
                len(p.get_text(strip=True).split()) for p in paragraphs
            ]
            avg_para_words = sum(word_counts) / len(word_counts)
            if avg_para_words < 50:
                score += 2.0
                details.append(
                    f"Short paragraphs (avg {avg_para_words:.0f} words)"
                )
            elif avg_para_words < 100:
                score += 1.2
                details.append(
                    f"Moderate paragraph length (avg {avg_para_words:.0f} words)"
                )
            else:
                score += 0.3
                details.append(
                    f"Long paragraphs (avg {avg_para_words:.0f} words)"
                )
        else:
            score += 1.5
            details.append("No paragraph elements found")

        # Text alignment (up to 1.5)
        justified = (
            "text-align: justify" in styles_text
            or "text-align:justify" in styles_text
        )
        if not justified:
            score += 1.5
            details.append("No justified text (good for dyslexia)")
        else:
            score += 0.3
            details.append(
                "Justified text detected (can cause uneven spacing)"
            )

        # Zoom support (up to 1.5)
        meta = self.soup.find("meta", attrs={"name": "viewport"})
        viewport = meta.get("content", "") if meta else ""
        if "user-scalable=no" in viewport or "maximum-scale=1" in viewport:
            details.append("Warning: zoom disabled via viewport meta")
        else:
            score += 1.5
            details.append("Text resizable (zoom not restricted)")

        return {"score": self.clamp_score(score), "details": details}
