from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class EventStatus(str, Enum):
    NEW = "NEW"
    SCORED = "SCORED"
    PROCESSED = "PROCESSED"

class Event(BaseModel):
    id: Optional[str] = None
    status: EventStatus = EventStatus.NEW
    content: str
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
