from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import require_admin, get_current_user
from app.core.security import get_password_hash
from app.models.user import User
from app.models.department import Department
from app.models.thrust_area import ThrustArea
from app.models.goal_cycle import GoalCycle
from app.schemas.admin import (
    UserCreate, UserUpdate, UserOut,
    DepartmentCreate, DepartmentOut,
    ThrustAreaCreate, ThrustAreaOut,
    CycleCreate, CycleUpdate, CycleOut,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ---- Users ----

@router.get("/users", response_model=List[UserOut])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.offset((page - 1) * page_size).limit(page_size).all()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        department_id=payload.department_id,
        manager_id=payload.manager_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# ---- Departments ----

@router.get("/departments", response_model=List[DepartmentOut])
def list_departments(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    return db.query(Department).all()


@router.post("/departments", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    dept = Department(name=payload.name)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


# ---- Thrust Areas ----

@router.get("/thrust-areas", response_model=List[ThrustAreaOut])
def list_thrust_areas(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    return db.query(ThrustArea).all()


@router.post("/thrust-areas", response_model=ThrustAreaOut, status_code=status.HTTP_201_CREATED)
def create_thrust_area(
    payload: ThrustAreaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ta = ThrustArea(name=payload.name, department_id=payload.department_id)
    db.add(ta)
    db.commit()
    db.refresh(ta)
    return ta


@router.delete("/thrust-areas/{ta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thrust_area(
    ta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ta = db.query(ThrustArea).filter(ThrustArea.id == ta_id).first()
    if not ta:
        raise HTTPException(status_code=404, detail="Thrust area not found")
    db.delete(ta)
    db.commit()


# ---- Goal Cycles ----

# /admin/cycles GET is intentionally accessible to all authenticated users
# (not just admins) for reading active cycle/window info. This is used by
# the employee dashboard to show the "Next window opens: [date]" banner and
# by the Achievements page to determine the active cycle ID for saving records.
# All write operations (create, update, activate, deactivate) are protected
# by Admin role check inside each route handler.
@router.get("/cycles", response_model=List[CycleOut])
def list_cycles(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return db.query(GoalCycle).all()


@router.post("/cycles", response_model=CycleOut, status_code=status.HTTP_201_CREATED)
def create_cycle(
    payload: CycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cycle = GoalCycle(**payload.model_dump())
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.put("/cycles/{cycle_id}", response_model=CycleOut)
def update_cycle(
    cycle_id: int,
    payload: CycleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cycle = db.query(GoalCycle).filter(GoalCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cycle, field, value)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.post("/cycles/{cycle_id}/activate", response_model=CycleOut)
def activate_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    # Deactivate all others
    db.query(GoalCycle).update({"is_active": False})
    cycle = db.query(GoalCycle).filter(GoalCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    cycle.is_active = True
    db.commit()
    db.refresh(cycle)
    return cycle


@router.post("/cycles/{cycle_id}/deactivate", response_model=CycleOut)
def deactivate_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cycle = db.query(GoalCycle).filter(GoalCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    cycle.is_active = False
    db.commit()
    db.refresh(cycle)
    return cycle
