"""
Escalation router.

Provides:
  - Admin: full CRUD on escalation rules + view all logs.
  - Manager: GET /escalations/my-team — widget data scoped to direct reports.
  - Cron: POST /escalations/run — internal endpoint called by the cron job.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager_or_admin, require_admin
from app.core.config import settings
from app.models.user import User
from app.models.goal import Goal, GoalStatus
from app.models.goal_cycle import GoalCycle, CyclePhase
from app.models.escalation import EscalationRule, EscalationLog, EscalationStatus
from app.models.achievement import Achievement
from app.schemas.escalation import (
    EscalationRuleCreate, EscalationRuleUpdate, EscalationRuleOut, EscalationLogOut
)
from app.services import email_service
from app.services.window_guard import get_open_quarter

router = APIRouter(prefix="/escalations", tags=["escalations"])


# ── Manager widget ────────────────────────────────────────────────────────────

@router.get("/my-team")
def manager_team_escalations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Returns open escalation logs for the manager's direct reports.
    Used by the Manager Dashboard escalation widget.
    """
    if current_user.role == "manager":
        team = db.query(User).filter(User.manager_id == current_user.id).all()
        team_ids = [u.id for u in team]
    else:
        # Admin sees all
        team = db.query(User).filter(User.role == "employee").all()
        team_ids = [u.id for u in team]

    if not team_ids:
        return {"items": [], "open_count": 0}

    logs = (
        db.query(EscalationLog)
        .filter(
            EscalationLog.target_user_id.in_(team_ids),
            EscalationLog.status == EscalationStatus.open,
        )
        .order_by(EscalationLog.triggered_at.desc())
        .all()
    )

    today = datetime.utcnow()
    result = []
    for log in logs:
        emp = db.query(User).filter(User.id == log.target_user_id).first()
        rule = db.query(EscalationRule).filter(EscalationRule.id == log.rule_id).first()
        days_overdue = (today - log.triggered_at).days if log.triggered_at else 0
        result.append({
            "escalation_id": log.id,
            "employee_id": log.target_user_id,
            "employee_name": emp.name if emp else "Unknown",
            "rule_type": rule.trigger_event if rule else "unknown",
            "rule_name": rule.rule_name if rule else "Unknown Rule",
            "days_overdue": days_overdue,
            "level_reached": log.step_reached,
            "triggered_at": log.triggered_at,
            "status": log.status,
        })

    return {"items": result, "open_count": len(result)}


# ── Admin: Escalation Rules CRUD ──────────────────────────────────────────────

@router.get("/rules", response_model=List[EscalationRuleOut])
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return db.query(EscalationRule).all()


@router.post("/rules", response_model=EscalationRuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    payload: EscalationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rule = EscalationRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/rules/{rule_id}", response_model=EscalationRuleOut)
def update_rule(
    rule_id: int,
    payload: EscalationRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rule = db.query(EscalationRule).filter(EscalationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


# ── Admin: Escalation Logs ────────────────────────────────────────────────────

@router.get("/logs")
def list_logs(
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(EscalationLog).order_by(EscalationLog.triggered_at.desc())
    if status_filter:
        query = query.filter(EscalationLog.status == status_filter)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for log in items:
        emp = db.query(User).filter(User.id == log.target_user_id).first()
        rule = db.query(EscalationRule).filter(EscalationRule.id == log.rule_id).first()
        result.append({
            "id": log.id,
            "employee_id": log.target_user_id,
            "employee_name": emp.name if emp else "Unknown",
            "rule_type": rule.trigger_event if rule else "unknown",
            "rule_name": rule.rule_name if rule else "Unknown Rule",
            "step_reached": log.step_reached,
            "triggered_at": log.triggered_at,
            "resolved_at": log.resolved_at,
            "status": log.status,
        })

    return {"items": result, "total": total, "page": page, "page_size": page_size}


@router.post("/logs/{log_id}/resolve", status_code=status.HTTP_200_OK)
def resolve_escalation(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    log = db.query(EscalationLog).filter(EscalationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Escalation log not found")
    log.status = EscalationStatus.resolved
    log.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": "Escalation resolved"}


# ── Cron endpoint (called by Vercel Cron) ────────────────────────────────────

@router.post("/run", include_in_schema=False)
async def run_escalations(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Protected cron endpoint.  Must be called with header:
      Authorization: Bearer <CRON_SECRET>
    Runs all active escalation rules and inserts/escalates logs.
    """
    auth_header = request.headers.get("authorization", "")
    expected = f"Bearer {settings.CRON_SECRET}"
    if not settings.CRON_SECRET or auth_header != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

    triggered = 0
    escalated = 0
    today = datetime.utcnow()

    active_rules = db.query(EscalationRule).filter(EscalationRule.is_active == True).all()
    open_quarter = get_open_quarter(db)

    for rule in active_rules:
        event = rule.trigger_event

        # ── GOAL_NOT_SUBMITTED ────────────────────────────────────────────────
        if event == "GOAL_NOT_SUBMITTED":
            # Find goal_setting cycle
            gs_cycle = (
                db.query(GoalCycle)
                .filter(GoalCycle.phase == CyclePhase.goal_setting, GoalCycle.is_active == True)
                .first()
            )
            if not gs_cycle or not gs_cycle.window_open:
                continue
            threshold_date = gs_cycle.window_open + timedelta(days=rule.threshold_days)
            if today.date() < threshold_date:
                continue

            # Employees with no submitted/approved goals
            all_employees = db.query(User).filter(User.role == "employee").all()
            for emp in all_employees:
                has_submitted = db.query(Goal).filter(
                    Goal.employee_id == emp.id,
                    Goal.status.in_([
                        GoalStatus.submitted, GoalStatus.resubmitted,
                        GoalStatus.approved, GoalStatus.locked,
                    ]),
                ).first()
                if not has_submitted:
                    triggered += _trigger_or_escalate(
                        db, rule, emp, today, event
                    )

        # ── APPROVAL_PENDING ──────────────────────────────────────────────────
        elif event == "APPROVAL_PENDING":
            threshold_date = today - timedelta(days=rule.threshold_days)
            pending_goals = db.query(Goal).filter(
                Goal.status.in_([GoalStatus.submitted, GoalStatus.resubmitted]),
                Goal.updated_at <= threshold_date,
            ).all()
            seen_employees = set()
            for goal in pending_goals:
                if goal.employee_id in seen_employees:
                    continue
                seen_employees.add(goal.employee_id)
                emp = db.query(User).filter(User.id == goal.employee_id).first()
                if emp:
                    triggered += _trigger_or_escalate(db, rule, emp, today, event)

        # ── CHECKIN_OVERDUE ───────────────────────────────────────────────────
        elif event == "CHECKIN_OVERDUE":
            if not open_quarter or not open_quarter.window_open:
                continue
            threshold_date = open_quarter.window_open + timedelta(days=rule.threshold_days)
            if today.date() < threshold_date:
                continue

            all_employees = db.query(User).filter(User.role == "employee").all()
            for emp in all_employees:
                has_checkin = db.query(Achievement).join(
                    Goal, Achievement.goal_id == Goal.id
                ).filter(
                    Goal.employee_id == emp.id,
                    Achievement.cycle_id == open_quarter.id,
                ).first()
                if not has_checkin:
                    triggered += _trigger_or_escalate(db, rule, emp, today, event)

    db.commit()
    return {"triggered": triggered, "escalated": escalated, "ran_at": today.isoformat()}


def _trigger_or_escalate(
    db: Session,
    rule: EscalationRule,
    emp: User,
    today: datetime,
    event: str,
) -> int:
    """
    Insert a new escalation log or escalate an existing open one.
    Returns 1 if an action was taken, 0 otherwise.
    """
    existing = (
        db.query(EscalationLog)
        .filter(
            EscalationLog.rule_id == rule.id,
            EscalationLog.target_user_id == emp.id,
            EscalationLog.status == EscalationStatus.open,
        )
        .first()
    )

    if existing:
        # Check if we should escalate to next level
        days_since = (today - existing.triggered_at).days
        if existing.step_reached == 1 and days_since >= rule.step1_delay_days:
            existing.step_reached = 2
            _send_escalation_email(db, emp, rule, 2, event)
            return 1
        elif existing.step_reached == 2 and days_since >= (rule.step1_delay_days + rule.step2_delay_days):
            existing.step_reached = 3
            _send_escalation_email(db, emp, rule, 3, event)
            return 1
        return 0
    else:
        # New escalation
        log = EscalationLog(
            rule_id=rule.id,
            target_user_id=emp.id,
            step_reached=1,
            triggered_at=today,
            status=EscalationStatus.open,
        )
        db.add(log)
        _send_escalation_email(db, emp, rule, 1, event)
        return 1


def _send_escalation_email(
    db: Session,
    emp: User,
    rule: EscalationRule,
    level: int,
    event: str,
):
    """Send escalation notification based on level."""
    if level == 1:
        # Notify employee and their manager
        recipients = [(emp.id, emp.email, "employee")]
        if emp.manager_id:
            mgr = db.query(User).filter(User.id == emp.manager_id).first()
            if mgr:
                recipients.append((mgr.id, mgr.email, "manager"))
    elif level == 2:
        # Skip-level / HR
        recipients = []
        if emp.manager_id:
            mgr = db.query(User).filter(User.id == emp.manager_id).first()
            if mgr and mgr.manager_id:
                skip = db.query(User).filter(User.id == mgr.manager_id).first()
                if skip:
                    recipients.append((skip.id, skip.email, "skip-level"))
    else:
        # Level 3 — HR/Admin
        admins = db.query(User).filter(User.role == "admin").all()
        recipients = [(a.id, a.email, "admin") for a in admins]

    subject = f"[PerformX Escalation L{level}] {rule.rule_name} — {emp.name}"
    body = (
        f"<p>This is an automated escalation notification (Level {level}).</p>"
        f"<p><strong>Employee:</strong> {emp.name} ({emp.email})</p>"
        f"<p><strong>Rule:</strong> {rule.rule_name}</p>"
        f"<p><strong>Event:</strong> {event}</p>"
        f"<p>Please take action in PerformX.</p>"
        f'<a href="{settings.APP_BASE_URL}" class="btn">Open PerformX</a>'
    )

    for uid, email, role_label in recipients:
        email_service.send_email_background(
            db, uid, email, f"escalation_l{level}", subject, body
        )
