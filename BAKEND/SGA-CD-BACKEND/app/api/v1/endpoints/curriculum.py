from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models import user as user_model

router = APIRouter()

def _check_user_roles(user: user_model.Usuario, allowed_roles: List[str]):
    user_roles = set(getattr(user, "role_codes", []))
    if getattr(user, "rol", None):
        rol_val = user.rol.value if hasattr(user.rol, "value") else str(user.rol)
        user_roles.add(rol_val)
    if not user_roles.intersection(set(allowed_roles)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized. Required roles: {allowed_roles}"
        )

# --- PlanCurricular Endpoints ---

@router.get("/planes/", response_model=List[schemas.PlanCurricular])
def read_planes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve curriculum plans for the current tenant.
    """
    planes = crud.curriculum.get_planes_by_tenant(db, inquilino_id=current_user.inquilino_id, skip=skip, limit=limit)
    return planes

@router.post("/planes/", response_model=schemas.PlanCurricular)
def create_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_in: schemas.PlanCurricularCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["profesor", "admin_empresa"])),
) -> Any:
    """
    Create a new curriculum plan for the user's tenant.
    """
    _check_user_roles(current_user, ["profesor", "admin_empresa"])
    if plan_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create curriculum plan for another tenant.")

    plan = crud.curriculum.create_plan(db=db, obj_in=plan_in)
    return plan


@router.put("/planes/{plan_id}", response_model=schemas.PlanCurricular)
def update_plan(
    plan_id: int,
    plan_in: schemas.PlanCurricularUpdate,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["profesor"])),
) -> Any:
    """
    Update a curriculum plan.
    Only the original author (profesor) can update their own plan. admin_empresa cannot edit plans created by others.
    If the plan was previously 'aprobado_definitivo' or 'vobo_tecnico', editing reopens it to 'borrador' and increments version.
    """
    _check_user_roles(current_user, ["profesor"])
    plan = crud.curriculum.get_plan(db, plan_id=plan_id)
    if not plan or plan.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan curricular not found.")

    if current_user.id != plan.creado_por_usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit a plan created by another user.")

    plan.nombre_plan = plan_in.nombre_plan
    plan.descripcion = plan_in.descripcion
    plan.area = plan_in.area

    # Reopening rule: post-approval edits reset state to 'borrador' and increment version
    if plan.estado_aprobacion in ("vobo_tecnico", "aprobado_definitivo"):
        plan.estado_aprobacion = "borrador"
        plan.version = (plan.version or 1) + 1
        plan.observaciones_revision = f"Plan modificado por autor. Versión {plan.version} reabierta para revisión."

    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/planes/{plan_id}/presentar", response_model=schemas.PlanCurricular)
def presentar_plan_revision(
    plan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["profesor"])),
) -> Any:
    """
    Teacher submits their own curriculum plan draft to coordinator for technical review (borrador/devuelto -> en_revision).
    admin_empresa, coordinador, and jefe_area CANNOT present plans.
    """
    _check_user_roles(current_user, ["profesor"])
    plan = crud.curriculum.get_plan(db, plan_id=plan_id)
    if not plan or plan.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan curricular not found.")

    if current_user.id != plan.creado_por_usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to submit a plan created by another user.")

    if plan.estado_aprobacion not in ("borrador", "devuelto"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot submit plan in state '{plan.estado_aprobacion}'.")

    plan.estado_aprobacion = "en_revision"
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/planes/{plan_id}/vobo", response_model=schemas.PlanCurricular)
def vobo_tecnico_coordinador(
    plan_id: int,
    action: Optional[schemas.PlanCurricularReviewAction] = None,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["coordinador"])),
) -> Any:
    """
    Coordinator grants technical VoBo to the plan (en_revision -> vobo_tecnico).
    admin_empresa, profesor, and jefe_area CANNOT grant technical VoBo.
    """
    from datetime import datetime, timezone
    _check_user_roles(current_user, ["coordinador"])
    plan = crud.curriculum.get_plan(db, plan_id=plan_id)
    if not plan or plan.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan curricular not found.")

    if plan.estado_aprobacion != "en_revision":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plan is not in 'en_revision' state (current: '{plan.estado_aprobacion}').")

    plan.estado_aprobacion = "vobo_tecnico"
    plan.vobo_coordinador_id = current_user.id
    plan.fecha_vobo = datetime.now(timezone.utc)
    if action and action.observaciones:
        plan.observaciones_revision = action.observaciones

    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/planes/{plan_id}/devolver", response_model=schemas.PlanCurricular)
def devolver_plan_observaciones(
    plan_id: int,
    action: schemas.PlanCurricularReviewAction,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["coordinador", "jefe_area"])),
) -> Any:
    """
    Coordinator or Jefe de Área returns plan with technical/administrative observations (en_revision / vobo_tecnico -> devuelto).
    Requires mandatory non-empty observaciones.
    """
    _check_user_roles(current_user, ["coordinador", "jefe_area"])
    plan = crud.curriculum.get_plan(db, plan_id=plan_id)
    if not plan or plan.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan curricular not found.")

    if not action or not action.observaciones or not action.observaciones.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Las observaciones son obligatorias para devolver un plan.")

    if plan.estado_aprobacion not in ("en_revision", "vobo_tecnico"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot return plan in state '{plan.estado_aprobacion}'.")

    plan.estado_aprobacion = "devuelto"
    plan.observaciones_revision = action.observaciones.strip()

    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/planes/{plan_id}/ratificar", response_model=schemas.PlanCurricular)
def ratificar_plan_jefe_area(
    plan_id: int,
    action: Optional[schemas.PlanCurricularReviewAction] = None,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["jefe_area"])),
) -> Any:
    """
    Jefe de Área grants final administrative ratification to a plan with VoBo técnico (vobo_tecnico -> aprobado_definitivo).
    Profesor, Coordinador, and admin_empresa CANNOT invoke this endpoint.
    """
    from datetime import datetime, timezone
    _check_user_roles(current_user, ["jefe_area"])
    plan = crud.curriculum.get_plan(db, plan_id=plan_id)
    if not plan or plan.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan curricular not found.")

    if plan.estado_aprobacion != "vobo_tecnico":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan requires valid technical VoBo from Coordinator before administrative ratification.")

    plan.estado_aprobacion = "aprobado_definitivo"
    plan.ratificacion_jefe_id = current_user.id
    plan.fecha_ratificacion = datetime.now(timezone.utc)
    if action and action.observaciones:
        plan.observaciones_revision = action.observaciones

    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

# --- PlanCurricularTema Endpoints ---

@router.post("/temas/", response_model=schemas.PlanCurricularTema)
def create_tema(
    *,
    db: Session = Depends(deps.get_db),
    tema_in: schemas.PlanCurricularTemaCreate,
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "profesor", "coordinador"])),
) -> Any:
    """
    Create a new topic for a curriculum plan with tenant validation.
    """
    plan = crud.curriculum.get_plan(db, plan_id=tema_in.plan_curricular_id)
    if not plan or plan.inquilino_id != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan curricular not found in current tenant.")

    tema = crud.curriculum.create_tema(db=db, obj_in=tema_in)
    return tema
