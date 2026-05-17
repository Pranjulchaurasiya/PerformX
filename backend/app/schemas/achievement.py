from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models.achievement import GoalProgressStatus


class AchievementCreate(BaseModel):
    goal_id: int
    cycle_id: int
    actual_value: Optional[float] = None
    actual_date: Optional[date] = None
    goal_status: GoalProgressStatus = GoalProgressStatus.not_started


class AchievementUpdate(BaseModel):
    actual_value: Optional[float] = None
    actual_date: Optional[date] = None
    goal_status: Optional[GoalProgressStatus] = None


class AchievementOut(BaseModel):
    id: int
    goal_id: int
    cycle_id: int
    actual_value: Optional[float] = None
    actual_date: Optional[date] = None
    tracking_score: Optional[float] = None
    goal_status: GoalProgressStatus
    updated_at: datetime

    class Config:
        from_attributes = True
