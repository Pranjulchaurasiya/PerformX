from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from app.models.user import UserRole
from app.models.goal_cycle import CyclePhase


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    department_id: Optional[int] = None
    manager_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    department_id: Optional[int] = None
    manager_id: Optional[int] = None

    class Config:
        from_attributes = True


class DepartmentCreate(BaseModel):
    name: str


class DepartmentOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ThrustAreaCreate(BaseModel):
    name: str
    department_id: Optional[int] = None


class ThrustAreaOut(BaseModel):
    id: int
    name: str
    department_id: Optional[int] = None

    class Config:
        from_attributes = True


class CycleCreate(BaseModel):
    name: str
    phase: CyclePhase
    window_open: Optional[date] = None
    window_close: Optional[date] = None
    is_active: bool = False
    # Late completion penalty for Timeline UoM: fraction per day (0.05 = 5%)
    penalty_factor: float = 0.05


class CycleUpdate(BaseModel):
    name: Optional[str] = None
    window_open: Optional[date] = None
    window_close: Optional[date] = None
    is_active: Optional[bool] = None
    penalty_factor: Optional[float] = None


class CycleOut(BaseModel):
    id: int
    name: str
    phase: CyclePhase
    window_open: Optional[date] = None
    window_close: Optional[date] = None
    is_active: bool
    penalty_factor: float = 0.05

    class Config:
        from_attributes = True
