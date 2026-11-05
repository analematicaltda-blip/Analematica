from sqlalchemy.orm import Session
from typing import List

from ..models.inventory import Elemento, Prestamo
from app.schemas.inventory import ElementoCreate, ElementoUpdate, PrestamoCreate, PrestamoUpdate

# --- CRUD for Elemento ---

def get_elemento(db: Session, elemento_id: int) -> Elemento | None:
    return db.query(Elemento).filter(Elemento.id == elemento_id).first()

def get_elementos_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[Elemento]:
    return (
        db.query(Elemento)
        .filter(Elemento.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_elemento(db: Session, *, obj_in: ElementoCreate) -> Elemento:
    db_obj = Elemento(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_elemento(db: Session, *, db_obj: Elemento, obj_in: ElementoUpdate) -> Elemento:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- CRUD for Prestamo ---

def get_prestamo(db: Session, prestamo_id: int) -> Prestamo | None:
    return db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()

def get_prestamos_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[Prestamo]:
    return (
        db.query(Prestamo)
        .filter(Prestamo.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_prestamo(db: Session, *, obj_in: PrestamoCreate) -> Prestamo:
    db_obj = Prestamo(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_prestamo(db: Session, *, db_obj: Prestamo, obj_in: PrestamoUpdate) -> Prestamo:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
