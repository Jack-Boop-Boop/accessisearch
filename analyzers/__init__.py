from bs4 import BeautifulSoup
from .simplified_language import SimplifiedLanguageAnalyzer
from .dyslexia_friendly import DyslexiaFriendlyAnalyzer
from .low_vision import LowVisionAnalyzer
from .screen_reader import ScreenReaderAnalyzer
from .motor_keyboard import MotorKeyboardAnalyzer
from .deaf_hoh import DeafHoHAnalyzer
from .color_blindness import ColorBlindnessAnalyzer
from .cognitive_load import CognitiveLoadAnalyzer

ANALYZER_CLASSES = {
    "simplified_language": SimplifiedLanguageAnalyzer,
    "dyslexia_friendly": DyslexiaFriendlyAnalyzer,
    "low_vision": LowVisionAnalyzer,
    "screen_reader": ScreenReaderAnalyzer,
    "motor_keyboard": MotorKeyboardAnalyzer,
    "deaf_hoh": DeafHoHAnalyzer,
    "color_blindness": ColorBlindnessAnalyzer,
    "cognitive_load": CognitiveLoadAnalyzer,
}


def analyze_page(html, url=""):
    """Run all 8 analyzers on an HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for category_id, cls in ANALYZER_CLASSES.items():
        analyzer = cls(soup, html, url)
        results[category_id] = analyzer.analyze()
    return results
