from .base import BaseAnalyzer


class DeafHoHAnalyzer(BaseAnalyzer):
    """Deaf / Hard of Hearing: video captions, audio transcripts, autoplay, embedded media."""

    def analyze(self):
        score = 0.0
        details = []

        # Video captions (up to 3.5)
        videos = self.soup.find_all("video")
        if not videos:
            score += 3.5
            details.append("No video elements (full points)")
        else:
            captioned = sum(
                1 for v in videos
                if v.find("track", attrs={"kind": ["captions", "subtitles"]})
            )
            ratio = captioned / len(videos)
            score += round(ratio * 3.5, 1)
            details.append(f"Video captions: {captioned}/{len(videos)}")

        # Audio alternatives (up to 2.5)
        audios = self.soup.find_all("audio")
        if not audios:
            score += 2.5
            details.append("No audio elements (full points)")
        else:
            transcript_links = self.soup.select(
                "a[href*='transcript'], a[href*='Transcript']"
            )
            if transcript_links:
                score += 2.5
                details.append("Transcript links found")
            else:
                score += 0.5
                details.append("Audio without transcript links")

        # Autoplay (up to 2.0)
        autoplay = self.soup.select("video[autoplay], audio[autoplay]")
        if not autoplay:
            score += 2.0
            details.append("No autoplay media")
        else:
            muted = sum(1 for el in autoplay if el.get("muted") is not None)
            if muted == len(autoplay):
                score += 1.0
                details.append("Autoplay media is muted")
            else:
                details.append(
                    f"Autoplay media without mute ({len(autoplay)} elements)"
                )

        # Embedded media iframes (up to 2.0)
        iframes = self.soup.find_all("iframe")
        media_iframes = [
            f for f in iframes
            if any(
                p in (f.get("src", "").lower())
                for p in ("youtube", "vimeo", "dailymotion")
            )
        ]
        if not media_iframes:
            score += 2.0
            details.append("No embedded video platforms")
        else:
            with_captions = sum(
                1 for f in media_iframes
                if "cc_load_policy=1" in f.get("src", "")
                or "captions" in f.get("src", "")
            )
            ratio = with_captions / len(media_iframes) if media_iframes else 0
            score += round(ratio * 2.0, 1)
            details.append(
                f"Embedded video caption params: {with_captions}/{len(media_iframes)}"
            )

        return {"score": self.clamp_score(score), "details": details}
