from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.checkin import CommentType


class CheckinCreate(BaseModel):
    employee_id: int
    cycle_id: int
    comment_type: CommentType
    comment_text: str


class CheckinOut(BaseModel):
    id: int
    manager_id: int
    employee_id: int
    cycle_id: int
    comment_type: Optional[CommentType] = None
    comment_text: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
