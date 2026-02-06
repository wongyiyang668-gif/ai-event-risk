from pydantic import BaseModel

class RiskSemantic(BaseModel):
    label: str
    description: str
    severity: float
