"""
Checkin / Achievement window guard.

Provides helpers to:
  - Determine the currently open quarter for a given cycle set.
  - Check whether a specific quarter's window is open today.
  - Return a human-readable "next window opens" message.
"""
from datetime import date
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.goal_cycle import GoalCycle, CyclePhase


# Ordered quarter phases (goal_setting is not a check-in quarter)
QUARTER_PHASES = [CyclePhase.q1, CyclePhase.q2, CyclePhase.q3, CyclePhase.q4]


def get_active_cycle(db: Session) -> Optional[GoalCycle]:
    """Return the currently active cycle (is_active=True)."""
    return db.query(GoalCycle).filter(GoalCycle.is_active == True).first()


def get_open_quarter(db: Session) -> Optional[GoalCycle]:
    """
    Return the GoalCycle row whose window is currently open today.
    Only considers check-in phases (q1–q4), not goal_setting.
    """
    today = date.today()
    return (
        db.query(GoalCycle)
        .filter(
            GoalCycle.phase.in_(QUARTER_PHASES),
            GoalCycle.window_open <= today,
            GoalCycle.window_close >= today,
        )
        .first()
    )


def is_quarter_window_open(db: Session, phase: CyclePhase) -> bool:
    """Return True if the given quarter's window is open today."""
    today = date.today()
    cycle = (
        db.query(GoalCycle)
        .filter(
            GoalCycle.phase == phase,
            GoalCycle.window_open <= today,
            GoalCycle.window_close >= today,
        )
        .first()
    )
    return cycle is not None


def next_window_info(db: Session) -> Tuple[Optional[str], Optional[date]]:
    """
    Return (phase_label, open_date) for the next upcoming check-in window.
    Returns (None, None) if no future windows are scheduled.
    """
    today = date.today()
    upcoming = (
        db.query(GoalCycle)
        .filter(
            GoalCycle.phase.in_(QUARTER_PHASES),
            GoalCycle.window_open > today,
        )
        .order_by(GoalCycle.window_open)
        .first()
    )
    if upcoming:
        return upcoming.phase.upper(), upcoming.window_open
    return None, None


def assert_window_open(db: Session, phase: CyclePhase):
    """
    Raise a ValueError with a descriptive message if the requested
    quarter window is not currently open.  Callers should convert this
    to an HTTPException(400) as appropriate.
    """
    if not is_quarter_window_open(db, phase):
        next_phase, next_date = next_window_info(db)
        if next_phase and next_date:
            msg = (
                f"{phase.upper()} window is not open. "
                f"Next window opens {next_date.strftime('%d %b %Y')} ({next_phase})."
            )
        else:
            msg = f"{phase.upper()} window is not open."
        raise ValueError(msg)
