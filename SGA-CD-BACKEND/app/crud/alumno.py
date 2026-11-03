from sqlalchemy.orm import Session
from typing import List

from ..models.user import Alumno
from app.schemas.alumno import AlumnoCreate, AlumnoUpdate

def get(db: Session, alumno_id: int) -> Alumno | None:
    """
    Get a single alumno by ID.
    """
    return db.query(Alumno).filter(Alumno.id == alumno_id).first()

def get_multi_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[Alumno]:
    """
    Get multiple alumnos for a specific tenant.
    """
    return (
        db.query(Alumno)
        .filter(Alumno.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create(db: Session, *, obj_in: AlumnoCreate) -> Alumno:
    """
    Create a new alumno.
    """
    db_obj = Alumno(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, *, db_obj: Alumno, obj_in: AlumnoUpdate) -> Alumno:
    """
    Update an existing alumno.
    """
    # Convert Pydantic model to dict
    update_data = obj_in.model_dump(exclude_unset=True)

    # Update fields in the SQLAlchemy object
    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, *, id: int) -> Alumno | None:
    """
    Delete an alumno.
    """
    obj = db.query(Alumno).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
