from sqlalchemy.orm import Session
from typing import List

from ..models.communication import (
    ChatConversacion, ChatParticipante, ChatMensaje,
    ForoClase, ForoHilo, ForoPublicacion
)
from app.schemas.communication import (
    ChatConversacionCreate, ChatMensajeCreate,
    ForoClaseCreate, ForoHiloCreate, ForoPublicacionCreate
)
from datetime import datetime

# --- CRUD for Chat ---

def create_conversacion(db: Session, *, obj_in: ChatConversacionCreate) -> ChatConversacion:
    db_conv = ChatConversacion(
        inquilino_id=obj_in.inquilino_id,
        fecha_creacion=datetime.utcnow()
    )
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)

    # Add participants
    for user_id in obj_in.participante_ids:
        db_participant = ChatParticipante(conversacion_id=db_conv.id, usuario_id=user_id)
        db.add(db_participant)
    db.commit()

    return db_conv

def create_mensaje(db: Session, *, obj_in: ChatMensajeCreate) -> ChatMensaje:
    db_msg = ChatMensaje(
        **obj_in.model_dump(),
        timestamp=datetime.utcnow(),
        leido=False
    )
    db.add(db_msg)
    # Also update the conversation's last message timestamp
    db.query(ChatConversacion).filter(ChatConversacion.id == obj_in.conversacion_id).update(
        {"ultimo_mensaje_timestamp": datetime.utcnow()}
    )
    db.commit()
    db.refresh(db_msg)
    return db_msg

# --- CRUD for Foros ---

def create_foro(db: Session, *, obj_in: ForoClaseCreate) -> ForoClase:
    db_obj = ForoClase(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_hilo(db: Session, *, obj_in: ForoHiloCreate) -> ForoHilo:
    db_obj = ForoHilo(**obj_in.model_dump(), timestamp=datetime.utcnow())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_publicacion(db: Session, *, obj_in: ForoPublicacionCreate) -> ForoPublicacion:
    db_obj = ForoPublicacion(**obj_in.model_dump(), timestamp=datetime.utcnow())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
