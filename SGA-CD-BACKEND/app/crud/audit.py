from sqlalchemy.orm import Session
from typing import List

from ..models.academic import AuditLog
from app.schemas.audit import AuditLogCreate

def get_audit_logs_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[AuditLog]:
    """
    Get all audit logs for a specific tenant.
    """
    return (
        db.query(AuditLog)
        .filter(AuditLog.inquilino_id == inquilino_id)
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_audit_log(db: Session, *, obj_in: AuditLogCreate) -> AuditLog:
    """
    Create a new audit log entry.
    This would typically be called by other services/endpoints after an action.
    """
    db_obj = AuditLog(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
