from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.core.deps import get_current_user, require_manager_or_admin, require_admin
from app.models.user import User
from app.models.goal import Goal, GoalStatus, UoMType
from app.models.audit_log import AuditLog
from app.models.shared_goal_link import SharedGoalLink
from app.schemas.goal import (
    GoalCreate, GoalUpdate, GoalOut, GoalListResponse,
    GoalManagerUpdate, GoalReturnRequest, GoalUnlockRequest, ThrustAreaOut
)
from app.models.thrust_area import ThrustArea
from app.services import email_service

router = APIRouter(prefix="/goals", tags=["goals"])

MAX_GOALS = 8
MIN_WEIGHTAGE = 10.0


def _enrich_goal(goal: Goal, db: Session) -> GoalOut:
    """Convert Goal ORM object to GoalOut, enriching shared-goal fields."""
    out = GoalOut.model_validate(goal)
    if goal.is_shared and goal.primary_owner_id:
        owner = db.query(User).filter(User.id == goal.primary_owner_id).first()
        out.primary_owner_name = owner.name if owner else None
        out.linked_employee_count = db.query(SharedGoalLink).filter(
            SharedGoalLink.goal_id == goal.id
        ).count()
    return out


def _validate_weightage(db: Session, employee_id: int, new_weightage: float,
                         exclude_goal_id: Optional[int] = None):
    """Validate total weightage = 100% across all non-draft goals."""
    query = db.query(Goal).filter(
        Goal.employee_id == employee_id,
        Goal.status != GoalStatus.rejected,
    )
    if exclude_goal_id:
        query = query.filter(Goal.id != exclude_goal_id)
    existing = query.all()
    total = sum(g.weightage for g in existing) + new_weightage
    return total, existing


@router.get("/thrust-areas", response_model=List[ThrustAreaOut])
def list_thrust_areas(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    return db.query(ThrustArea).all()


@router.get("", response_model=GoalListResponse)
def list_goals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Goal).options(joinedload(Goal.thrust_area))

    if current_user.role == "employee":
        query = query.filter(Goal.employee_id == current_user.id)
    elif current_user.role == "manager":
        if employee_id:
            # Verify employee is under this manager
            emp = db.query(User).filter(User.id == employee_id,
                                         User.manager_id == current_user.id).first()
            if not emp:
                raise HTTPException(status_code=403, detail="Not your team member")
            query = query.filter(Goal.employee_id == employee_id)
        else:
            team_ids = [u.id for u in db.query(User).filter(
                User.manager_id == current_user.id).all()]
            query = query.filter(Goal.employee_id.in_(team_ids))
    # admin sees all

    if status:
        query = query.filter(Goal.status == status)

    total = query.count()
    goals = query.offset((page - 1) * page_size).limit(page_size).all()
    enriched = [_enrich_goal(g, db) for g in goals]
    return GoalListResponse(items=enriched, total=total, page=page, page_size=page_size)


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("employee", "manager", "admin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    employee_id = current_user.id

    # Max 8 goals check
    existing_count = db.query(Goal).filter(
        Goal.employee_id == employee_id,
        Goal.status != GoalStatus.rejected,
    ).count()
    if existing_count >= MAX_GOALS:
        raise HTTPException(status_code=400, detail="Maximum 8 goals per employee allowed")

    # Min weightage
    if payload.weightage < MIN_WEIGHTAGE:
        raise HTTPException(status_code=400, detail="Minimum weightage per goal is 10%")

    # Total weightage check (draft goals included for running total)
    total, _ = _validate_weightage(db, employee_id, payload.weightage)
    if total > 100:
        raise HTTPException(
            status_code=400,
            detail=f"Total weightage would exceed 100% (current total would be {total}%)"
        )

    goal = Goal(
        employee_id=employee_id,
        thrust_area_id=payload.thrust_area_id,
        title=payload.title,
        description=payload.description,
        uom_type=payload.uom_type,
        target=payload.target,
        target_date=payload.target_date,
        weightage=payload.weightage,
        status=GoalStatus.draft,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/{goal_id}", response_model=GoalOut)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).options(joinedload(Goal.thrust_area)).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    _check_access(goal, current_user, db)
    return _enrich_goal(goal, db)


@router.put("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if goal.employee_id != current_user.id and current_user.role not in ("manager", "admin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    if goal.status in (GoalStatus.approved, GoalStatus.locked):
        raise HTTPException(status_code=400, detail="Cannot edit approved/locked goals")

    if goal.status not in (GoalStatus.draft, GoalStatus.returned, GoalStatus.resubmitted):
        raise HTTPException(status_code=400, detail="Goal cannot be edited in current state")

    update_data = payload.model_dump(exclude_unset=True)

    if "weightage" in update_data:
        new_w = update_data["weightage"]
        if new_w < MIN_WEIGHTAGE:
            raise HTTPException(status_code=400, detail="Minimum weightage is 10%")
        total, _ = _validate_weightage(db, goal.employee_id, new_w, exclude_goal_id=goal_id)
        if total > 100:
            raise HTTPException(status_code=400, detail=f"Total weightage would be {total}%")

    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return goal


@router.post("/{goal_id}/submit", response_model=GoalOut)
def submit_goal(
    goal_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.employee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your goal")
    if goal.status not in (GoalStatus.draft, GoalStatus.returned, GoalStatus.resubmitted):
        raise HTTPException(status_code=400, detail="Goal cannot be submitted in current state")

    # Validate total weightage = 100% before submission
    all_goals = db.query(Goal).filter(
        Goal.employee_id == current_user.id,
        Goal.status != GoalStatus.rejected,
    ).all()
    total = sum(g.weightage for g in all_goals)
    if abs(total - 100.0) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Total weightage must equal 100% before submission. Current: {total}%"
        )

    new_status = GoalStatus.resubmitted if goal.status == GoalStatus.returned else GoalStatus.submitted
    goal.status = new_status

    # Audit log for resubmission
    if new_status == GoalStatus.resubmitted:
        audit = AuditLog(
            user_id=current_user.id,
            goal_id=goal.id,
            field_changed="status",
            old_value=GoalStatus.returned,
            new_value=GoalStatus.resubmitted,
            reason="Employee resubmitted after rework",
        )
        db.add(audit)

    db.commit()
    db.refresh(goal)

    # Notify manager
    if current_user.manager_id:
        manager = db.query(User).filter(User.id == current_user.manager_id).first()
        if manager:
            background_tasks.add_task(
                email_service.notify_goal_submitted,
                db, manager.email, manager.id, current_user.name, goal.id
            )

    return goal


@router.post("/{goal_id}/approve", response_model=GoalOut)
def approve_goal(
    goal_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.status not in (GoalStatus.submitted, GoalStatus.resubmitted):
        raise HTTPException(status_code=400, detail="Goal is not in submitted state")

    old_status = goal.status
    goal.status = GoalStatus.locked

    # Audit log — written in same transaction; rolls back with approval if it fails
    audit = AuditLog(
        user_id=current_user.id,
        goal_id=goal.id,
        field_changed="status",
        old_value=str(old_status),
        new_value=str(GoalStatus.locked),
        reason=None,
    )
    db.add(audit)
    db.commit()
    db.refresh(goal)

    employee = db.query(User).filter(User.id == goal.employee_id).first()
    if employee:
        background_tasks.add_task(
            email_service.notify_goal_approved,
            db, employee.email, employee.id, goal.id
        )

    return goal


@router.post("/{goal_id}/return", response_model=GoalOut)
def return_goal(
    goal_id: int,
    payload: GoalReturnRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.status not in (GoalStatus.submitted, GoalStatus.resubmitted):
        raise HTTPException(status_code=400, detail="Goal is not in submitted state")

    old_status = goal.status
    goal.status = GoalStatus.returned
    goal.rework_comment = payload.comment

    # Audit log — same transaction as status change
    audit = AuditLog(
        user_id=current_user.id,
        goal_id=goal.id,
        field_changed="status",
        old_value=str(old_status),
        new_value=str(GoalStatus.returned),
        reason=payload.comment,
    )
    db.add(audit)
    db.commit()
    db.refresh(goal)

    employee = db.query(User).filter(User.id == goal.employee_id).first()
    if employee:
        # Fetch active goal-setting cycle deadline for deadline reminder
        from app.models.goal_cycle import GoalCycle, CyclePhase
        from datetime import date as _date
        gs_cycle = (
            db.query(GoalCycle)
            .filter(
                GoalCycle.phase == CyclePhase.goal_setting,
                GoalCycle.is_active == True,
            )
            .first()
        )
        cycle_deadline = None
        if gs_cycle and gs_cycle.window_close:
            days_left = (gs_cycle.window_close - _date.today()).days
            if days_left <= 7:
                cycle_deadline = gs_cycle.window_close.strftime("%d %b %Y")

        background_tasks.add_task(
            email_service.notify_goal_returned,
            db, employee.email, employee.id, goal.id, payload.comment,
            current_user.name, cycle_deadline,
        )

    return goal


@router.post("/{goal_id}/reject", response_model=GoalOut)
def reject_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    old_status = goal.status
    goal.status = GoalStatus.rejected

    # Audit log — same transaction as status change
    audit = AuditLog(
        user_id=current_user.id,
        goal_id=goal.id,
        field_changed="status",
        old_value=str(old_status),
        new_value=str(GoalStatus.rejected),
        reason=None,
    )
    db.add(audit)
    db.commit()
    db.refresh(goal)
    return goal


@router.put("/{goal_id}/manager-edit", response_model=GoalOut)
def manager_edit_goal(
    goal_id: int,
    payload: GoalManagerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """Manager can edit target/weightage inline before approving."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.status not in (GoalStatus.submitted, GoalStatus.resubmitted):
        raise HTTPException(status_code=400, detail="Can only edit submitted goals")

    if payload.weightage is not None:
        if payload.weightage < MIN_WEIGHTAGE:
            raise HTTPException(status_code=400, detail="Minimum weightage is 10%")
        # Re-validate total
        all_goals = db.query(Goal).filter(
            Goal.employee_id == goal.employee_id,
            Goal.status != GoalStatus.rejected,
            Goal.id != goal_id,
        ).all()
        total = sum(g.weightage for g in all_goals) + payload.weightage
        if abs(total - 100.0) > 0.01:
            raise HTTPException(status_code=400, detail=f"Total weightage would be {total}%")
        goal.weightage = payload.weightage

    if payload.target is not None:
        goal.target = payload.target
    if payload.target_date is not None:
        goal.target_date = payload.target_date

    db.commit()
    db.refresh(goal)
    return goal


@router.post("/{goal_id}/unlock", response_model=GoalOut)
def unlock_goal(
    goal_id: int,
    payload: GoalUnlockRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin unlocks a locked goal — mandatory reason required."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.status != GoalStatus.locked:
        raise HTTPException(status_code=400, detail="Goal is not locked")
    if not payload.reason or not payload.reason.strip():
        raise HTTPException(status_code=400, detail="Reason is mandatory for unlocking")

    old_status = goal.status
    goal.status = GoalStatus.approved

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        goal_id=goal.id,
        field_changed="status",
        old_value=old_status,
        new_value=GoalStatus.approved,
        reason=payload.reason,
    )
    db.add(audit)
    db.commit()
    db.refresh(goal)

    # Notify employee and manager
    employee = db.query(User).filter(User.id == goal.employee_id).first()
    if employee:
        manager = db.query(User).filter(User.id == employee.manager_id).first() if employee.manager_id else None
        background_tasks.add_task(
            email_service.notify_goal_unlocked,
            db,
            employee.email, employee.id,
            manager.email if manager else employee.email,
            manager.id if manager else employee.id,
            goal.id, payload.reason
        )

    return goal


def _check_access(goal: Goal, user: User, db: Session):
    if user.role == "employee" and goal.employee_id != user.id:
        raise HTTPException(status_code=403, detail="Not your goal")
    if user.role == "manager":
        team_ids = [u.id for u in db.query(User).filter(User.manager_id == user.id).all()]
        if goal.employee_id not in team_ids and goal.employee_id != user.id:
            raise HTTPException(status_code=403, detail="Not your team member's goal")


@router.get("/{goal_id}/resubmission-diff")
def get_resubmission_diff(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Returns a diff of what changed since the last submission.
    Compares current goal values against the oldest audit_log entry
    for this goal (i.e., the state at first submission).
    Only meaningful when goal.status == RESUBMITTED.
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.status != GoalStatus.resubmitted:
        raise HTTPException(status_code=400, detail="Goal is not in resubmitted state")

    # Fetch audit logs for this goal ordered by time
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.goal_id == goal_id)
        .order_by(AuditLog.changed_at)
        .all()
    )

    changes = [
        {
            "field": log.field_changed,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "changed_at": log.changed_at,
            "reason": log.reason,
        }
        for log in logs
    ]

    return {
        "goal_id": goal_id,
        "status": goal.status,
        "rework_comment": goal.rework_comment,
        "changes": changes,
    }
