from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models import user as user_model

router = APIRouter()

@router.get("/", response_model=List[schemas.Clase])
def read_clases(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve clases for the current user's tenant.
    """
    clases = crud.clase.get_clases_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return clases

@router.post("/", response_model=schemas.Clase)
def create_clase(
    *,
    db: Session = Depends(deps.get_db),
    clase_in: schemas.ClaseCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "profesor"])),
) -> Any:
    """
    Create new clase.
    """
    if clase_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=403, detail="Cannot create clase for another tenant.")
    clase = crud.clase.create_clase(db=db, obj_in=clase_in)
    return clase

@router.get("/{clase_id}", response_model=schemas.Clase)
def read_clase_by_id(
    clase_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific clase by id.
    """
    clase = crud.clase.get_clase(db=db, clase_id=clase_id)
    if not clase or clase.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=404, detail="Clase not found")
    return clase

@router.put("/{clase_id}", response_model=schemas.Clase)
def update_clase(
    *,
    db: Session = Depends(deps.get_db),
    clase_id: int,
    clase_in: schemas.ClaseUpdate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "profesor"])),
) -> Any:
    """
    Update a clase.
    """
    db_clase = crud.clase.get_clase(db=db, clase_id=clase_id)
    if not db_clase or db_clase.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=404, detail="Clase not found")
    clase = crud.clase.update_clase(db=db, db_obj=db_clase, obj_in=clase_in)
    return clase
