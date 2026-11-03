from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models import user as user_model

router = APIRouter()

@router.get("/", response_model=List[schemas.Evento])
def read_eventos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve eventos for the current tenant.
    """
    eventos = crud.evento.get_eventos_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return eventos

@router.post("/", response_model=schemas.Evento)
def create_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_in: schemas.EventoCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new evento for the user's tenant with role authority check (admin_empresa, jefe_area, profesional_area).
    """
    if evento_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create evento for another tenant.")

    allowed_roles = {"admin_empresa", "jefe_area", "profesional_area", "admin_general"}
    user_roles = set(getattr(current_user, "role_codes", getattr(current_user, "role_list", [])))
    if not user_roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to create institutional events. Required roles: {list(allowed_roles)}"
        )

    evento = crud.evento.create_evento(db=db, obj_in=evento_in)
    return evento

@router.post("/participantes/", response_model=schemas.EventoParticipante)
def add_participante_to_evento(
    *,
    db: Session = Depends(deps.get_db),
    participante_in: schemas.EventoParticipanteCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a participant or assigned teacher to an event with tenant validation and active teacher checks.
    """
    if participante_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot add participant for another tenant.")

    evento = crud.evento.get_evento(db, evento_id=participante_in.evento_id)
    if not evento or evento.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento not found in current tenant.")

    # Check participant user
    participant_user = crud.user.get(db=db, id=participante_in.usuario_id)
    if not participant_user or participant_user.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant user not found in tenant.")

    if not participant_user.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Participant user is inactive.")

    participante = crud.evento.add_participante_to_evento(db=db, obj_in=participante_in)
    return participante
