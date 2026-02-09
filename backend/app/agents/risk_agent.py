"""
LangChain-based Risk Analysis Agent.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from app.agents.tools import RISK_TOOLS, score_event, classify_risk, find_similar_events, generate_recommendation


SYSTEM_PROMPT = """You are a Risk Analysis Agent for an enterprise AI system.
Your job is to analyze events and provide comprehensive risk assessments.

You have access to the following tools:
1. score_event - Calculate risk scores for an event
2. classify_risk - Classify event into risk categories  
3. find_similar_events - Find similar historical events
4. generate_recommendation - Generate actionable recommendations

When analyzing an event:
1. First score the event to get quantitative metrics
2. Classify the risk to understand semantic categories
3. Find similar events for context
4. Generate a final recommendation

Provide a clear, structured summary of your analysis."""


class RiskAgent:
    """
    A lightweight LangChain agent that orchestrates risk analysis tools.
    Single-run analysis with no memory or chat history.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: str = None):
        """
        Initialize the Risk Agent.
        
        Args:
            model_name: OpenAI model to use
            api_key: OpenAI API key (uses env var if not provided)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=0,
        )
        self.llm_with_tools = self.llm.bind_tools(RISK_TOOLS)
        self.parser = StrOutputParser()
    
    def analyze(self, event_text: str) -> dict:
        """
        Analyze an event and return a comprehensive risk assessment.
        
        Args:
            event_text: The event content to analyze
            
        Returns:
            dict with scores, classification, similar events, and recommendation
        """
        # Step 1: Score the event
        scores = score_event.invoke(event_text)
        
        # Step 2: Classify risks
        classification = classify_risk.invoke(event_text)
        
        # Step 3: Find similar events
        similar = find_similar_events.invoke(event_text)
        
        # Step 4: Generate recommendation
        category_scores = classification["category_scores"]
        recommendation = generate_recommendation.invoke({
            "event_text": event_text,
            "operational_risk": category_scores.get("operational_risk", 0),
            "compliance_risk": category_scores.get("compliance_risk", 0),
            "reputational_risk": category_scores.get("reputational_risk", 0),
            "financial_risk": category_scores.get("financial_risk", 0),
        })
        
        # Step 5: Generate final summary using LLM
        summary_prompt = f"""
Summarize this risk analysis in 2-3 sentences:

Event: {event_text}

Scores: {scores}
Risk Classification: {classification['category_scores']}
Matched Keywords: {classification['matched_keywords']}
Similar Events Found: {len(similar)}
Recommendation: {recommendation}
"""
        
        messages = [
            SystemMessage(content="You are a concise risk analyst. Provide brief, actionable summaries."),
            HumanMessage(content=summary_prompt),
        ]
        
        try:
            summary = self.llm.invoke(messages).content
        except Exception:
            # Fallback if LLM not available
            summary = f"Analysis complete. {recommendation}"
        
        return {
            "event_text": event_text,
            "scores": scores,
            "classification": classification,
            "similar_events": similar,
            "recommendation": recommendation,
            "summary": summary,
        }


class RiskAgentSimple:
    """
    A simpler version that works without OpenAI API key.
    Uses rule-based analysis instead of LLM.
    """
    
    def analyze(self, event_text: str) -> dict:
        """
        Analyze an event using deterministic tools only.
        """
        # Step 1: Score the event
        scores = score_event.invoke(event_text)
        
        # Step 2: Classify risks
        classification = classify_risk.invoke(event_text)
        
        # Step 3: Find similar events
        similar = find_similar_events.invoke(event_text)
        
        # Step 4: Generate recommendation
        category_scores = classification["category_scores"]
        recommendation = generate_recommendation.invoke({
            "event_text": event_text,
            "operational_risk": category_scores.get("operational_risk", 0),
            "compliance_risk": category_scores.get("compliance_risk", 0),
            "reputational_risk": category_scores.get("reputational_risk", 0),
            "financial_risk": category_scores.get("financial_risk", 0),
        })
        
        # Generate deterministic summary
        max_risk_category = max(category_scores, key=category_scores.get)
        max_risk_value = category_scores[max_risk_category]
        matched = [kw for kws in classification["matched_keywords"].values() for kw in kws]
        
        if matched:
            summary = f"Event flagged for {max_risk_category.replace('_', ' ')} ({max_risk_value*100:.0f}% confidence). Keywords detected: {', '.join(matched)}. {recommendation}"
        else:
            summary = f"No significant risk indicators detected. {recommendation}"
        
        return {
            "event_text": event_text,
            "scores": scores,
            "classification": classification,
            "similar_events": similar,
            "recommendation": recommendation,
            "summary": summary,
        }
