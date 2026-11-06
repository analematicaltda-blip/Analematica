from sqlalchemy.orm import Session
from typing import List

from ..models.academic import ProcesoFormacion, Clase
from app.schemas.clase import ProcesoFormacionCreate, ProcesoFormacionUpdate, ClaseCreate, ClaseUpdate

# --- CRUD for ProcesoFormacion ---

def get_proceso(db: Session, proceso_id: int) -> ProcesoFormacion | None:
    return db.query(ProcesoFormacion).filter(ProcesoFormacion.id == proceso_id).first()

def get_procesos_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[ProcesoFormacion]:
    return (
        db.query(ProcesoFormacion)
        .filter(ProcesoFormacion.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_proceso(db: Session, *, obj_in: ProcesoFormacionCreate) -> ProcesoFormacion:
    db_obj = ProcesoFormacion(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_clases_by_profesor(db: Session, *, profesor_id: int, skip: int = 0, limit: int = 100) -> List[Clase]:
    """
    Retrieve all clases (courses) for a specific profesor.
    """
    return (
        db.query(Clase)
        .filter(Clase.profesor_id == profesor_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def update_proceso(db: Session, *, db_obj: ProcesoFormacion, obj_in: ProcesoFormacionUpdate) -> ProcesoFormacion:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- CRUD for Clase ---

def get_clase(db: Session, clase_id: int) -> Clase | None:
    return db.query(Clase).filter(Clase.id == clase_id).first()

def get_clases_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[Clase]:
    return (
        db.query(Clase)
        .filter(Clase.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_clase(db: Session, *, obj_in: ClaseCreate) -> Clase:
    db_obj = Clase(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_clase(db: Session, *, db_obj: Clase, obj_in: ClaseUpdate) -> Clase:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
