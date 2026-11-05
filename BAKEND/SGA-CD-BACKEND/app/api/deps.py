from typing import Generator, Any, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.schemas.token import TokenData
from app import crud
from app.models import user as user_model


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"  # Updated to new login URL
)

def get_db() -> Generator:
    """
    Dependency to get a DB session for each request.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_token_data(token: str = Depends(reusable_oauth2)) -> TokenData:
    """
    Dependency that decodes and validates the JWT token, returning the payload.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type, expected 'access'",
            )
        token_data = TokenData(
            sub=payload.get("sub"),
            roles=payload.get("roles", []),
            inquilino_id=payload.get("inquilino_id")
        )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data


def get_current_user(
    db: Session = Depends(get_db), token_data: TokenData = Depends(get_token_data)
) -> user_model.Usuario:
    """
    Dependency to get the current user from the token payload.
    """
    user = db.query(user_model.Usuario).filter(user_model.Usuario.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Attach role codes from token to avoid modifying mapped relationship on ORM instance
    user.role_codes = token_data.roles
    return user

def get_current_active_user(
    current_user: user_model.Usuario = Depends(get_current_user),
) -> user_model.Usuario:
    """
    Dependency to get the current active user.
    Raises an exception if the user is inactive.
    """
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def role_required(required_roles: List[str]):
    """
    A dependency factory that returns a dependency to check for required roles.
    Checks the roles present on the authenticated user and returns the current user ORM instance.
    """
    def role_checker(
        current_user: user_model.Usuario = Depends(get_current_active_user)
    ) -> user_model.Usuario:
        user_roles = set(getattr(current_user, "role_codes", []))
        if not user_roles:
            user_roles = set(getattr(current_user, "role_list", []))
        if not user_roles.intersection(set(required_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized. Requires one of the following roles: {required_roles}",
            )
        return current_user

    return role_checker


def require_plan_capability(capability_name: str):
    """
    Dependency factory enforcing commercial feature access based on the tenant's Plan & Subscription.
    Derives identity exclusively from current_user (JWT).
    Checks PlanCapabilityService.resolve_capabilities and raises:
      - 400 Bad Request if user has no inquilino_id associated.
      - 404 Not Found if tenant record does not exist in DB.
      - 403 Forbidden if tenant account is inactive.
      - 402 Payment Required if requested capability is not enabled in tenant's Plan or subscription is expired/canceled.
      - 403 Forbidden if capability_name is unrecognized.
    Does NOT write to DB.
    """
    def capability_checker(
        db: Session = Depends(get_db),
        current_user: user_model.Usuario = Depends(get_current_active_user)
    ) -> user_model.Usuario:
        if current_user.inquilino_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any organization tenant."
            )

        from app.models.tenancy import Inquilino
        from app.models.billing import Suscripcion
        from app.services.plan_capability_service import PlanCapabilityService

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

        caps_dict = effective_caps.dict()

        target_key = capability_name if capability_name.endswith("_enabled") else f"{capability_name}_enabled"

        if target_key not in caps_dict:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unknown capability '{capability_name}' requested."
            )

        if not caps_dict[target_key]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Capability '{capability_name}' is not enabled for your organization plan or subscription is inactive. Please upgrade to Plan Full."
            )

        return current_user

    return capability_checker


def verify_resource_tenant_and_owner(
    db_obj: Any,
    current_user: user_model.Usuario,
    owner_field: str = "usuario_id",
    tenant_field: str = "inquilino_id",
    enforce_owner: bool = False
) -> bool:
    """
    Helper function to enforce strict ABAC / Tenant isolation and ownership on any SQLAlchemy DB object.
    Raises HTTP 404 if object belongs to another tenant (preventing object enumeration),
    and HTTP 403 if user lacks ownership when enforce_owner is True.
    """
    if not db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    obj_tenant = getattr(db_obj, tenant_field, None)
    if obj_tenant is not None and obj_tenant != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    if enforce_owner:
        obj_owner = getattr(db_obj, owner_field, None)
        if obj_owner is not None and obj_owner != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")

    return True
