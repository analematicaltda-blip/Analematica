from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models import user as user_model
from app.api import deps

router = APIRouter()

# --- Escenario Endpoints ---

@router.get("/", response_model=List[schemas.Escenario])
def read_escenarios(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve escenarios for the current tenant.
    """
    escenarios = crud.escenario.get_escenarios_by_tenant(
        db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit
    )
    return escenarios

@router.post("/", response_model=schemas.Escenario)
def create_escenario(
    *,
    db: Session = Depends(deps.get_db),
    escenario_in: schemas.EscenarioCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "jefe_escenarios"]))
) -> Any:
    """
    Create new escenario. Only accessible to admins and scenario managers.
    """
    escenario = crud.escenario.create_escenario(
        db=db, obj_in=escenario_in, inquilino_id=current_user.inquilino_id
    )
    return escenario

# --- Reserva Endpoints ---

@router.get("/reservas/", response_model=List[schemas.Reserva])
def read_reservas_by_part(
    escenario_parte_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve reservas for a specific escenario part.
    """
    reservas = crud.escenario.get_reservas_by_escenario_parte(
        db, escenario_parte_id=escenario_parte_id, skip=skip, limit=limit
    )
    return reservas


@router.post("/reservas/", response_model=schemas.Reserva)
def create_reserva(
    *,
    db: Session = Depends(deps.get_db),
    reserva_in: schemas.ReservaCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create a new reserva after checking for scheduling conflicts.
    """
    conflictos = crud.escenario.get_reservas_en_horario(
        db,
        escenario_parte_id=reserva_in.escenario_parte_id,
        fecha_inicio=reserva_in.fecha_inicio,
        fecha_fin=reserva_in.fecha_fin,
    )
    if conflictos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El escenario ya está reservado en este horario.",
        )

    reserva = crud.escenario.create_reserva(
        db=db,
        obj_in=reserva_in,
        inquilino_id=current_user.inquilino_id,
        usuario_id=current_user.id
    )
    return reserva
