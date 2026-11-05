from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.crud import tenancy as crud_tenancy
from app.api import deps
from app.services.plan_capability_service import PlanCapabilityService
from app.models.tenancy import Inquilino
from app.models.billing import Suscripcion

router = APIRouter()

@router.post("/register", response_model=schemas.tenancy.TenantCreateResponse)
def register_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_in: schemas.tenancy.TenantCreate,
):
    """
    Register a new tenant (company) and its initial admin user.
    """
    try:
        created_tenant = crud_tenancy.create_tenant_and_admin(db=db, obj_in=tenant_in)
        # The admin is attached to the tenant object in the CRUD function
        return {
            "tenant": created_tenant,
            "admin": created_tenant.admin,
        }
    except ValueError as e:
        # This could happen if the role doesn't exist, for example.
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch other potential database errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred during registration.")


@router.get("/my-plan-capabilities", response_model=schemas.tenancy.TenantCapabilitiesResponse)
def get_my_plan_capabilities(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Get effective capabilities and monthly quotas for the authenticated user's organization.
    Strictly read-only resolution enforcing tenant isolation derived from the user's JWT identity.
    """
    if current_user.inquilino_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization tenant."
        )

    tenant = db.query(Inquilino).filter(Inquilino.id == current_user.inquilino_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization tenant not found."
        )

    if not getattr(tenant, "activo", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization tenant account is inactive."
        )

    sub = db.query(Suscripcion).filter(Suscripcion.inquilino_id == tenant.id).order_by(Suscripcion.id.desc()).first()

    tenant_data = {
        "id": tenant.id,
        "nombre_empresa": getattr(tenant, "nombre_empresa", ""),
        "tipo_organizacion": getattr(tenant, "tipo_organizacion", "entidad_publica"),
        "ambito_organizacional": getattr(tenant, "ambito_organizacional", "municipal"),
        "vocacion_institucional": getattr(tenant, "vocacion_institucional", "deportiva"),
        "plan": getattr(tenant, "plan", "basico"),
        "activo": getattr(tenant, "activo", True),
    }

    sub_data = None
    if sub:
        sub_data = {
            "id": getattr(sub, "id", None),
            "plan": getattr(sub, "plan", None),
            "estado": getattr(sub, "estado", None),
            "fecha_inicio": getattr(sub, "fecha_inicio", None),
            "fecha_fin": getattr(sub, "fecha_fin", None),
        }

    effective_caps = PlanCapabilityService.resolve_capabilities(
        tenant_data=tenant_data,
        subscription_data=sub_data
    )

    return effective_caps.dict()
