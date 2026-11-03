from sqlalchemy.orm import Session
from typing import List

from ..models.academic import Evento, EventoParticipante
from app.schemas.evento import EventoCreate, EventoUpdate, EventoParticipanteCreate

# --- CRUD for Evento ---

def get_evento(db: Session, evento_id: int) -> Evento | None:
    return db.query(Evento).filter(Evento.id == evento_id).first()

def get_eventos_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[Evento]:
    return (
        db.query(Evento)
        .filter(Evento.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_evento(db: Session, *, obj_in: EventoCreate) -> Evento:
    data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()
    db_obj = Evento(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_eventos_by_area_ids(db: Session, *, area_ids: List[int], skip: int = 0, limit: int = 100) -> List[Evento]:
    """
    Retrieve all eventos (events) for a specific list of area IDs.
    """
    return (
        db.query(Evento)
        .filter(Evento.area_id.in_(area_ids))
        .offset(skip)
        .limit(limit)
        .all()
    )

# --- CRUD for EventoParticipante ---

def add_participante_to_evento(db: Session, *, obj_in: EventoParticipanteCreate) -> EventoParticipante:
    data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()
    db_obj = EventoParticipante(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
