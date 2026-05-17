"""
Progress Score Engine — computes Tracking Score for each UoM type.
All scores are labelled "Tracking Score" — never "Rating".

Timeline scoring (3-case):
  Case 1 — Completed on or before deadline:        score = 100
  Case 2 — In progress (not yet completed):        score = min(100, elapsed_ms / total_ms * 100)
  Case 3 — Completed after deadline:               score = max(0, 100 - days_late * penalty_pct_per_day)
"""
from datetime import date
from typing import Optional
from app.models.goal import UoMType

# Default penalty factor: 5% per day late.
# Overridden per-cycle via GoalCycle.penalty_factor (stored as 0.05 = 5%).
DEFAULT_PENALTY_FACTOR = 0.05  # fraction, not percentage


def compute_tracking_score(
    uom_type: UoMType,
    target: Optional[float],
    achievement: Optional[float],
    target_date: Optional[date] = None,
    actual_date: Optional[date] = None,
    start_date: Optional[date] = None,
    penalty_factor: Optional[float] = None,  # fraction e.g. 0.05 = 5% per day
) -> Optional[float]:
    """
    Returns tracking score as a float 0–100 (or higher for overachievement on min/max).
    Returns None if insufficient data.

    Args:
        uom_type:       UoM type of the goal.
        target:         Numeric target (for min/max/zero).
        achievement:    Actual numeric achievement (for min/max/zero).
        target_date:    Deadline date (for timeline).
        actual_date:    Date of completion (for timeline, if completed).
        start_date:     Goal start date (for in-progress timeline calculation).
        penalty_factor: Fraction deducted per day late (default 0.05 = 5%).
    """
    if penalty_factor is None:
        penalty_factor = DEFAULT_PENALTY_FACTOR

    # Convert fraction to percentage points per day (e.g. 0.05 → 5.0)
    penalty_pct_per_day = penalty_factor * 100.0

    try:
        if uom_type == UoMType.min:
            # Higher is better: achievement / target * 100
            if target and target > 0 and achievement is not None:
                return round((achievement / target) * 100, 2)

        elif uom_type == UoMType.max:
            # Lower is better: target / achievement * 100
            if achievement and achievement > 0 and target is not None:
                return round((target / achievement) * 100, 2)

        elif uom_type == UoMType.zero:
            # Zero = success
            if achievement is not None:
                return 100.0 if achievement == 0 else 0.0

        elif uom_type == UoMType.timeline:
            today = date.today()

            if actual_date is not None and target_date is not None:
                # ── Case 1: Completed on or before deadline ──────────────────
                if actual_date <= target_date:
                    return 100.0

                # ── Case 3: Completed after deadline ─────────────────────────
                days_late = (actual_date - target_date).days
                penalty = days_late * penalty_pct_per_day
                return max(0.0, round(100.0 - penalty, 2))

            elif target_date is not None:
                # ── Case 2: In progress (not yet completed) ───────────────────
                if start_date is None:
                    # No start date available — use today as a fallback reference
                    # If already past deadline, treat as 0% (overdue, not completed)
                    if today > target_date:
                        days_late = (today - target_date).days
                        penalty = days_late * penalty_pct_per_day
                        return max(0.0, round(100.0 - penalty, 2))
                    return 50.0  # Unknown progress, not yet due

                total_ms = (target_date - start_date).days
                if total_ms <= 0:
                    return 0.0
                elapsed_ms = (today - start_date).days
                return round(min(100.0, (elapsed_ms / total_ms) * 100), 2)

    except (ZeroDivisionError, TypeError):
        pass

    return None
