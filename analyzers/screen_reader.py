from .base import BaseAnalyzer


class ScreenReaderAnalyzer(BaseAnalyzer):
    """Screen Reader Friendly: alt text, ARIA, headings, skip links, form labels, lang."""

    def analyze(self):
        score = 0.0
        details = []

        # Image alt text (up to 2.5)
        imgs = self.soup.find_all("img")
        if not imgs:
            score += 2.5
            details.append("No images found (full points)")
        else:
            with_alt = sum(
                1 for img in imgs
                if img.get("alt") is not None or img.get("role") == "presentation"
            )
            ratio = with_alt / len(imgs)
            pts = round(ratio * 2.5, 1)
            score += pts
            details.append(f"Alt text: {with_alt}/{len(imgs)} images ({pts}/2.5)")

        # ARIA landmarks and labels (up to 2.0)
        aria_count = len(self.soup.select(
            "[role], [aria-label], [aria-labelledby], [aria-describedby]"
        ))
        landmarks = len(self.soup.select(
            "nav, main, header, footer, aside, "
            "section[aria-label], section[aria-labelledby]"
        ))
        total_aria = aria_count + landmarks
        if total_aria >= 11:
            score += 2.0
            details.append(f"Strong ARIA usage ({total_aria} elements)")
        elif total_aria >= 6:
            score += 1.5
            details.append(f"Good ARIA usage ({total_aria} elements)")
        elif total_aria >= 3:
            score += 1.0
            details.append(f"Basic ARIA usage ({total_aria} elements)")
        elif total_aria >= 1:
            score += 0.5
            details.append(f"Minimal ARIA usage ({total_aria} elements)")
        else:
            details.append("No ARIA landmarks or labels found")

        # Heading hierarchy (up to 2.0)
        headings = self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        has_h1 = bool(self.soup.find("h1"))
        levels = sorted(set(int(h.name[1]) for h in headings))
        no_skip = all(
            levels[i + 1] - levels[i] <= 1 for i in range(len(levels) - 1)
        ) if len(levels) > 1 else True

        if has_h1:
            score += 0.5
            details.append("H1 present")
        if no_skip and len(levels) > 1:
            score += 1.0
            details.append("No heading levels skipped")
        if len(levels) >= 3:
            score += 0.5
            details.append(f"{len(levels)} heading levels used")

        # Skip links (up to 1.5)
        if self.has_skip_link():
            score += 1.5
            details.append("Skip navigation link found")
        else:
            details.append("No skip navigation link detected")

        # Form labels (up to 1.0)
        inputs = self.soup.select("input:not([type='hidden']), select, textarea")
        if not inputs:
            score += 1.0
            details.append("No form inputs (full points)")
        else:
            labeled = 0
            for inp in inputs:
                if inp.get("aria-label") or inp.get("aria-labelledby"):
                    labeled += 1
                    continue
                inp_id = inp.get("id")
                if inp_id and self.soup.find("label", attrs={"for": inp_id}):
                    labeled += 1
                    continue
                if inp.find_parent("label"):
                    labeled += 1
                    continue
            ratio = labeled / len(inputs)
            pts = round(ratio * 1.0, 1)
            score += pts
            details.append(f"Labeled inputs: {labeled}/{len(inputs)} ({pts}/1.0)")

        # Language attribute (up to 1.0)
        html_tag = self.soup.find("html")
        if html_tag and html_tag.get("lang"):
            score += 1.0
            details.append(f"Language declared: {html_tag.get('lang')}")
        else:
            details.append("No lang attribute on <html>")

        return {"score": self.clamp_score(score), "details": details}
