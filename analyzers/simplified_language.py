import re
from .base import BaseAnalyzer


class SimplifiedLanguageAnalyzer(BaseAnalyzer):
    """Simplified Language: readability, sentence length, word complexity, chunking."""

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
        avg_sentence_len = len(words) / max(len(sentences), 1)

        # Sentence length (up to 2.5)
        if avg_sentence_len < 15:
            score += 2.5
            details.append(
                f"Short sentences (avg {avg_sentence_len:.0f} words) -- easy to read"
            )
        elif avg_sentence_len < 20:
            score += 1.8
            details.append(
                f"Moderate sentence length (avg {avg_sentence_len:.0f} words)"
            )
        elif avg_sentence_len < 25:
            score += 1.0
            details.append(
                f"Long sentences (avg {avg_sentence_len:.0f} words)"
            )
        else:
            score += 0.3
            details.append(
                f"Very long sentences (avg {avg_sentence_len:.0f} words)"
            )

        # Complex word ratio (up to 3.0)
        complex_words = [w for w in words if len(w) > 6]
        complex_ratio = len(complex_words) / len(words)
        if complex_ratio < 0.15:
            score += 3.0
            details.append(
                f"Simple vocabulary ({complex_ratio:.0%} complex words)"
            )
        elif complex_ratio < 0.25:
            score += 2.0
            details.append(
                f"Moderate vocabulary ({complex_ratio:.0%} complex words)"
            )
        elif complex_ratio < 0.35:
            score += 1.0
            details.append(
                f"Complex vocabulary ({complex_ratio:.0%} complex words)"
            )
        else:
            details.append(
                f"Very complex vocabulary ({complex_ratio:.0%} complex words)"
            )

        # Average word length (up to 2.0)
        avg_word_len = sum(len(w) for w in words) / len(words)
        if avg_word_len < 5.0:
            score += 2.0
            details.append(f"Short average word length ({avg_word_len:.1f} chars)")
        elif avg_word_len < 6.0:
            score += 1.2
            details.append(f"Moderate word length ({avg_word_len:.1f} chars)")
        else:
            score += 0.5
            details.append(f"Long average word length ({avg_word_len:.1f} chars)")

        # Paragraph chunking (up to 1.5)
        paragraphs = self.soup.find_all("p")
        if len(paragraphs) >= 5:
            score += 1.5
            details.append(
                f"Well-chunked content ({len(paragraphs)} paragraphs)"
            )
        elif len(paragraphs) >= 2:
            score += 0.8
            details.append(
                f"Some content chunking ({len(paragraphs)} paragraphs)"
            )
        else:
            details.append("Minimal paragraph structure")

        # Lists for organization (up to 1.0)
        lists = self.soup.find_all(["ul", "ol"])
        if len(lists) >= 2:
            score += 1.0
            details.append(f"Lists used to organize information ({len(lists)} lists)")
        elif len(lists) >= 1:
            score += 0.5
            details.append("Some list usage")

        return {"score": self.clamp_score(score), "details": details}
