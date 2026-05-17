from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UoMType(str, enum.Enum):
    min = "min"
    max = "max"
    timeline = "timeline"
    zero = "zero"


class GoalStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    returned = "returned"
    resubmitted = "resubmitted"
    approved = "approved"
    locked = "locked"
    rejected = "rejected"


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    thrust_area_id = Column(Integer, ForeignKey("thrust_areas.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    uom_type = Column(Enum(UoMType), nullable=False)
    target = Column(Float, nullable=True)
    target_date = Column(Date, nullable=True)
    weightage = Column(Float, nullable=False)
    status = Column(Enum(GoalStatus), nullable=False, default=GoalStatus.draft, index=True)
    is_shared = Column(Boolean, default=False)
    primary_owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rework_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employee = relationship("User", foreign_keys=[employee_id], back_populates="goals")
    primary_owner = relationship("User", foreign_keys=[primary_owner_id])
    thrust_area = relationship("ThrustArea", back_populates="goals")
    achievements = relationship("Achievement", back_populates="goal", cascade="all, delete-orphan")
    shared_links = relationship("SharedGoalLink", back_populates="goal", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="goal")
