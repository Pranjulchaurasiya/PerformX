from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class EscalationStatus(str, enum.Enum):
    open = "open"
    resolved = "resolved"


class EscalationRule(Base):
    __tablename__ = "escalation_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(200), nullable=False)
    trigger_event = Column(String(100), nullable=False)
    threshold_days = Column(Integer, nullable=False, default=7)
    step1_delay_days = Column(Integer, nullable=False, default=3)
    step2_delay_days = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    logs = relationship("EscalationLog", back_populates="rule")


class EscalationLog(Base):
    __tablename__ = "escalation_logs"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("escalation_rules.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    step_reached = Column(Integer, default=1)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(EscalationStatus), default=EscalationStatus.open)

    rule = relationship("EscalationRule", back_populates="logs")
    target_user = relationship("User")
