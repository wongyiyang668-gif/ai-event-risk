import uuid
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.agents import pipeline
from app.db.models import EventORM, ScoreORM, ReviewORM
from app.db.session import SessionLocal
from app.models.event import Event
from app.models.score import ScoreMatrix
from app.models.review import ReviewCreate, ReviewRead
from app.models.risk_semantic import RiskSemantic
from app.models.explainability import Explainability, generate_reasoning
from app.services import semantics

router = APIRouter()

@router.post("/events")
def create_event(event: Event):
    score_matrix, risk_semantic, explainability, similar_events, llm_output = pipeline.process_event(event)

    event_id = str(uuid.uuid4())

    db = SessionLocal()
    try:
        event_orm = EventORM(
            id=event_id,
            content=event.content,
            source=event.source,
            timestamp=event.timestamp,
            status=event.status.value if hasattr(event.status, "value") else str(event.status),
        )
        score_orm = ScoreORM(
            event_id=event_id,
            signal_strength=score_matrix.signal_strength,
            historical_rarity=score_matrix.historical_rarity,
            trend_acceleration=score_matrix.trend_acceleration,
            cross_source_presence=score_matrix.cross_source_presence,
            uncertainty=score_matrix.uncertainty,
        )
        event_orm.score = score_orm
        db.add(event_orm)
        db.commit()
    finally:
        db.close()

    event.id = event_id
    return {
        "event": event,
        "score_matrix": score_matrix,
        "risk_semantics": risk_semantic,
        "explainability": explainability,
        "similar_events": similar_events,
        "risk_summary": llm_output.get("summary"),
        "recommendation": llm_output.get("recommendation")
    }


@router.get("/events")
def list_events(limit: int = 100):
    db = SessionLocal()
    try:
        events = db.query(EventORM).order_by(EventORM.timestamp.desc()).limit(limit).all()
        results = []
        for event_orm in events:
            score_orm = event_orm.score
            score_matrix = None
            if score_orm:
                score_matrix = ScoreMatrix(
                    signal_strength=score_orm.signal_strength,
                    historical_rarity=score_orm.historical_rarity,
                    trend_acceleration=score_orm.trend_acceleration,
                    cross_source_presence=score_orm.cross_source_presence,
                    uncertainty=score_orm.uncertainty,
                )
            event_model = Event(
                id=event_orm.id,
                content=event_orm.content,
                source=event_orm.source,
                timestamp=event_orm.timestamp,
                status=event_orm.status,
            )
            results.append({"event": event_model, "score_matrix": score_matrix})
        return results
    finally:
        db.close()


@router.get("/stats")
def get_stats():
    db = SessionLocal()
    try:
        total_events = db.query(EventORM).count()
        total_reviews = db.query(ReviewORM).count()
        
        # Simple high risk count (naive scan for now)
        recent_events = db.query(EventORM).order_by(EventORM.timestamp.desc()).limit(10).all()
        
        return {
            "total_events": total_events,
            "total_reviews": total_reviews,
            "recent_count": len(recent_events),
            "status": "operational"
        }
    finally:
        db.close()


@router.get("/events/{event_id}")
def get_event(event_id: str):
    db = SessionLocal()
    try:
        event_orm = db.query(EventORM).filter(EventORM.id == event_id).first()
        if not event_orm:
            raise HTTPException(status_code=404, detail="Event not found")
        
        score_orm = event_orm.score
        score_matrix = None
        if score_orm:
            score_matrix = ScoreMatrix(
                signal_strength=score_orm.signal_strength,
                historical_rarity=score_orm.historical_rarity,
                trend_acceleration=score_orm.trend_acceleration,
                cross_source_presence=score_orm.cross_source_presence,
                uncertainty=score_orm.uncertainty,
            )
        
        event_model = Event(
            id=event_orm.id,
            content=event_orm.content,
            source=event_orm.source,
            timestamp=event_orm.timestamp,
            status=event_orm.status,
        )
        
        reviews = [
            ReviewRead(
                reviewer=r.reviewer,
                note=r.note,
                reviewed_at=r.reviewed_at
            ) for r in event_orm.reviews
        ]
        
        # Calculate risk semantics on-the-fly
        semantic_scores = semantics.calculate_semantics(event_orm.content)
        risk_semantic = RiskSemantic(**semantic_scores)
        
        return {
            "event": event_model,
            "score": score_matrix,
            "reviews": reviews,
            "risk_semantics": risk_semantic
        }
    finally:
        db.close()


@router.post("/events/{event_id}/review")
def create_review(event_id: str, review: ReviewCreate):
    db = SessionLocal()
    try:
        event = db.query(EventORM).filter(EventORM.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        review_orm = ReviewORM(
            event_id=event_id,
            reviewer=review.reviewer,
            note=review.note,
            reviewed_at=datetime.utcnow()
        )
        db.add(review_orm)
        db.commit()
        return {"message": "Review added successfully"}
    finally:
        db.close()
