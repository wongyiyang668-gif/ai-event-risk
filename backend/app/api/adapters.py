from datetime import datetime
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, Any

class IngestedEvent(BaseModel):
    source: str
    sender: str
    content: str
    timestamp: datetime

class BaseAdapter(ABC):
    @abstractmethod
    def transform(self, payload: Dict[str, Any]) -> IngestedEvent:
        pass

class TelegramAdapter(BaseAdapter):
    def transform(self, payload: Dict[str, Any]) -> IngestedEvent:
        # Expected Telegram payload structure
        message = payload.get("message", {})
        from_user = message.get("from", {})
        return IngestedEvent(
            source="telegram",
            sender=str(from_user.get("id", "unknown")),
            content=message.get("text", ""),
            timestamp=datetime.fromtimestamp(message.get("date", datetime.now().timestamp()))
        )

class EmailAdapter(BaseAdapter):
    def transform(self, payload: Dict[str, Any]) -> IngestedEvent:
        # Expected Email payload structure
        return IngestedEvent(
            source="email",
            sender=payload.get("from", "unknown"),
            content=payload.get("body", ""),
            timestamp=datetime.fromisoformat(payload.get("date", datetime.now().isoformat()))
        )

class WhatsAppAdapter(BaseAdapter):
    def transform(self, payload: Dict[str, Any]) -> IngestedEvent:
        # Expected WhatsApp payload structure (Experimental)
        return IngestedEvent(
            source="whatsapp",
            sender=payload.get("sender_number", "unknown"),
            content=payload.get("message_text", ""),
            timestamp=datetime.now() # WhatsApp payloads often need custom timing
        )
