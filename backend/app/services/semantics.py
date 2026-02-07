import os
import yaml

# Load anchors from YAML file
_anchors_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "risk_anchors.yaml")
with open(_anchors_path, "r") as f:
    RISK_ANCHORS = yaml.safe_load(f)


def calculate_semantics(text: str) -> dict:
    """
    Calculate semantic risk scores based on keyword anchors.
    Returns a dict with:
      - category_scores: scores normalized to 0-1 for each category
      - matched_keywords: dict of category -> list of matched keywords
    """
    text_lower = text.lower()
    category_scores = {}
    matched_keywords = {}

    for category, keywords in RISK_ANCHORS.items():
        matches = [kw for kw in keywords if kw in text_lower]
        total = len(keywords)
        score = len(matches) / total if total > 0 else 0.0
        category_scores[category] = round(score, 4)
        matched_keywords[category] = matches

    return {
        "category_scores": category_scores,
        "matched_keywords": matched_keywords
    }
