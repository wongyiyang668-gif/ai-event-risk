from fastapi import APIRouter, HTTPException
from app.api.adapters import TelegramAdapter, EmailAdapter, WhatsAppAdapter, IngestedEvent
from app.agents import pipeline
from app.db.models import EventORM, ScoreORM
from app.db.session import SessionLocal
from app.models.event import Event, EventStatus
from typing import Dict, Any

from app.services.notification import notification_service

router = APIRouter(prefix="/ingest", tags=["ingestion"])

telegram_adapter = TelegramAdapter()
email_adapter = EmailAdapter()
whatsapp_adapter = WhatsAppAdapter()

def process_ingested_event(ingested: IngestedEvent):
    # Convert to internal Event model for pipeline
    event_model = Event(
        content=ingested.content,
        source=ingested.source,
        timestamp=ingested.timestamp,
        status=EventStatus.NEW
    )
    
    # Process through pipeline
    score_matrix, risk_semantic, explainability, similar_events, llm_output = pipeline.process_event(event_model)
    
    # Persist to DB
    db = SessionLocal()
    try:
        event_orm = EventORM(
            id=event_model.id,
            content=event_model.content,
            source=event_model.source,
            timestamp=event_model.timestamp,
            status=event_model.status.value
        )
        score_orm = ScoreORM(
            event_id=event_model.id,
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

    # Check for high risk and send alert
    max_risk = max(
        risk_semantic.operational_risk, 
        risk_semantic.compliance_risk, 
        risk_semantic.reputational_risk, 
        risk_semantic.financial_risk
    )
    
    if max_risk >= 0.6:
        notification_service.send_risk_alert(
            event_id=event_model.id,
            content=event_model.content,
            source=event_model.source,
            risk_summary=llm_output.get("summary", "No summary available."),
            recommendation=llm_output.get("recommendation", "Review immediately."),
            risk_score=max_risk
        )
    
    return {
        "event_id": event_model.id,
        "source": ingested.source,
        "status": "processed",
        "risk_level": "high" if max_risk >= 0.6 else "normal"
    }

@router.post("/message")
async def ingest_message(event: IngestedEvent):
    """
    Generic ingestion endpoint for standard normalized messages.
    """
    try:
        return process_ingested_event(event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/telegram")
async def ingest_telegram(payload: Dict[str, Any]):
    try:
        ingested = telegram_adapter.transform(payload)
        return process_ingested_event(ingested)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/email")
async def ingest_email(payload: Dict[str, Any]):
    try:
        ingested = email_adapter.transform(payload)
        return process_ingested_event(ingested)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/whatsapp")
async def ingest_whatsapp(payload: Dict[str, Any]):
    try:
        ingested = whatsapp_adapter.transform(payload)
        return process_ingested_event(ingested)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
