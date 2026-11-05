from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models import user as user_model
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.AuditLog])
def read_audit_logs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "admin_general"]))
) -> Any:
    """
    Retrieve audit logs for the current user's tenant.
    This is restricted to users with 'admin_empresa' or 'admin_general' roles.
    """
    logs = crud.audit.get_audit_logs_by_tenant(
        db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit
    )
    return logs
