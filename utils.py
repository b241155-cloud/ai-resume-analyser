"""
utils.py
Utility helpers for the AI Resume Analyser app.
"""


def score_color(score: int) -> str:
    """Return a hex color based on score value for visual feedback."""
    if score >= 75:
        return "#2ecc71"   # green
    elif score >= 50:
        return "#f39c12"   # orange
    else:
        return "#e74c3c"   # red


def score_label(score: int) -> str:
    """Return a human-readable label for the score."""
    if score >= 80:
        return "Excellent ✅"
    elif score >= 60:
        return "Good 👍"
    elif score >= 40:
        return "Average ⚠️"
    else:
        return "Needs Work ❌"


def build_radar_data(sections: dict) -> tuple:
    """Convert section scores dict to lists suitable for a radar/polar chart."""
    labels = list(sections.keys())
    values = list(sections.values())
    # Prettify labels
    pretty_labels = [label.replace("_", " ").title() for label in labels]
    return pretty_labels, values

