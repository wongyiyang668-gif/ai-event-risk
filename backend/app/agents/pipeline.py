import uuid
from app.models.event import Event, EventStatus
from app.models.score import ScoreMatrix
from app.models.risk_semantic import RiskSemantic
from app.models.explainability import Explainability, generate_reasoning
from app.services import scoring
from app.services import semantics
from app.services.rag_service import find_similar_events
from app.services.llm_service import generate_risk_summary
from app.db.session import SessionLocal
from app.db.models import EventORM


def _get_past_events() -> list[dict]:
    """Fetch past events from database for similarity search."""
    db = SessionLocal()
    try:
        events = db.query(EventORM).limit(100).all()
        return [{"id": e.id, "content": e.content} for e in events]
    finally:
        db.close()


def process_event(event: Event) -> tuple[ScoreMatrix, RiskSemantic, Explainability, list, dict]:
    """
    Process an event through the full analysis pipeline.
    
    Returns:
        (score_matrix, risk_semantics, explainability, similar_events, llm_output)
    """
    # Generate ID if missing
    if not event.id:
        event.id = str(uuid.uuid4())
    
    # Set default status
    event.status = EventStatus.NEW
    
    # Calculate scores
    score_matrix = scoring.calculate_scores(event.content)
    
    # Calculate risk semantics
    semantic_result = semantics.calculate_semantics(event.content)
    category_scores = semantic_result["category_scores"]
    matched_keywords = semantic_result["matched_keywords"]
    
    risk_semantic = RiskSemantic(**category_scores)
    
    # Generate explainability
    reasoning = generate_reasoning(matched_keywords, category_scores)
    explainability = Explainability(
        matched_keywords=matched_keywords,
        reasoning=reasoning
    )
    
    # RAG: Find similar events
    past_events = _get_past_events()
    similar_events = find_similar_events(event.content, past_events)
    
    # LLM: Generate risk summary
    scores_dict = {
        "signal_strength": score_matrix.signal_strength,
        "historical_rarity": score_matrix.historical_rarity,
        "trend_acceleration": score_matrix.trend_acceleration,
        "cross_source_presence": score_matrix.cross_source_presence,
        "uncertainty": score_matrix.uncertainty,
    }
    llm_output = generate_risk_summary(event.content, scores_dict, semantic_result)
    
    # Update status
    event.status = EventStatus.SCORED
    
    return score_matrix, risk_semantic, explainability, similar_events, llm_output
