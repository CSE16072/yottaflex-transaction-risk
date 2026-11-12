
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TransactionResponse(BaseModel):
    transaction_id: str
    account_id: str
    merchant_id: Optional[str] = None
    amount: float
    currency: str
    transaction_type: str
    status: str
    timestamp: datetime


class AlertResponse(BaseModel):
    alert_id: str
    customer_id: str
    transaction_id: Optional[str] = None
    risk_score: float
    risk_level: str
    status: str
    explanation: str
    created_at: datetime


class CaseResponse(BaseModel):
    case_id: str
    customer_id: str
    status: str
    priority: str
    disposition: Optional[str] = None
    created_at: datetime


class AnalystActionRequest(BaseModel):
    analyst_id: str = Field(min_length=1)
    action_type: str = Field(min_length=1)
    comments: Optional[str] = None


class CaseUpdateRequest(BaseModel):
    status: str
    disposition: Optional[str] = None
    comments: Optional[str] = None


class RiskScoreResponse(BaseModel):
    transaction_id: str
    risk_score: float
    risk_level: str
    reasons: list[str]


class DashboardSummary(BaseModel):
    total_customers: int
    total_accounts: int
    total_transactions: int
    total_alerts: int
    open_alerts: int
    open_cases: int
