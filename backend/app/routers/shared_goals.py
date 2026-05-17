from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager_or_admin
from app.models.user import User
from app.models.goal import Goal, GoalStatus, UoMType
from app.models.shared_goal_link import SharedGoalLink
from app.schemas.shared_goal import SharedGoalCreate, SharedGoalWeightageUpdate
from app.schemas.goal import GoalOut

router = APIRouter(prefix="/shared-goals", tags=["shared-goals"])


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_shared_goal(
    payload: SharedGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """Admin or Manager creates a shared/departmental KPI and assigns to multiple employees."""
    if not payload.employee_ids:
        raise HTTPException(status_code=400, detail="At least one employee required")

    primary_owner_id = payload.employee_ids[0]

    goal = Goal(
        employee_id=primary_owner_id,
        thrust_area_id=payload.thrust_area_id,
        title=payload.title,
        description=payload.description,
        uom_type=payload.uom_type,
        target=payload.target,
        weightage=payload.default_weightage,
        status=GoalStatus.approved,
        is_shared=True,
        primary_owner_id=primary_owner_id,
    )
    db.add(goal)
    db.flush()

    for emp_id in payload.employee_ids:
        link = SharedGoalLink(
            goal_id=goal.id,
            employee_id=emp_id,
            weightage=payload.default_weightage,
        )
        db.add(link)

    db.commit()
    db.refresh(goal)
    return goal


@router.put("/{goal_id}/weightage")
def update_shared_goal_weightage(
    goal_id: int,
    payload: SharedGoalWeightageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Employee can update their own weightage on a shared goal."""
    link = db.query(SharedGoalLink).filter(
        SharedGoalLink.goal_id == goal_id,
        SharedGoalLink.employee_id == current_user.id,
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Shared goal link not found")

    if payload.weightage < 10:
        raise HTTPException(status_code=400, detail="Minimum weightage is 10%")

    link.weightage = payload.weightage
    db.commit()
    return {"message": "Weightage updated", "weightage": payload.weightage}


@router.get("/{goal_id}/links")
def get_shared_goal_links(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = db.query(SharedGoalLink).filter(SharedGoalLink.goal_id == goal_id).all()
    return [{"employee_id": l.employee_id, "weightage": l.weightage} for l in links]
