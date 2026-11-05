from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models import user as user_model
from app.models.communication import ChatConversacion, ChatParticipante, ForoClase, ForoHilo

router = APIRouter()

# --- Chat Endpoints ---

@router.post("/chat/conversaciones/", response_model=schemas.ChatConversacion)
def create_conversacion(
    *,
    db: Session = Depends(deps.get_db),
    conv_in: schemas.ChatConversacionCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new chat conversation with tenant validation.
    """
    if conv_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create conversation for another tenant.")

    if current_user.id not in conv_in.participante_ids:
        conv_in.participante_ids.append(current_user.id)

    conversacion = crud.communication.create_conversacion(db=db, obj_in=conv_in)
    return conversacion

@router.post("/chat/mensajes/", response_model=schemas.ChatMensaje)
def create_mensaje(
    *,
    db: Session = Depends(deps.get_db),
    msg_in: schemas.ChatMensajeCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Post a new message in a conversation with ABAC participant check.
    """
    conv = db.query(ChatConversacion).filter(ChatConversacion.id == msg_in.conversacion_id).first()
    if not conv or conv.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    participant = (
        db.query(ChatParticipante)
        .filter(ChatParticipante.conversacion_id == msg_in.conversacion_id, ChatParticipante.usuario_id == current_user.id)
        .first()
    )
    if not participant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a participant of this conversation.")

    if msg_in.remitente_usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot send message as another user.")

    mensaje = crud.communication.create_mensaje(db=db, obj_in=msg_in)
    return mensaje

# --- Foro Endpoints ---

@router.post("/foros/", response_model=schemas.ForoClase)
def create_foro(
    *,
    db: Session = Depends(deps.get_db),
    foro_in: schemas.ForoClaseCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "profesor", "coordinador"])),
) -> Any:
    """
    Create a new forum for a class.
    """
    if foro_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create forum for another tenant.")

    foro = crud.communication.create_foro(db=db, obj_in=foro_in)
    return foro

@router.post("/foros/hilos/", response_model=schemas.ForoHilo)
def create_hilo(
    *,
    db: Session = Depends(deps.get_db),
    hilo_in: schemas.ForoHiloCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new thread in a forum with tenant validation.
    """
    foro = db.query(ForoClase).filter(ForoClase.id == hilo_in.foro_id).first()
    if not foro or foro.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forum not found.")

    if hilo_in.creado_por_usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create thread on behalf of another user.")

    hilo = crud.communication.create_hilo(db=db, obj_in=hilo_in)
    return hilo

@router.post("/foros/publicaciones/", response_model=schemas.ForoPublicacion)
def create_publicacion(
    *,
    db: Session = Depends(deps.get_db),
    publicacion_in: schemas.ForoPublicacionCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new post in a forum thread with tenant validation.
    """
    hilo = db.query(ForoHilo).filter(ForoHilo.id == publicacion_in.hilo_id).first()
    if not hilo or not hilo.foro or hilo.foro.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forum thread not found.")

    if publicacion_in.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot post on behalf of another user.")

    publicacion = crud.communication.create_publicacion(db=db, obj_in=publicacion_in)
    return publicacion
