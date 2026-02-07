import uuid
from app.models.event import Event, EventStatus
from app.models.score import ScoreMatrix
from app.models.risk_semantic import RiskSemantic
from app.models.explainability import Explainability, generate_reasoning
from app.services import scoring
from app.services import semantics


def process_event(event: Event) -> tuple[ScoreMatrix, RiskSemantic, Explainability]:
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
    
    # Update status
    event.status = EventStatus.SCORED
    
    return score_matrix, risk_semantic, explainability
