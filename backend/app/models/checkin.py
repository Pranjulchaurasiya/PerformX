from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CommentType(str, enum.Enum):
    positive_feedback = "positive_feedback"
    needs_improvement = "needs_improvement"
    at_risk = "at_risk"
    note = "note"


class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cycle_id = Column(Integer, ForeignKey("goal_cycles.id"), nullable=False)
    comment_type = Column(Enum(CommentType), nullable=True)
    comment_text = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    manager = relationship("User", foreign_keys=[manager_id])
    employee = relationship("User", foreign_keys=[employee_id])
    cycle = relationship("GoalCycle", back_populates="checkins")
