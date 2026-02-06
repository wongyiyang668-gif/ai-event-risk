from datetime import datetime
from pydantic import BaseModel

class ReviewCreate(BaseModel):
    reviewer: str
    note: str

class ReviewRead(BaseModel):
    reviewer: str
    note: str
    reviewed_at: datetime

    class Config:
        from_attributes = True
