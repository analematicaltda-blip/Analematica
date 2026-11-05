from sqlalchemy.orm import Session
from typing import List

from ..models.academic import Notificacion
from app.schemas.notificacion import NotificacionCreate

def get_notificaciones_by_user(
    db: Session, *, usuario_id: int, skip: int = 0, limit: int = 100
) -> List[Notificacion]:
    """
    Get all notifications for a specific user.
    """
    return (
        db.query(Notificacion)
        .filter(Notificacion.usuario_id == usuario_id)
        .order_by(Notificacion.fecha_hora.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_notificacion(db: Session, *, obj_in: NotificacionCreate) -> Notificacion:
    """
    Create a new notification.
    """
    db_obj = Notificacion(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def mark_as_read(db: Session, *, notificacion_id: int) -> Notificacion | None:
    """
    Mark a specific notification as read.
    """
    db_obj = db.query(Notificacion).get(notificacion_id)
    if db_obj:
        db_obj.leido = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return db_obj
