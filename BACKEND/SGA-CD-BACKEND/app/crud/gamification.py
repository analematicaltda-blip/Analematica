from sqlalchemy.orm import Session
from typing import List

from ..models.gamification import (
    GamificacionAccion, GamificacionPuntosLog, GamificacionMedalla, GamificacionMedallaObtenida,
    GamificacionMision, GamificacionMercadoItem
)
from app.schemas.gamification import (
    GamificacionAccionCreate, GamificacionPuntosLogCreate, GamificacionMedallaCreate,
    GamificacionMisionCreate, GamificacionMercadoItemCreate
)

# --- CRUD for GamificacionAccion ---

def get_accion(db: Session, accion_id: int) -> GamificacionAccion | None:
    return db.query(GamificacionAccion).filter(GamificacionAccion.id == accion_id).first()

def get_acciones_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[GamificacionAccion]:
    return (
        db.query(GamificacionAccion)
        .filter(GamificacionAccion.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_accion(db: Session, *, obj_in: GamificacionAccionCreate) -> GamificacionAccion:
    db_obj = GamificacionAccion(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- CRUD for GamificacionPuntosLog ---

def create_puntos_log(db: Session, *, obj_in: GamificacionPuntosLogCreate) -> GamificacionPuntosLog:
    db_obj = GamificacionPuntosLog(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- CRUD for GamificacionMedalla ---

def get_medalla(db: Session, medalla_id: int) -> GamificacionMedalla | None:
    return db.query(GamificacionMedalla).filter(GamificacionMedalla.id == medalla_id).first()

def create_medalla(db: Session, *, obj_in: GamificacionMedallaCreate) -> GamificacionMedalla:
    db_obj = GamificacionMedalla(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- CRUD for GamificacionMision ---

def get_mision(db: Session, mision_id: int) -> GamificacionMision | None:
    return db.query(GamificacionMision).filter(GamificacionMision.id == mision_id).first()

def get_misiones_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[GamificacionMision]:
    return (
        db.query(GamificacionMision)
        .filter(GamificacionMision.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_mision(db: Session, *, obj_in: GamificacionMisionCreate) -> GamificacionMision:
    db_obj = GamificacionMision(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- CRUD for GamificacionMercadoItem ---

def get_mercado_item(db: Session, item_id: int) -> GamificacionMercadoItem | None:
    return db.query(GamificacionMercadoItem).filter(GamificacionMercadoItem.id == item_id).first()

def get_mercado_items_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[GamificacionMercadoItem]:
    return (
        db.query(GamificacionMercadoItem)
        .filter(GamificacionMercadoItem.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_mercado_item(db: Session, *, obj_in: GamificacionMercadoItemCreate) -> GamificacionMercadoItem:
    db_obj = GamificacionMercadoItem(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Additional business logic functions will be needed here, e.g.:
# - A function to handle a student purchasing an item, which would
#   deduct points and create a GamificacionCompraLog entry.
# - A function to check a student's progress on a mission.
