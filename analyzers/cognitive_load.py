import re
from .base import BaseAnalyzer


class CognitiveLoadAnalyzer(BaseAnalyzer):
    """Cognitive Load: readability, navigation, headings, semantic layout, auto-refresh."""

    def analyze(self):
        score = 0.0
        details = []

        # Readability (up to 3.0)
        text = self.get_all_text()
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

        if len(sentences) > 3:
            total_words = sum(len(s.split()) for s in sentences)
            avg_words = total_words / len(sentences)
            if avg_words < 15:
                score += 3.0
                details.append(
                    f"Good readability (avg {avg_words:.0f} words/sentence)"
                )
            elif avg_words < 20:
                score += 2.0
                details.append(
                    f"Moderate readability (avg {avg_words:.0f} words/sentence)"
                )
            elif avg_words < 25:
                score += 1.0
                details.append(
                    f"Complex language (avg {avg_words:.0f} words/sentence)"
                )
            else:
                details.append(
                    f"Very complex language (avg {avg_words:.0f} words/sentence)"
                )
        else:
            score += 2.0
            details.append("Limited text content to analyze")

        # Clear navigation (up to 2.5)
        nav = self.soup.find("nav")
        if nav:
            nav_list = nav.find(["ul", "ol"])
            if nav_list:
                score += 2.5
                details.append("Navigation with structured list")
            else:
                score += 1.5
                details.append("Navigation element present")
        else:
            score += 0.5
            details.append("No nav element found")

        # Heading structure (up to 2.0)
        headings = self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        if len(headings) >= 3:
            score += 2.0
            details.append(f"{len(headings)} headings provide clear structure")
        elif len(headings) >= 1:
            score += 1.0
            details.append(f"{len(headings)} heading(s) found")
        else:
            details.append("No headings found")

        # Semantic layout (up to 1.5)
        has_header = self.soup.find("header") is not None
        has_main = self.soup.find("main") is not None
        has_footer = self.soup.find("footer") is not None
        layout_count = sum([has_header, has_main, has_footer])
        if layout_count == 3:
            score += 1.5
            details.append("Full semantic layout (header, main, footer)")
        elif layout_count == 2:
            score += 1.0
            details.append(f"{layout_count}/3 semantic layout elements")
        elif layout_count == 1:
            score += 0.5
            details.append(f"{layout_count}/3 semantic layout elements")
        else:
            details.append("No semantic layout elements")

        # Auto-refresh (up to 1.0)
        refresh = self.soup.find("meta", attrs={"http-equiv": "refresh"})
        if not refresh:
            score += 1.0
            details.append("No auto-refresh detected")
        else:
            details.append("Auto-refresh meta tag found")

        return {"score": self.clamp_score(score), "details": details}
