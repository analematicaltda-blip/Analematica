from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models import user as user_model
from app.models.academic import Notificacion

router = APIRouter()

@router.get("/me/", response_model=List[schemas.Notificacion])
def read_my_notificaciones(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve notifications for the current logged-in user.
    """
    notificaciones = crud.notificacion.get_notificaciones_by_user(
        db, usuario_id=current_user.id, skip=skip, limit=limit
    )
    return notificaciones

@router.put("/{notificacion_id}/read", response_model=schemas.Notificacion)
def mark_notification_as_read(
    notificacion_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark a notification as read with strict ownership validation (ABAC).
    """
    notif = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if not notif or notif.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notif.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this tenant's notification")

    db_notification = crud.notificacion.mark_as_read(db, notificacion_id=notificacion_id)
    return db_notification
