from pydantic import BaseModel


class Explainability(BaseModel):
    matched_keywords: dict[str, list[str]]
    reasoning: str


def generate_reasoning(matched_keywords: dict[str, list[str]], category_scores: dict[str, float]) -> str:
    """
    Generate a human-readable reasoning text based on matched keywords.
    """
    explanations = []
    
    risk_labels = {
        "operational_risk": "Operational risk",
        "compliance_risk": "Compliance risk",
        "reputational_risk": "Reputational risk",
        "financial_risk": "Financial risk"
    }
    
    for category, matches in matched_keywords.items():
        if matches:
            score = category_scores.get(category, 0.0)
            level = "high" if score >= 0.5 else "moderate" if score >= 0.25 else "low"
            label = risk_labels.get(category, category)
            explanations.append(f"{label} is {level} because keywords {matches} were detected.")
    
    if not explanations:
        return "No significant risk indicators detected."
    
    return " ".join(explanations)
