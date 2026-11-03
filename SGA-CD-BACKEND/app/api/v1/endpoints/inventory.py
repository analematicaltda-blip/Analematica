from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models import user as user_model

router = APIRouter()

# --- Elemento Endpoints ---

@router.get("/elementos/", response_model=List[schemas.Elemento])
def read_elementos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve elementos for the current tenant.
    """
    elementos = crud.inventory.get_elementos_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return elementos

@router.post("/elementos/", response_model=schemas.Elemento)
def create_elemento(
    *,
    db: Session = Depends(deps.get_db),
    elemento_in: schemas.ElementoCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "jefe_almacen", "almacenista"])),
) -> Any:
    """
    Create new elemento for the current tenant.
    """
    if elemento_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create elemento for another tenant.")

    elemento = crud.inventory.create_elemento(db=db, obj_in=elemento_in)
    return elemento

# --- Prestamo Endpoints ---

@router.get("/prestamos/", response_model=List[schemas.Prestamo])
def read_prestamos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve prestamos for the current tenant.
    """
    prestamos = crud.inventory.get_prestamos_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return prestamos

@router.post("/prestamos/", response_model=schemas.Prestamo)
def create_prestamo(
    *,
    db: Session = Depends(deps.get_db),
    prestamo_in: schemas.PrestamoCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "jefe_almacen", "almacenista", "profesor"])),
) -> Any:
    """
    Create new prestamo with tenant validation.
    """
    if prestamo_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create prestamo for another tenant.")

    elemento = crud.inventory.get_elemento(db, elemento_id=prestamo_in.elemento_id)
    if not elemento or elemento.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Elemento not found in current tenant.")

    prestamo = crud.inventory.create_prestamo(db=db, obj_in=prestamo_in)
    return prestamo
