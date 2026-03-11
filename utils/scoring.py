CATEGORY_IDS = [
    "simplified_language", "dyslexia_friendly", "low_vision",
    "screen_reader", "motor_keyboard", "deaf_hoh",
    "color_blindness", "cognitive_load",
]

CATEGORY_DISPLAY_NAMES = {
    "simplified_language": "Simplified Language",
    "dyslexia_friendly": "Dyslexia-Friendly",
    "low_vision": "Low Vision",
    "screen_reader": "Screen Reader Friendly",
    "motor_keyboard": "Motor / Keyboard-Only",
    "deaf_hoh": "Deaf / Hard of Hearing",
    "color_blindness": "Color Blindness",
    "cognitive_load": "Cognitive Load",
}


def compute_overall_score(category_scores, active_filters):
    """Weighted average of selected categories."""
    if "all" in active_filters:
        categories = CATEGORY_IDS
    else:
        categories = [c for c in active_filters if c in CATEGORY_IDS]

    if not categories:
        return 5.0

    total = sum(
        category_scores.get(cat, {}).get("score", 5.0)
        for cat in categories
    )
    return round(total / len(categories), 1)


def sort_results_by_score(results, active_filters):
    """Sort results descending by overall score."""
    for r in results:
        if r.get("scores"):
            r["overall_score"] = compute_overall_score(r["scores"], active_filters)
        else:
            r["overall_score"] = 0.0
    return sorted(results, key=lambda r: r["overall_score"], reverse=True)
