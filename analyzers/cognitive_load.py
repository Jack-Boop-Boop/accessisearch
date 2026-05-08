from .base import BaseAnalyzer


class CognitiveLoadAnalyzer(BaseAnalyzer):
    """Cognitive Load: navigation, headings, semantic layout, auto-refresh, modals, carousels."""

    def analyze(self):
        score = 0.0
        details = []

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

        # Semantic layout (up to 2.0)
        has_header = self.soup.find("header") is not None
        has_main = self.soup.find("main") is not None
        has_footer = self.soup.find("footer") is not None
        layout_count = sum([has_header, has_main, has_footer])
        if layout_count == 3:
            score += 2.0
            details.append("Full semantic layout (header, main, footer)")
        elif layout_count == 2:
            score += 1.2
            details.append(f"{layout_count}/3 semantic layout elements")
        elif layout_count == 1:
            score += 0.5
            details.append(f"{layout_count}/3 semantic layout elements")
        else:
            details.append("No semantic layout elements")

        # No auto-refresh (up to 1.0)
        refresh = self.soup.find("meta", attrs={"http-equiv": "refresh"})
        if not refresh:
            score += 1.0
            details.append("No auto-refresh detected")
        else:
            details.append("Auto-refresh meta tag found (disorienting)")

        # No modal/popup overlays (up to 1.5)
        modal_roles = self.soup.find_all(attrs={"role": "dialog"})
        modal_classes = [
            el for el in self.soup.find_all(["div", "section", "aside"])
            if any(
                k in " ".join(el.get("class") or []).lower()
                for k in ["modal", "popup", "overlay", "lightbox", "cookie-banner"]
            )
        ]
        popup_count = len(modal_roles) + len(modal_classes)
        if popup_count == 0:
            score += 1.5
            details.append("No modal overlays or popups detected")
        elif popup_count <= 1:
            score += 0.75
            details.append(f"{popup_count} modal/popup element detected")
        else:
            details.append(f"{popup_count} modal/popup elements detected (high cognitive load)")

        # No carousels or auto-playing sliders (up to 1.0)
        carousel_els = [
            el for el in self.soup.find_all(True)
            if any(
                k in " ".join(el.get("class") or []).lower()
                for k in ["carousel", "slider", "slideshow", "swiper", "slick"]
            )
        ]
        if not carousel_els:
            score += 1.0
            details.append("No carousels or sliders detected")
        else:
            details.append(f"{len(carousel_els)} carousel/slider element(s) found")

        return {"score": self.clamp_score(score), "details": details}
