from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models import user as user_model

router = APIRouter()

@router.get("/", response_model=List[schemas.ProcesoFormacion])
def read_procesos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve procesos de formacion for the current user's tenant.
    """
    procesos = crud.clase.get_procesos_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return procesos

@router.post("/", response_model=schemas.ProcesoFormacion)
def create_proceso(
    *,
    db: Session = Depends(deps.get_db),
    proceso_in: schemas.ProcesoFormacionCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "profesor", "coordinador"])),
) -> Any:
    """
    Create new proceso de formacion.
    """
    if proceso_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create proceso for another tenant.")

    proceso = crud.clase.create_proceso(db=db, obj_in=proceso_in)
    return proceso

@router.get("/{proceso_id}", response_model=schemas.ProcesoFormacion)
def read_proceso_by_id(
    proceso_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific proceso by id.
    """
    proceso = crud.clase.get_proceso(db=db, proceso_id=proceso_id)
    if not proceso or proceso.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso not found")
    return proceso

@router.put("/{proceso_id}", response_model=schemas.ProcesoFormacion)
def update_proceso(
    *,
    db: Session = Depends(deps.get_db),
    proceso_id: int,
    proceso_in: schemas.ProcesoFormacionUpdate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "profesor", "coordinador"])),
) -> Any:
    """
    Update a proceso.
    """
    db_proceso = crud.clase.get_proceso(db=db, proceso_id=proceso_id)
    if not db_proceso or db_proceso.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso not found")
    proceso = crud.clase.update_proceso(db=db, db_obj=db_proceso, obj_in=proceso_in)
    return proceso
