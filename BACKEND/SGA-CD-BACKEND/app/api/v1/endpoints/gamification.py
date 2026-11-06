from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.models import user as user_model
from app.api import deps

router = APIRouter()


# @router.post("/mercado/comprar/{item_id}", response_model=schemas.GamificacionCompraLog)
# def comprar_item_mercado(
#     *,
#     db: Session = Depends(deps.get_db),
#     item_id: int,
#     current_user: user_model.Usuario = Depends(deps.role_required(["alumno"])),
# ) -> Any:
#     """
#     Allows a student to purchase an item from the marketplace.
#     """
#     # Business logic for purchasing an item would go here
#     # 1. Get the item and its cost
#     # 2. Check if the student has enough points
#     # 3. Deduct points from the student
#     # 4. Create a purchase log entry
#     # This is a placeholder implementation
#     item = crud.gamification.get_mercado_item(db, item_id=item_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")

#     # Placeholder for student points check
#     print(f"User {current_user.nombre_completo} is attempting to buy {item.nombre} for {item.costo_puntos} points.")

#     # Create a dummy purchase log
#     compra_log_in = schemas.GamificacionCompraLogCreate(
#         item_id=item_id,
#         alumno_id=current_user.id,
#         costo_en_puntos=item.costo_puntos
#     )
#     # This is not a real CRUD function, so we just return the schema
#     # In a real scenario, you'd have a crud.gamification.create_compra_log
#     return compra_log_in


# --- GamificacionAccion Endpoints ---

@router.get("/acciones/", response_model=List[schemas.GamificacionAccion])
def read_acciones(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve gamification actions for the current tenant.
    """
    acciones = crud.gamification.get_acciones_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return acciones

@router.post("/acciones/", response_model=schemas.GamificacionAccion)
def create_accion(
    *,
    db: Session = Depends(deps.get_db),
    accion_in: schemas.GamificacionAccionCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa"])),
) -> Any:
    """
    Create a new gamification action for the user's tenant.
    """
    if accion_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=403, detail="Cannot create action for another tenant.")

    accion = crud.gamification.create_accion(db=db, obj_in=accion_in)
    return accion

# --- GamificacionPuntosLog Endpoints ---

@router.post("/puntos-log/", response_model=schemas.GamificacionPuntosLog)
def create_puntos_log_entry(
    *,
    db: Session = Depends(deps.get_db),
    log_in: schemas.GamificacionPuntosLogCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new gamification points log entry with tenant validation.
    This would be called by other services when a student completes an action.
    """
    if log_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=403, detail="Cannot log points for another tenant.")

    log_entry = crud.gamification.create_puntos_log(db=db, obj_in=log_in)
    return log_entry

# Other endpoints for Medals, etc., would follow the same pattern.


# --- GamificacionMision Endpoints ---

@router.get("/misiones/", response_model=List[schemas.GamificacionMision])
def read_misiones(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all missions for the current user's tenant.
    """
    misiones = crud.gamification.get_misiones_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return misiones

@router.post("/misiones/", response_model=schemas.GamificacionMision)
def create_mision(
    *,
    db: Session = Depends(deps.get_db),
    mision_in: schemas.GamificacionMisionCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "coordinador"])),
) -> Any:
    """
    Create a new mission. (Restricted to admins and coordinators)
    """
    if mision_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=403, detail="Cannot create mission for another tenant.")
    mision = crud.gamification.create_mision(db=db, obj_in=mision_in)
    return mision


# --- GamificacionMercadoItem Endpoints ---

@router.get("/mercado/items/", response_model=List[schemas.GamificacionMercadoItem])
def read_mercado_items(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all marketplace items for the current user's tenant.
    """
    items = crud.gamification.get_mercado_items_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return items

@router.post("/mercado/items/", response_model=schemas.GamificacionMercadoItem)
def create_mercado_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.GamificacionMercadoItemCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "jefe_almacen"])),
) -> Any:
    """
    Create a new marketplace item. (Restricted to admins and warehouse managers)
    """
    if item_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=403, detail="Cannot create marketplace item for another tenant.")
    item = crud.gamification.create_mercado_item(db=db, obj_in=item_in)
    return item
