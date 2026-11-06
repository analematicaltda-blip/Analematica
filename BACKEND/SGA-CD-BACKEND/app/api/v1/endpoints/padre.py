from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.models import user as user_model

router = APIRouter()

@router.get("/hijos", response_model=List[schemas.User])
def get_my_hijos(
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
):
    """
    Retrieve the children of the current user (padre_acudiente).
    Ensures children belong strictly to the same tenant as the parent.
    """
    # Use the roles from the token attached by the dependency
    if "padre_acudiente" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Required role: padre_acudiente",
        )

    # Filter children strictly by tenant match
    hijos_models = [hijo for hijo in current_user.hijos if hijo.inquilino_id == current_user.inquilino_id]
    hijos_schemas = []
    for hijo in hijos_models:
        # Fetch roles for each child
        query = "SELECT r.nombre FROM roles r JOIN user_roles ur ON r.id = ur.role_id WHERE ur.user_id = :user_id"
        from sqlalchemy import text
        roles_result = db.execute(text(query), {"user_id": hijo.id}).fetchall()
        hijo_roles = [row[0] for row in roles_result]

        hijo_schema = schemas.User(
            id=hijo.id,
            email=hijo.correo,
            nombre_completo=hijo.nombre_completo,
            activo=hijo.activo,
            roles=hijo_roles
        )
        hijos_schemas.append(hijo_schema)

    return hijos_schemas
