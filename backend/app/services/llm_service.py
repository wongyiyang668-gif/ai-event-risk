"""
LLM-based risk summarization service.
Uses OpenAI API for generating risk summaries and recommendations.
Falls back to deterministic output if API key is missing.
"""
import os
from openai import OpenAI


SYSTEM_PROMPT = """You are an enterprise risk analyst.
Given event details and risk scores, write a short professional summary and recommendation.
Be concise and objective. Use formal business language.

Output format:
SUMMARY: [2-3 sentences summarizing the risk]
RECOMMENDATION: [1 sentence with actionable recommendation]"""


def generate_risk_summary(event_text: str, scores: dict, semantics: dict) -> dict:
    """
    Generate an LLM-based risk summary and recommendation.
    
    Args:
        event_text: The event content
        scores: Score matrix dict
        semantics: Risk semantics dict with category_scores and matched_keywords
        
    Returns:
        dict with 'summary' and 'recommendation' keys
    """
    # Build the prompt
    category_scores = semantics.get("category_scores", {})
    matched_keywords = semantics.get("matched_keywords", {})
    
    user_prompt = f"""
Event: {event_text}

Risk Scores:
- Signal Strength: {scores.get('signal_strength', 0):.3f}
- Historical Rarity: {scores.get('historical_rarity', 0):.3f}
- Trend Acceleration: {scores.get('trend_acceleration', 0):.3f}
- Cross-Source Presence: {scores.get('cross_source_presence', 0):.3f}
- Uncertainty: {scores.get('uncertainty', 0):.3f}

Risk Categories:
- Operational Risk: {category_scores.get('operational_risk', 0)*100:.1f}%
- Compliance Risk: {category_scores.get('compliance_risk', 0)*100:.1f}%
- Reputational Risk: {category_scores.get('reputational_risk', 0)*100:.1f}%
- Financial Risk: {category_scores.get('financial_risk', 0)*100:.1f}%

Matched Keywords: {', '.join([kw for kws in matched_keywords.values() for kw in kws]) or 'None'}

Provide a professional risk summary and recommendation.
"""

    # Try OpenAI API
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            
            output = response.choices[0].message.content
            return _parse_llm_output(output)
        
        except Exception as e:
            # Fall back to deterministic
            return _generate_deterministic_summary(event_text, scores, semantics)
    
    # No API key - use deterministic fallback
    return _generate_deterministic_summary(event_text, scores, semantics)


def _parse_llm_output(output: str) -> dict:
    """Parse LLM output into summary and recommendation."""
    summary = ""
    recommendation = ""
    
    lines = output.strip().split("\n")
    for line in lines:
        if line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "").strip()
        elif line.startswith("RECOMMENDATION:"):
            recommendation = line.replace("RECOMMENDATION:", "").strip()
    
    # If parsing failed, use the whole output as summary
    if not summary:
        summary = output.strip()
    if not recommendation:
        recommendation = "Review the event details and take appropriate action."
    
    return {"summary": summary, "recommendation": recommendation}


def _generate_deterministic_summary(event_text: str, scores: dict, semantics: dict) -> dict:
    """
    Generate a deterministic summary when LLM is not available.
    """
    category_scores = semantics.get("category_scores", {})
    matched_keywords = semantics.get("matched_keywords", {})
    
    # Find highest risk category
    if category_scores:
        max_category = max(category_scores, key=category_scores.get)
        max_value = category_scores[max_category]
    else:
        max_category = "unknown"
        max_value = 0
    
    # Collect matched keywords
    all_keywords = [kw for kws in matched_keywords.values() for kw in kws]
    
    # Determine severity
    if max_value >= 0.6:
        severity = "high"
        urgency = "requires immediate attention"
    elif max_value >= 0.3:
        severity = "moderate"
        urgency = "should be reviewed within 24 hours"
    else:
        severity = "low"
        urgency = "can be monitored passively"
    
    # Build summary
    category_name = max_category.replace("_", " ").title()
    
    if all_keywords:
        summary = f"This event exhibits {severity} {category_name.lower()} indicators based on detected keywords: {', '.join(all_keywords)}. The overall risk confidence is {max_value*100:.0f}%."
    else:
        summary = f"This event shows {severity} risk levels across all categories. No specific risk keywords were detected in the content."
    
    # Build recommendation
    if max_value >= 0.6:
        recommendation = f"Escalate immediately to the incident response team for {category_name.lower()} review."
    elif max_value >= 0.3:
        recommendation = f"Schedule a review within 24 hours to assess {category_name.lower()} implications."
    else:
        recommendation = "Log for tracking purposes; no immediate action required."
    
    return {"summary": summary, "recommendation": recommendation}
