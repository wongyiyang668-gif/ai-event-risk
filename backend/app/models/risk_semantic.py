from pydantic import BaseModel


class RiskSemantic(BaseModel):
    operational_risk: float
    compliance_risk: float
    reputational_risk: float
    financial_risk: float
