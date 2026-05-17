from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CyclePhase(str, enum.Enum):
    goal_setting = "goal_setting"
    q1 = "q1"
    q2 = "q2"
    q3 = "q3"
    q4 = "q4"


class GoalCycle(Base):
    __tablename__ = "goal_cycles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phase = Column(Enum(CyclePhase), nullable=False)
    window_open = Column(Date, nullable=True)
    window_close = Column(Date, nullable=True)
    is_active = Column(Boolean, default=False)
    # Configurable penalty rate for Timeline UoM: % deducted per day late (default 5%)
    penalty_factor = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    achievements = relationship("Achievement", back_populates="cycle")
    checkins = relationship("Checkin", back_populates="cycle")
