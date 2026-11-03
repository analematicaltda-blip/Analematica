from sqlalchemy.orm import Session
from typing import List

from app.models.academic import Inscripcion, Asistencia
from app.models.user import Usuario
from app.schemas.inscripcion_asistencia import InscripcionCreate, AsistenciaCreate

# --- CRUD for Inscripcion ---

def get_inscripciones_by_clase(db: Session, clase_id: int) -> List[Inscripcion]:
    return db.query(Inscripcion).filter(Inscripcion.clase_id == clase_id).all()

def create_inscripcion(db: Session, *, obj_in: InscripcionCreate) -> Inscripcion:
    db_obj = Inscripcion(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_alumnos_by_clase(db: Session, *, clase_id: int) -> List[Usuario]:
    """
    Retrieve all student users enrolled in a specific clase (course).
    """
    return (
        db.query(Usuario)
        .join(Inscripcion, Usuario.id == Inscripcion.alumno_id)
        .filter(Inscripcion.clase_id == clase_id)
        .all()
    )

# --- CRUD for Asistencia ---

def get_asistencias_by_clase(db: Session, clase_id: int) -> List[Asistencia]:
    return db.query(Asistencia).filter(Asistencia.clase_id == clase_id).all()

def create_asistencia(db: Session, *, obj_in: AsistenciaCreate) -> Asistencia:
    db_obj = Asistencia(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
