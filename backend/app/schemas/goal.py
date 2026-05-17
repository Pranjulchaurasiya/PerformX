from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List
from datetime import date, datetime
from app.models.goal import UoMType, GoalStatus


class GoalCreate(BaseModel):
    thrust_area_id: int
    title: str
    description: Optional[str] = None
    uom_type: UoMType
    target: Optional[float] = None
    target_date: Optional[date] = None
    weightage: float

    @field_validator("weightage")
    @classmethod
    def weightage_min(cls, v):
        if v < 10:
            raise ValueError("Minimum weightage per goal is 10%")
        return v

    @model_validator(mode="after")
    def check_target(self):
        if self.uom_type == UoMType.timeline:
            if not self.target_date:
                raise ValueError("target_date is required for Timeline UoM")
        else:
            if self.target is None:
                raise ValueError("target is required for this UoM type")
        return self


class GoalUpdate(BaseModel):
    thrust_area_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    uom_type: Optional[UoMType] = None
    target: Optional[float] = None
    target_date: Optional[date] = None
    weightage: Optional[float] = None


class GoalManagerUpdate(BaseModel):
    target: Optional[float] = None
    target_date: Optional[date] = None
    weightage: Optional[float] = None


class GoalReturnRequest(BaseModel):
    comment: str


class GoalUnlockRequest(BaseModel):
    reason: str


class ThrustAreaOut(BaseModel):
    id: int
    name: str
    department_id: Optional[int] = None

    class Config:
        from_attributes = True


class GoalOut(BaseModel):
    id: int
    employee_id: int
    thrust_area_id: int
    thrust_area: Optional[ThrustAreaOut] = None
    title: str
    description: Optional[str] = None
    uom_type: UoMType
    target: Optional[float] = None
    target_date: Optional[date] = None
    weightage: float
    status: GoalStatus
    is_shared: bool
    primary_owner_id: Optional[int] = None
    primary_owner_name: Optional[str] = None   # populated by API for shared goals
    linked_employee_count: Optional[int] = None  # how many employees share this goal
    rework_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalListResponse(BaseModel):
    items: List[GoalOut]
    total: int
    page: int
    page_size: int
