import re
from .base import BaseAnalyzer


class SimplifiedLanguageAnalyzer(BaseAnalyzer):
    """Simplified Language: Flesch-Kincaid readability, paragraph chunking, lists."""

    def analyze(self):
        score = 0.0
        details = []
        text = self.get_all_text()
        words = text.split()

        if len(words) < 20:
            return {
                "score": 5.0,
                "details": ["Insufficient text content to analyze readability"],
            }

        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if not sentences:
            return {"score": 5.0, "details": ["No complete sentences found"]}

        syllables = sum(self._count_syllables(w) for w in words)
        words_per_sentence = len(words) / len(sentences)
        syllables_per_word = syllables / len(words)

        # Flesch Reading Ease (up to 6.0)
        fk = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
        fk = max(0.0, min(100.0, fk))

        if fk >= 80:
            score += 6.0
            details.append(f"Very easy reading level (Flesch {fk:.0f}/100 — plain language)")
        elif fk >= 65:
            score += 4.5
            details.append(f"Standard reading level (Flesch {fk:.0f}/100)")
        elif fk >= 50:
            score += 3.0
            details.append(f"Moderately complex (Flesch {fk:.0f}/100)")
        elif fk >= 30:
            score += 1.5
            details.append(f"Difficult reading level (Flesch {fk:.0f}/100)")
        else:
            score += 0.5
            details.append(f"Very difficult reading level (Flesch {fk:.0f}/100)")

        # Paragraph chunking (up to 2.5)
        paragraphs = self.soup.find_all("p")
        if len(paragraphs) >= 5:
            score += 2.5
            details.append(f"Well-chunked content ({len(paragraphs)} paragraphs)")
        elif len(paragraphs) >= 2:
            score += 1.5
            details.append(f"Some content chunking ({len(paragraphs)} paragraphs)")
        elif len(paragraphs) >= 1:
            score += 0.5
            details.append("Minimal paragraph structure")
        else:
            details.append("No paragraph elements found")

        # Lists for organization (up to 1.5)
        lists = self.soup.find_all(["ul", "ol"])
        if len(lists) >= 2:
            score += 1.5
            details.append(f"Lists used to organize content ({len(lists)} lists)")
        elif len(lists) == 1:
            score += 0.8
            details.append("Some list usage")
        else:
            details.append("No list elements found")

        return {"score": self.clamp_score(score), "details": details}

    def _count_syllables(self, word):
        word = word.lower().strip(".,!?;:\"'()[]{}")
        if len(word) <= 3:
            return 1
        count = 0
        prev_vowel = False
        for ch in word:
            is_v = ch in "aeiouy"
            if is_v and not prev_vowel:
                count += 1
            prev_vowel = is_v
        if word.endswith("e"):
            count -= 1
        return max(1, count)
