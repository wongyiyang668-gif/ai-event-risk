"""
LangChain tools for risk analysis.
"""
from langchain_core.tools import tool
from app.services import scoring, semantics


@tool
def score_event(event_text: str) -> dict:
    """
    Calculate risk scores for an event. 
    Returns a score matrix with signal_strength, historical_rarity, 
    trend_acceleration, cross_source_presence, and uncertainty.
    """
    score_matrix = scoring.calculate_scores(event_text)
    return {
        "signal_strength": score_matrix.signal_strength,
        "historical_rarity": score_matrix.historical_rarity,
        "trend_acceleration": score_matrix.trend_acceleration,
        "cross_source_presence": score_matrix.cross_source_presence,
        "uncertainty": score_matrix.uncertainty,
    }


@tool
def classify_risk(event_text: str) -> dict:
    """
    Classify event into risk categories.
    Returns semantic risk scores for operational, compliance, 
    reputational, and financial risks, plus matched keywords.
    """
    result = semantics.calculate_semantics(event_text)
    return {
        "category_scores": result["category_scores"],
        "matched_keywords": result["matched_keywords"],
    }


@tool
def find_similar_events(event_text: str) -> list:
    """
    Find similar events in the database.
    Returns top 3 similar events (mocked for now).
    """
    # Mocked implementation - in production would use embeddings/similarity search
    return [
        {"id": "mock-001", "content": "Similar event about system issues", "similarity": 0.85},
        {"id": "mock-002", "content": "Related incident from last week", "similarity": 0.72},
        {"id": "mock-003", "content": "Comparable alert detected", "similarity": 0.68},
    ]


@tool
def generate_recommendation(event_text: str, operational_risk: float, compliance_risk: float, 
                            reputational_risk: float, financial_risk: float) -> str:
    """
    Generate a decision recommendation based on event and risk scores.
    Returns a short actionable recommendation.
    """
    max_risk = max(operational_risk, compliance_risk, reputational_risk, financial_risk)
    
    if max_risk >= 0.6:
        urgency = "URGENT"
        action = "Immediate escalation required. Notify incident response team."
    elif max_risk >= 0.3:
        urgency = "MODERATE"
        action = "Schedule review within 24 hours. Monitor for escalation."
    else:
        urgency = "LOW"
        action = "Log for tracking. No immediate action needed."
    
    # Identify primary risk type
    risks = {
        "operational": operational_risk,
        "compliance": compliance_risk,
        "reputational": reputational_risk,
        "financial": financial_risk,
    }
    primary_risk = max(risks, key=risks.get)
    
    return f"[{urgency}] Primary risk: {primary_risk}. Recommended action: {action}"


# Export all tools
RISK_TOOLS = [score_event, classify_risk, find_similar_events, generate_recommendation]
