from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditLogOut(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    goal_id: Optional[int] = None
    field_changed: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True
