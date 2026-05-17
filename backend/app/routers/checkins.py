from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager_or_admin
from app.models.user import User
from app.models.checkin import Checkin
from app.models.goal_cycle import GoalCycle, CyclePhase
from app.schemas.checkin import CheckinCreate, CheckinOut
from app.services.window_guard import get_open_quarter, next_window_info

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.get("")
def list_checkins(
    employee_id: Optional[int] = None,
    cycle_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Checkin)

    if current_user.role == "manager":
        query = query.filter(Checkin.manager_id == current_user.id)
    elif current_user.role == "employee":
        query = query.filter(Checkin.employee_id == current_user.id)

    if employee_id:
        query = query.filter(Checkin.employee_id == employee_id)
    if cycle_id:
        query = query.filter(Checkin.cycle_id == cycle_id)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [CheckinOut.model_validate(c) for c in items],
            "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=CheckinOut, status_code=status.HTTP_201_CREATED)
def create_checkin(
    payload: CheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    # Verify employee is under this manager
    if current_user.role == "manager":
        emp = db.query(User).filter(User.id == payload.employee_id,
                                     User.manager_id == current_user.id).first()
        if not emp:
            raise HTTPException(status_code=403, detail="Not your team member")

    cycle = db.query(GoalCycle).filter(GoalCycle.id == payload.cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    # Check if already exists
    existing = db.query(Checkin).filter(
        Checkin.manager_id == current_user.id,
        Checkin.employee_id == payload.employee_id,
        Checkin.cycle_id == payload.cycle_id,
    ).first()

    if existing:
        # Update existing
        existing.comment_type = payload.comment_type
        existing.comment_text = payload.comment_text
        existing.is_completed = True
        existing.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    checkin = Checkin(
        manager_id=current_user.id,
        employee_id=payload.employee_id,
        cycle_id=payload.cycle_id,
        comment_type=payload.comment_type,
        comment_text=payload.comment_text,
        is_completed=True,
        completed_at=datetime.utcnow(),
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


@router.get("/completion-status")
def checkin_completion_status(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Real-time completion dashboard."""
    if current_user.role == "employee":
        raise HTTPException(status_code=403, detail="Not allowed")

    if current_user.role == "manager":
        team = db.query(User).filter(User.manager_id == current_user.id).all()
    else:
        team = db.query(User).filter(User.role == "employee").all()

    result = []
    for emp in team:
        checkin = db.query(Checkin).filter(
            Checkin.employee_id == emp.id,
            Checkin.cycle_id == cycle_id,
            Checkin.is_completed == True,
        ).first()
        result.append({
            "employee_id": emp.id,
            "employee_name": emp.name,
            "completed": checkin is not None,
            "completed_at": checkin.completed_at if checkin else None,
        })

    return result


@router.get("/window-status")
def checkin_window_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the currently open check-in quarter (if any) and the next
    upcoming window.  Used by the frontend guard to block/allow access.
    """
    open_cycle = get_open_quarter(db)
    next_phase, next_date = next_window_info(db)
    return {
        "open_quarter": open_cycle.phase if open_cycle else None,
        "open_cycle_id": open_cycle.id if open_cycle else None,
        "window_open": open_cycle.window_open if open_cycle else None,
        "window_close": open_cycle.window_close if open_cycle else None,
        "next_phase": next_phase,
        "next_window_opens": next_date,
    }
