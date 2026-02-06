import uuid
from app.models.event import Event, EventStatus
from app.models.score import ScoreMatrix
from app.services import scoring

def process_event(event: Event) -> ScoreMatrix:
    # Generate ID if missing
    if not event.id:
        event.id = str(uuid.uuid4())
    
    # Set default status
    event.status = EventStatus.NEW
    
    # Calculate scores
    score_matrix = scoring.calculate_scores(event.content)
    
    # Update status
    event.status = EventStatus.SCORED
    
    return score_matrix
