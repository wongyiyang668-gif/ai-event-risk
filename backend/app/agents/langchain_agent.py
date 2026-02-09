"""
LangChain-based Risk Analysis Agent.
Orchestrates existing services as tools for comprehensive risk analysis.
"""
import os
import json
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from app.services import scoring, semantics
from app.services.rag_service import find_similar_events
from app.services.llm_service import generate_risk_summary
from app.db.session import SessionLocal
from app.db.models import EventORM

# Tool 1: score_event
@tool
def score_event(event_text: str) -> dict:
    """
    Calculate quantitative risk scores for an event text.
    Returns signal_strength, historical_rarity, trend_acceleration, 
    cross_source_presence, and uncertainty.
    """
    score_matrix = scoring.calculate_scores(event_text)
    return {
        "signal_strength": score_matrix.signal_strength,
        "historical_rarity": score_matrix.historical_rarity,
        "trend_acceleration": score_matrix.trend_acceleration,
        "cross_source_presence": score_matrix.cross_source_presence,
        "uncertainty": score_matrix.uncertainty,
    }

# Tool 2: classify_risk
@tool
def classify_risk(event_text: str) -> dict:
    """
    Classify event into semantic risk categories using keyword anchors.
    Returns category scores and matched keywords.
    """
    result = semantics.calculate_semantics(event_text)
    return {
        "category_scores": result["category_scores"],
        "matched_keywords": result["matched_keywords"],
    }

# Tool 3: retrieve_similar
@tool
def retrieve_similar(event_text: str) -> list:
    """
    Retrieve top 3 similar historical events using RAG-like retrieval.
    """
    db = SessionLocal()
    try:
        events = db.query(EventORM).limit(100).all()
        past_events = [{"id": e.id, "content": e.content} for e in events]
    finally:
        db.close()
    
    return find_similar_events(event_text, past_events)

# Tool 4: summarize_risk
@tool
def summarize_risk(event_text: str, scores: dict, semantics_result: dict) -> dict:
    """
    Generate professional risk summary and recommendation using LLM reasoning.
    """
    return generate_risk_summary(event_text, scores, semantics_result)

class RiskAnalysisAgent:
    """
    Agent class that orchestrates risk tools using LangChain.
    """
    def __init__(self, model_name: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        self.llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
        self.tools = [score_event, classify_risk, retrieve_similar, summarize_risk]
        
        # Using initialize_agent with OPENAI_FUNCTIONS for reliable tool calling
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=False
        )

    def analyze(self, event_text: str) -> dict:
        """
        Execute the agent to perform full analysis.
        """
        prompt = f"""
Analyze the following event and provide a structured risk assessment:
Event Text: "{event_text}"

Steps:
1. Score the event quantitatively.
2. Classify risks into semantic categories.
3. Retrieve similar events for context.
4. Generate a summarized risk profile and recommendation.

Return a JSON-like structure ONLY with these keys: 
"scores", "semantics", "similar_events", "summary", "recommendation"
"""
        response = self.agent.run(prompt)
        
        # The agent output is usually a string, attempt to parse if it's formatted as JSON,
        # but the prompt asks for a dict return from the method.
        # For this implementation, we ensure the agent provides the structured data.
        try:
            # If the LLM returned a JSON string
            if "{" in response and "}" in response:
                json_part = response[response.find("{"):response.rfind("}")+1]
                return json.loads(json_part)
        except:
            pass
            
        return {"raw_output": response}
