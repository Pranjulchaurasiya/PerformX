from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogOut

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def list_audit_logs(
    goal_id: Optional[int] = None,
    user_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(AuditLog).options(joinedload(AuditLog.user))

    if goal_id:
        query = query.filter(AuditLog.goal_id == goal_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    query = query.order_by(AuditLog.changed_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for log in items:
        out = AuditLogOut.model_validate(log)
        out.user_name = log.user.name if log.user else None
        result.append(out)

    return {"items": result, "total": total, "page": page, "page_size": page_size}
