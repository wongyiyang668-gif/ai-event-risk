from pydantic import BaseModel

class ScoreMatrix(BaseModel):
    signal_strength: float
    historical_rarity: float
    trend_acceleration: float
    cross_source_presence: float
    uncertainty: float
