from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class GoalProgressStatus(str, enum.Enum):
    not_started = "not_started"
    on_track = "on_track"
    completed = "completed"


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    cycle_id = Column(Integer, ForeignKey("goal_cycles.id"), nullable=False, index=True)
    actual_value = Column(Float, nullable=True)
    actual_date = Column(Date, nullable=True)
    tracking_score = Column(Float, nullable=True)
    goal_status = Column(Enum(GoalProgressStatus), nullable=False, default=GoalProgressStatus.not_started)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    goal = relationship("Goal", back_populates="achievements")
    cycle = relationship("GoalCycle", back_populates="achievements")
