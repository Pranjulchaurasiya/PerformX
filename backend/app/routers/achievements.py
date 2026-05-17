from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.goal import Goal, GoalStatus, UoMType
from app.models.achievement import Achievement
from app.models.goal_cycle import GoalCycle
from app.models.shared_goal_link import SharedGoalLink
from app.schemas.achievement import AchievementCreate, AchievementUpdate, AchievementOut
from app.services.score_engine import compute_tracking_score

router = APIRouter(prefix="/achievements", tags=["achievements"])


def _get_active_cycle(db: Session) -> Optional[GoalCycle]:
    return db.query(GoalCycle).filter(GoalCycle.is_active == True).first()


def _check_window_open(cycle: Optional[GoalCycle]) -> bool:
    if not cycle:
        return False
    today = date.today()
    if cycle.window_open and cycle.window_close:
        return cycle.window_open <= today <= cycle.window_close
    return cycle.is_active


@router.get("")
def list_achievements(
    goal_id: Optional[int] = None,
    cycle_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Achievement)

    if current_user.role == "employee":
        # Only own goals
        own_goal_ids = [g.id for g in db.query(Goal).filter(
            Goal.employee_id == current_user.id).all()]
        query = query.filter(Achievement.goal_id.in_(own_goal_ids))
    elif current_user.role == "manager":
        if employee_id:
            emp = db.query(User).filter(User.id == employee_id,
                                         User.manager_id == current_user.id).first()
            if not emp:
                raise HTTPException(status_code=403, detail="Not your team member")
            team_goal_ids = [g.id for g in db.query(Goal).filter(
                Goal.employee_id == employee_id).all()]
        else:
            team_ids = [u.id for u in db.query(User).filter(
                User.manager_id == current_user.id).all()]
            team_goal_ids = [g.id for g in db.query(Goal).filter(
                Goal.employee_id.in_(team_ids)).all()]
        query = query.filter(Achievement.goal_id.in_(team_goal_ids))

    if goal_id:
        query = query.filter(Achievement.goal_id == goal_id)
    if cycle_id:
        query = query.filter(Achievement.cycle_id == cycle_id)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [AchievementOut.model_validate(a) for a in items],
            "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=AchievementOut, status_code=status.HTTP_201_CREATED)
def create_achievement(
    payload: AchievementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check window
    cycle = db.query(GoalCycle).filter(GoalCycle.id == payload.cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    if not _check_window_open(cycle):
        raise HTTPException(status_code=400, detail="Achievement window is not currently open")

    goal = db.query(Goal).filter(Goal.id == payload.goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Only primary owner can enter achievement for shared goals
    if goal.is_shared and goal.primary_owner_id != current_user.id:
        raise HTTPException(status_code=403,
                            detail="Only the primary owner can enter achievement for shared goals")

    if goal.employee_id != current_user.id and not goal.is_shared:
        raise HTTPException(status_code=403, detail="Not your goal")

    if goal.status != GoalStatus.locked:
        raise HTTPException(status_code=400, detail="Can only update achievements for locked goals")

    # Check if already exists
    existing = db.query(Achievement).filter(
        Achievement.goal_id == payload.goal_id,
        Achievement.cycle_id == payload.cycle_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Achievement already exists. Use PUT to update.")

    score = compute_tracking_score(
        uom_type=goal.uom_type,
        target=goal.target,
        achievement=payload.actual_value,
        target_date=goal.target_date,
        actual_date=payload.actual_date,
        start_date=goal.created_at.date() if goal.created_at else None,
        penalty_factor=getattr(cycle, "penalty_factor", None),
    )

    ach = Achievement(
        goal_id=payload.goal_id,
        cycle_id=payload.cycle_id,
        actual_value=payload.actual_value,
        actual_date=payload.actual_date,
        tracking_score=score,
        goal_status=payload.goal_status,
    )
    db.add(ach)
    db.commit()
    db.refresh(ach)

    # Sync shared goal achievement
    if goal.is_shared:
        _sync_shared_achievement(db, goal, payload.cycle_id, payload.actual_value,
                                  payload.actual_date, payload.goal_status,
                                  getattr(cycle, "penalty_factor", None))

    return ach


@router.put("/{achievement_id}", response_model=AchievementOut)
def update_achievement(
    achievement_id: int,
    payload: AchievementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ach = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")

    goal = db.query(Goal).filter(Goal.id == ach.goal_id).first()

    # Check window
    cycle = db.query(GoalCycle).filter(GoalCycle.id == ach.cycle_id).first()
    if not _check_window_open(cycle):
        raise HTTPException(status_code=400, detail="Achievement window is not currently open")

    if goal.employee_id != current_user.id and not (goal.is_shared and goal.primary_owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ach, field, value)

    # Recompute score
    ach.tracking_score = compute_tracking_score(
        uom_type=goal.uom_type,
        target=goal.target,
        achievement=ach.actual_value,
        target_date=goal.target_date,
        actual_date=ach.actual_date,
        start_date=goal.created_at.date() if goal.created_at else None,
        penalty_factor=getattr(cycle, "penalty_factor", None),
    )

    db.commit()
    db.refresh(ach)

    if goal.is_shared:
        _sync_shared_achievement(db, goal, ach.cycle_id, ach.actual_value,
                                  ach.actual_date, ach.goal_status,
                                  getattr(cycle, "penalty_factor", None))

    return ach


def _sync_shared_achievement(db: Session, primary_goal: Goal, cycle_id: int,
                               actual_value, actual_date, goal_status,
                               penalty_factor=None):
    """Sync primary owner's achievement to all linked employees."""
    links = db.query(SharedGoalLink).filter(
        SharedGoalLink.goal_id == primary_goal.id).all()

    for link in links:
        if link.employee_id == primary_goal.primary_owner_id:
            continue
        # Find linked employee's goal (same shared goal)
        linked_ach = db.query(Achievement).filter(
            Achievement.goal_id == primary_goal.id,
            Achievement.cycle_id == cycle_id,
        ).first()
        if linked_ach:
            linked_ach.actual_value = actual_value
            linked_ach.actual_date = actual_date
            linked_ach.goal_status = goal_status
            linked_ach.tracking_score = compute_tracking_score(
                uom_type=primary_goal.uom_type,
                target=primary_goal.target,
                achievement=actual_value,
                target_date=primary_goal.target_date,
                actual_date=actual_date,
                penalty_factor=penalty_factor,
            )
    db.commit()
