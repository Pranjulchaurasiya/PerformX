from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.escalation import EscalationStatus


class EscalationRuleCreate(BaseModel):
    rule_name: str
    trigger_event: str
    threshold_days: int
    step1_delay_days: int
    step2_delay_days: int
    is_active: bool = True


class EscalationRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    threshold_days: Optional[int] = None
    step1_delay_days: Optional[int] = None
    step2_delay_days: Optional[int] = None
    is_active: Optional[bool] = None


class EscalationRuleOut(BaseModel):
    id: int
    rule_name: str
    trigger_event: str
    threshold_days: int
    step1_delay_days: int
    step2_delay_days: int
    is_active: bool

    class Config:
        from_attributes = True


class EscalationLogOut(BaseModel):
    id: int
    rule_id: int
    rule_name: Optional[str] = None
    target_user_id: int
    target_user_name: Optional[str] = None
    step_reached: int
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    status: EscalationStatus

    class Config:
        from_attributes = True
