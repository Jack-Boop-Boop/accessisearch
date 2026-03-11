import re
from .base import BaseAnalyzer


class ColorBlindnessAnalyzer(BaseAnalyzer):
    """Color Blindness: link underlines, contrast, error indicators, labels, media queries."""

    def analyze(self):
        score = 0.0
        details = []
        styles_text = self.get_all_styles_text()

        # Link distinguishability (up to 2.5)
        has_link_underline = bool(
            re.search(
                r"a\s*[^{}]*\{[^}]*text-decoration\s*:\s*underline", styles_text
            )
        )
        removes_underline = bool(
            re.search(
                r"a\s*[^{}]*\{[^}]*text-decoration\s*:\s*none", styles_text
            )
        )
        if has_link_underline or not removes_underline:
            score += 2.5
            details.append("Links appear to use underline (not color-only)")
        else:
            score += 0.5
            details.append(
                "Links may rely on color alone (text-decoration: none found)"
            )

        # Color contrast CSS patterns (up to 2.5)
        has_high_contrast_vars = any(
            kw in styles_text.lower()
            for kw in ("--color-", "prefers-contrast", "forced-colors")
        )
        if has_high_contrast_vars:
            score += 2.5
            details.append("CSS custom properties or contrast media queries found")
        elif "color:" in styles_text and "background" in styles_text:
            score += 1.5
            details.append("Explicit color and background declarations present")
        else:
            score += 1.0
            details.append("Minimal color declarations (relies on browser defaults)")

        # Form error patterns (up to 2.0)
        error_indicators = len(
            self.soup.select(
                "[aria-invalid], [aria-errormessage], [role='alert'], .error, .invalid"
            )
        )
        if error_indicators > 0:
            score += 2.0
            details.append(
                f"Non-color error indicators found ({error_indicators} elements)"
            )
        else:
            forms = self.soup.find_all("form")
            if not forms:
                score += 2.0
                details.append("No forms (no color-only error risk)")
            else:
                score += 1.0
                details.append(
                    "Forms present but no non-color error indicators detected"
                )

        # Icon/symbol text labels (up to 1.5)
        icons_with_text = len(self.soup.select("[aria-label], [title]"))
        if icons_with_text >= 5:
            score += 1.5
            details.append(
                f"Good text labels on interactive elements ({icons_with_text})"
            )
        elif icons_with_text >= 1:
            score += 0.8
            details.append(f"Some text labels on elements ({icons_with_text})")
        else:
            score += 0.3
            details.append("Few explicit text labels found")

        # Accessibility media queries (up to 1.5)
        if (
            "prefers-color-scheme" in styles_text
            or "prefers-contrast" in styles_text
        ):
            score += 1.5
            details.append("Accessibility media queries detected")
        else:
            score += 0.3
            details.append(
                "No prefers-color-scheme or prefers-contrast media queries"
            )

        return {"score": self.clamp_score(score), "details": details}
