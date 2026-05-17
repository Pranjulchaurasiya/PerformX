from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from collections import defaultdict

from app.core.database import get_db
from app.core.deps import require_manager_or_admin, get_current_user
from app.models.user import User
from app.models.goal import Goal, GoalStatus
from app.models.achievement import Achievement
from app.models.goal_cycle import GoalCycle, CyclePhase
from app.models.checkin import Checkin
from app.models.department import Department
from app.models.escalation import EscalationLog, EscalationStatus
from app.services.analytics_cache import cache_get, cache_set

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    cache_key = f"overview_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    if current_user.role == "manager":
        team = db.query(User).filter(User.manager_id == current_user.id).all()
        team_ids = [u.id for u in team]
    else:
        team = db.query(User).filter(User.role == "employee").all()
        team_ids = [u.id for u in team]

    total_goals = db.query(Goal).filter(Goal.employee_id.in_(team_ids)).count()
    locked_goals = db.query(Goal).filter(
        Goal.employee_id.in_(team_ids),
        Goal.status == GoalStatus.locked
    ).count()
    pending_approvals = db.query(Goal).filter(
        Goal.employee_id.in_(team_ids),
        Goal.status.in_(["submitted", "resubmitted"])
    ).count()

    avg_score = db.query(func.avg(Achievement.tracking_score)).join(
        Goal, Achievement.goal_id == Goal.id
    ).filter(Goal.employee_id.in_(team_ids)).scalar()

    result = {
        "total_goals": total_goals,
        "locked_goals": locked_goals,
        "pending_approvals": pending_approvals,
        "avg_tracking_score": round(avg_score or 0, 1),
        "team_size": len(team_ids),
    }
    cache_set(cache_key, result)
    return result


@router.get("/qoq-trends")
def qoq_trends(
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    cache_key = f"qoq_{current_user.id}_{employee_id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    cycles = db.query(GoalCycle).order_by(GoalCycle.id).all()

    if current_user.role == "manager":
        team_ids = [u.id for u in db.query(User).filter(
            User.manager_id == current_user.id).all()]
    else:
        team_ids = [u.id for u in db.query(User).filter(User.role == "employee").all()]

    if employee_id and employee_id in team_ids:
        team_ids = [employee_id]

    result = []
    for cycle in cycles:
        avg = db.query(func.avg(Achievement.tracking_score)).join(
            Goal, Achievement.goal_id == Goal.id
        ).filter(
            Achievement.cycle_id == cycle.id,
            Goal.employee_id.in_(team_ids),
        ).scalar()
        result.append({
            "cycle": cycle.name,
            "phase": cycle.phase,
            "avg_tracking_score": round(avg or 0, 1),
        })

    cache_set(cache_key, result)
    return result


@router.get("/goal-distribution")
def goal_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    cache_key = f"dist_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    if current_user.role == "manager":
        team_ids = [u.id for u in db.query(User).filter(
            User.manager_id == current_user.id).all()]
    else:
        team_ids = [u.id for u in db.query(User).filter(User.role == "employee").all()]

    # By UoM type
    uom_dist = db.query(Goal.uom_type, func.count(Goal.id)).filter(
        Goal.employee_id.in_(team_ids)
    ).group_by(Goal.uom_type).all()

    # By status
    status_dist = db.query(Goal.status, func.count(Goal.id)).filter(
        Goal.employee_id.in_(team_ids)
    ).group_by(Goal.status).all()

    # By thrust area
    from app.models.thrust_area import ThrustArea
    thrust_dist = db.query(ThrustArea.name, func.count(Goal.id)).join(
        Goal, Goal.thrust_area_id == ThrustArea.id
    ).filter(Goal.employee_id.in_(team_ids)).group_by(ThrustArea.name).all()

    result = {
        "by_uom": [{"uom_type": r[0], "count": r[1]} for r in uom_dist],
        "by_status": [{"status": r[0], "count": r[1]} for r in status_dist],
        "by_thrust_area": [{"thrust_area": r[0], "count": r[1]} for r in thrust_dist],
    }
    cache_set(cache_key, result)
    return result


@router.get("/manager-effectiveness")
def manager_effectiveness(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    cache_key = f"mgr_eff_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    managers = db.query(User).filter(User.role == "manager").all()
    result = []

    for mgr in managers:
        team = db.query(User).filter(User.manager_id == mgr.id).all()
        team_ids = [u.id for u in team]
        if not team_ids:
            continue

        total_checkins = db.query(Checkin).filter(
            Checkin.manager_id == mgr.id,
            Checkin.is_completed == True,
        ).count()

        avg_score = db.query(func.avg(Achievement.tracking_score)).join(
            Goal, Achievement.goal_id == Goal.id
        ).filter(Goal.employee_id.in_(team_ids)).scalar()

        result.append({
            "manager_id": mgr.id,
            "manager_name": mgr.name,
            "team_size": len(team_ids),
            "completed_checkins": total_checkins,
            "avg_team_tracking_score": round(avg_score or 0, 1),
        })

    cache_set(cache_key, result)
    return result


@router.get("/department-heatmap")
def department_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    cache_key = f"heatmap_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    departments = db.query(Department).all()
    cycles = db.query(GoalCycle).order_by(GoalCycle.id).all()

    result = []
    for dept in departments:
        dept_users = db.query(User).filter(User.department_id == dept.id).all()
        dept_user_ids = [u.id for u in dept_users]
        if not dept_user_ids:
            continue

        row = {"department": dept.name, "cycles": {}}
        for cycle in cycles:
            total = len(dept_user_ids)
            completed = db.query(Checkin).filter(
                Checkin.employee_id.in_(dept_user_ids),
                Checkin.cycle_id == cycle.id,
                Checkin.is_completed == True,
            ).count()
            row["cycles"][cycle.name] = round((completed / total) * 100, 1) if total else 0

        result.append(row)

    cache_set(cache_key, result)
    return result


# ── Manager Analytics ─────────────────────────────────────────────────────────

@router.get("/manager/qoq-team")
def manager_qoq_team(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Quarter-on-Quarter line chart data: team average tracking score per quarter.
    Scoped to the manager's direct reports.
    """
    cache_key = f"mgr_qoq_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    if current_user.role == "manager":
        team_ids = [u.id for u in db.query(User).filter(
            User.manager_id == current_user.id).all()]
    else:
        team_ids = [u.id for u in db.query(User).filter(User.role == "employee").all()]

    quarters = db.query(GoalCycle).filter(
        GoalCycle.phase.in_([CyclePhase.q1, CyclePhase.q2, CyclePhase.q3, CyclePhase.q4])
    ).order_by(GoalCycle.window_open).all()

    result = []
    for q in quarters:
        avg = db.query(func.avg(Achievement.tracking_score)).join(
            Goal, Achievement.goal_id == Goal.id
        ).filter(
            Achievement.cycle_id == q.id,
            Goal.employee_id.in_(team_ids),
        ).scalar()
        result.append({
            "quarter": q.phase.upper(),
            "cycle_name": q.name,
            "avg_tracking_score": round(avg or 0, 1),
        })

    cache_set(cache_key, result)
    return result


@router.get("/manager/goal-status-breakdown")
def manager_goal_status_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Stacked bar chart: goal status breakdown per team member.
    """
    cache_key = f"mgr_status_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    if current_user.role == "manager":
        team = db.query(User).filter(User.manager_id == current_user.id).all()
    else:
        team = db.query(User).filter(User.role == "employee").all()

    result = []
    for emp in team:
        status_counts = db.query(Goal.status, func.count(Goal.id)).filter(
            Goal.employee_id == emp.id
        ).group_by(Goal.status).all()
        result.append({
            "employee_id": emp.id,
            "employee_name": emp.name,
            "status_breakdown": {s: c for s, c in status_counts},
        })

    cache_set(cache_key, result)
    return result


@router.get("/manager/checkin-completion")
def manager_checkin_completion(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Check-in completion rate for the manager's team across all quarters.
    """
    cache_key = f"mgr_checkin_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    if current_user.role == "manager":
        team = db.query(User).filter(User.manager_id == current_user.id).all()
    else:
        team = db.query(User).filter(User.role == "employee").all()

    team_ids = [u.id for u in team]
    if not team_ids:
        return {"completion_rate": 0, "completed": 0, "total": 0, "by_quarter": []}

    quarters = db.query(GoalCycle).filter(
        GoalCycle.phase.in_([CyclePhase.q1, CyclePhase.q2, CyclePhase.q3, CyclePhase.q4])
    ).order_by(GoalCycle.window_open).all()

    by_quarter = []
    total_possible = 0
    total_completed = 0

    for q in quarters:
        completed = db.query(Checkin).filter(
            Checkin.employee_id.in_(team_ids),
            Checkin.cycle_id == q.id,
            Checkin.is_completed == True,
        ).count()
        possible = len(team_ids)
        total_possible += possible
        total_completed += completed
        by_quarter.append({
            "quarter": q.phase.upper(),
            "cycle_name": q.name,
            "completed": completed,
            "total": possible,
            "rate": round((completed / possible) * 100, 1) if possible else 0,
        })

    overall_rate = round((total_completed / total_possible) * 100, 1) if total_possible else 0
    result = {
        "completion_rate": overall_rate,
        "completed": total_completed,
        "total": total_possible,
        "by_quarter": by_quarter,
    }
    cache_set(cache_key, result)
    return result


@router.get("/manager/employee-progress")
def manager_employee_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Individual employee cards: current cycle progress %.
    """
    cache_key = f"mgr_emp_prog_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    if current_user.role == "manager":
        team = db.query(User).filter(User.manager_id == current_user.id).all()
    else:
        team = db.query(User).filter(User.role == "employee").all()

    # Use the most recent active quarter
    from datetime import date
    today = date.today()
    active_quarter = (
        db.query(GoalCycle)
        .filter(
            GoalCycle.phase.in_([CyclePhase.q1, CyclePhase.q2, CyclePhase.q3, CyclePhase.q4]),
            GoalCycle.window_open <= today,
            GoalCycle.window_close >= today,
        )
        .first()
    )

    result = []
    for emp in team:
        goals = db.query(Goal).filter(
            Goal.employee_id == emp.id,
            Goal.status == GoalStatus.locked,
        ).all()
        goal_ids = [g.id for g in goals]

        avg_score = None
        if goal_ids and active_quarter:
            avg_score = db.query(func.avg(Achievement.tracking_score)).filter(
                Achievement.goal_id.in_(goal_ids),
                Achievement.cycle_id == active_quarter.id,
            ).scalar()

        result.append({
            "employee_id": emp.id,
            "employee_name": emp.name,
            "total_goals": len(goals),
            "current_quarter": active_quarter.phase.upper() if active_quarter else None,
            "avg_tracking_score": round(avg_score or 0, 1),
        })

    cache_set(cache_key, result)
    return result


# ── Admin Analytics ───────────────────────────────────────────────────────────

@router.get("/admin/org-qoq-trends")
def admin_org_qoq_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Org-wide QoQ achievement trends broken down by department.
    Line chart data: department × quarter → avg tracking score.
    """
    cache_key = f"admin_qoq_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    departments = db.query(Department).all()
    quarters = db.query(GoalCycle).filter(
        GoalCycle.phase.in_([CyclePhase.q1, CyclePhase.q2, CyclePhase.q3, CyclePhase.q4])
    ).order_by(GoalCycle.window_open).all()

    result = []
    for dept in departments:
        dept_users = db.query(User).filter(User.department_id == dept.id).all()
        dept_user_ids = [u.id for u in dept_users]
        if not dept_user_ids:
            continue

        series = []
        for q in quarters:
            avg = db.query(func.avg(Achievement.tracking_score)).join(
                Goal, Achievement.goal_id == Goal.id
            ).filter(
                Achievement.cycle_id == q.id,
                Goal.employee_id.in_(dept_user_ids),
            ).scalar()
            series.append({
                "quarter": q.phase.upper(),
                "cycle_name": q.name,
                "avg_tracking_score": round(avg or 0, 1),
            })

        result.append({
            "department_id": dept.id,
            "department": dept.name,
            "series": series,
        })

    cache_set(cache_key, result)
    return result


@router.get("/admin/department-completion-heatmap")
def admin_department_completion_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Heatmap: rows=departments, columns=Q1–Q4, cell=completion %.
    Color thresholds: green >80%, amber 50–80%, red <50%.
    """
    cache_key = f"admin_heatmap_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    departments = db.query(Department).all()
    quarters = db.query(GoalCycle).filter(
        GoalCycle.phase.in_([CyclePhase.q1, CyclePhase.q2, CyclePhase.q3, CyclePhase.q4])
    ).order_by(GoalCycle.window_open).all()

    result = []
    for dept in departments:
        dept_users = db.query(User).filter(User.department_id == dept.id).all()
        dept_user_ids = [u.id for u in dept_users]
        if not dept_user_ids:
            continue

        cells = []
        for q in quarters:
            total = len(dept_user_ids)
            completed = db.query(Checkin).filter(
                Checkin.employee_id.in_(dept_user_ids),
                Checkin.cycle_id == q.id,
                Checkin.is_completed == True,
            ).count()
            pct = round((completed / total) * 100, 1) if total else 0
            color = "green" if pct >= 80 else ("amber" if pct >= 50 else "red")
            cells.append({
                "quarter": q.phase.upper(),
                "cycle_name": q.name,
                "completion_pct": pct,
                "color": color,
            })

        result.append({
            "department_id": dept.id,
            "department": dept.name,
            "cells": cells,
        })

    cache_set(cache_key, result)
    return result


@router.get("/admin/goal-distribution")
def admin_goal_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Goal distribution charts:
      - By Thrust Area (donut)
      - By UoM Type (bar)
      - By Status (stacked bar)
    """
    cache_key = f"admin_dist_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    from app.models.thrust_area import ThrustArea

    by_thrust = db.query(ThrustArea.name, func.count(Goal.id)).join(
        Goal, Goal.thrust_area_id == ThrustArea.id
    ).group_by(ThrustArea.name).all()

    by_uom = db.query(Goal.uom_type, func.count(Goal.id)).group_by(Goal.uom_type).all()

    by_status = db.query(Goal.status, func.count(Goal.id)).group_by(Goal.status).all()

    result = {
        "by_thrust_area": [{"thrust_area": r[0], "count": r[1]} for r in by_thrust],
        "by_uom_type": [{"uom_type": r[0], "count": r[1]} for r in by_uom],
        "by_status": [{"status": r[0], "count": r[1]} for r in by_status],
    }
    cache_set(cache_key, result)
    return result


@router.get("/admin/manager-effectiveness")
def admin_manager_effectiveness(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """
    Manager effectiveness table:
    Manager Name | Team Size | Check-in Completion % | Avg Team Score | Escalations Triggered
    Sortable by each column (sorting done client-side; all data returned).
    """
    cache_key = f"admin_mgr_eff_{current_user.id}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    managers = db.query(User).filter(User.role == "manager").all()
    result = []

    for mgr in managers:
        team = db.query(User).filter(User.manager_id == mgr.id).all()
        team_ids = [u.id for u in team]
        if not team_ids:
            continue

        # Check-in completion across all quarters
        quarters = db.query(GoalCycle).filter(
            GoalCycle.phase.in_([CyclePhase.q1, CyclePhase.q2, CyclePhase.q3, CyclePhase.q4])
        ).all()
        total_possible = len(team_ids) * len(quarters)
        total_completed = db.query(Checkin).filter(
            Checkin.manager_id == mgr.id,
            Checkin.is_completed == True,
        ).count()
        checkin_rate = round((total_completed / total_possible) * 100, 1) if total_possible else 0

        avg_score = db.query(func.avg(Achievement.tracking_score)).join(
            Goal, Achievement.goal_id == Goal.id
        ).filter(Goal.employee_id.in_(team_ids)).scalar()

        escalations_triggered = db.query(EscalationLog).filter(
            EscalationLog.target_user_id.in_(team_ids),
        ).count()

        result.append({
            "manager_id": mgr.id,
            "manager_name": mgr.name,
            "team_size": len(team_ids),
            "checkin_completion_pct": checkin_rate,
            "avg_team_tracking_score": round(avg_score or 0, 1),
            "escalations_triggered": escalations_triggered,
        })

    cache_set(cache_key, result)
    return result
