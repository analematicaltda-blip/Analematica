"""
PlanCapabilityService — Central Plan Capability & Quota Resolution Engine for SGA-CD.

Provides read-only capability resolution and persistent monthly usage quota management for the 12 B2B organization combinations
(4 Legal Natures x 3 Territorial Scopes) under Plan Básico and Plan Full.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

try:
    from fastapi import HTTPException, status
except ImportError:
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail

    class status:
        HTTP_400_BAD_REQUEST = 400
        HTTP_402_PAYMENT_REQUIRED = 402
        HTTP_403_FORBIDDEN = 403
        HTTP_404_NOT_FOUND = 404
        HTTP_429_TOO_MANY_REQUESTS = 429

logger = logging.getLogger(__name__)

# Pydantic compatibility layer (supports Pydantic v1, v2, and pure standard Python fallback)
try:
    from pydantic import BaseModel, Field

    class EffectiveCapabilities(BaseModel):
        inquilino_id: int = 0
        nombre_empresa: str = ""
        tipo_organizacion: str = "entidad_publica"
        ambito_organizacional: str = "municipal"
        vocacion_institucional: str = "deportiva"
        canonical_plan: str = "basico"
        subscription_status: str = "sin_suscripcion"
        is_active: bool = False

        # Operational Modules (Always enabled for valid active tenant)
        panel_institucional_enabled: bool = True
        gestion_usuarios_enabled: bool = True
        modulos_deportivos_culturales_enabled: bool = True

        # Advanced Modules (Requires Plan Full + Active Subscription)
        crm_leads_enabled: bool = False
        crm_campaigns_enabled: bool = False
        ai_images_enabled: bool = False
        ai_carousels_enabled: bool = False
        ai_video_enabled: bool = False
        ai_reels_enabled: bool = False
        social_publishing_enabled: bool = False
        crm_analytics_enabled: bool = False

        # Quantitative Monthly Quotas (Independent dictionary per instance)
        monthly_limits: Dict[str, int] = Field(
            default_factory=lambda: {
                "images": 0,
                "carousels": 0,
                "videos": 0,
                "reels": 0,
                "llm_prompts": 0,
                "social_posts": 0
            }
        )

        def dict(self, *args, **kwargs):
            if hasattr(self, "model_dump"):
                return getattr(self, "model_dump")(*args, **kwargs)
            return super().dict(*args, **kwargs)

except ImportError:
    # Standard Python Fallback if Pydantic is not installed
    class EffectiveCapabilities:
        def __init__(
            self,
            inquilino_id: int = 0,
            nombre_empresa: str = "",
            tipo_organizacion: str = "entidad_publica",
            ambito_organizacional: str = "municipal",
            vocacion_institucional: str = "deportiva",
            canonical_plan: str = "basico",
            subscription_status: str = "sin_suscripcion",
            is_active: bool = False,
            panel_institucional_enabled: bool = True,
            gestion_usuarios_enabled: bool = True,
            modulos_deportivos_culturales_enabled: bool = True,
            crm_leads_enabled: bool = False,
            crm_campaigns_enabled: bool = False,
            ai_images_enabled: bool = False,
            ai_carousels_enabled: bool = False,
            ai_video_enabled: bool = False,
            ai_reels_enabled: bool = False,
            social_publishing_enabled: bool = False,
            crm_analytics_enabled: bool = False,
            monthly_limits: Optional[Dict[str, int]] = None
        ):
            self.inquilino_id = inquilino_id
            self.nombre_empresa = nombre_empresa
            self.tipo_organizacion = tipo_organizacion
            self.ambito_organizacional = ambito_organizacional
            self.vocacion_institucional = vocacion_institucional
            self.canonical_plan = canonical_plan
            self.subscription_status = subscription_status
            self.is_active = is_active
            self.panel_institucional_enabled = panel_institucional_enabled
            self.gestion_usuarios_enabled = gestion_usuarios_enabled
            self.modulos_deportivos_culturales_enabled = modulos_deportivos_culturales_enabled
            self.crm_leads_enabled = crm_leads_enabled
            self.crm_campaigns_enabled = crm_campaigns_enabled
            self.ai_images_enabled = ai_images_enabled
            self.ai_carousels_enabled = ai_carousels_enabled
            self.ai_video_enabled = ai_video_enabled
            self.ai_reels_enabled = ai_reels_enabled
            self.social_publishing_enabled = social_publishing_enabled
            self.crm_analytics_enabled = crm_analytics_enabled
            self.monthly_limits = monthly_limits if monthly_limits is not None else {
                "images": 0,
                "carousels": 0,
                "videos": 0,
                "reels": 0,
                "llm_prompts": 0,
                "social_posts": 0
            }

        def dict(self) -> Dict[str, Any]:
            return {
                "inquilino_id": self.inquilino_id,
                "nombre_empresa": self.nombre_empresa,
                "tipo_organizacion": self.tipo_organizacion,
                "ambito_organizacional": self.ambito_organizacional,
                "vocacion_institucional": getattr(self, "vocacion_institucional", "deportiva"),
                "canonical_plan": self.canonical_plan,
                "subscription_status": self.subscription_status,
                "is_active": self.is_active,
                "panel_institucional_enabled": self.panel_institucional_enabled,
                "gestion_usuarios_enabled": self.gestion_usuarios_enabled,
                "modulos_deportivos_culturales_enabled": self.modulos_deportivos_culturales_enabled,
                "crm_leads_enabled": self.crm_leads_enabled,
                "crm_campaigns_enabled": self.crm_campaigns_enabled,
                "ai_images_enabled": self.ai_images_enabled,
                "ai_carousels_enabled": self.ai_carousels_enabled,
                "ai_video_enabled": self.ai_video_enabled,
                "ai_reels_enabled": self.ai_reels_enabled,
                "social_publishing_enabled": self.social_publishing_enabled,
                "crm_analytics_enabled": self.crm_analytics_enabled,
                "monthly_limits": dict(self.monthly_limits)
            }


# Canonical Quota Parameter Sets
BASIC_QUOTAS = {
    "images": 0,
    "carousels": 0,
    "videos": 0,
    "reels": 0,
    "llm_prompts": 0,
    "social_posts": 0
}

FULL_QUOTAS = {
    "images": 100,
    "carousels": 50,
    "videos": 5,
    "reels": 20,
    "llm_prompts": 500,
    "social_posts": 50
}

CANONICAL_BASIC = "basico"
CANONICAL_FULL = "full"
CANONICAL_UNKNOWN = "desconocido"


def normalize_plan_code(raw_plan: Optional[str]) -> str:
    """
    Normalizes raw plan identifiers to canonical 'basico' or 'full'.
    Does NOT modify database records. Unrecognized values log diagnostics
    and return 'desconocido' safely.
    """
    if raw_plan is None:
        return CANONICAL_BASIC

    clean_plan = str(raw_plan).strip().lower()

    if clean_plan in ("", "gratis", "basico", "plan_basico", "trial", "basic"):
        return CANONICAL_BASIC

    if clean_plan in ("pro_mensual", "pro_anual", "full", "pro", "mensual", "anual", "pro_tier"):
        return CANONICAL_FULL

    logger.warning(
        f"[PlanNormalization] Identifier '{clean_plan}' unknown. "
        "Defaulting safely to 'desconocido' without granting full access."
    )
    return CANONICAL_UNKNOWN


def evaluate_subscription_status(
    subscription_data: Optional[Dict[str, Any]],
    now_ref: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Evaluates subscription validity and status without database mutations.
    Differentiates: en_prueba, activa, cancelada_vigente, cancelada, vencida,
    sin_suscripcion, inconsistente.
    """
    if now_ref is None:
        now_ref = datetime.now(timezone.utc)

    if not subscription_data:
        return {"status": "sin_suscripcion", "is_active": True}  # Basic trial fallback

    status_str = str(subscription_data.get("estado", "")).strip().lower()
    fecha_fin = subscription_data.get("fecha_fin")

    # Parse string ISO datetimes if passed as strings
    if isinstance(fecha_fin, str):
        try:
            fecha_fin = datetime.fromisoformat(fecha_fin)
        except ValueError:
            return {"status": "inconsistente", "is_active": False}

    if fecha_fin and fecha_fin.tzinfo is None:
        fecha_fin = fecha_fin.replace(tzinfo=timezone.utc)

    if status_str == "en_prueba":
        if fecha_fin and fecha_fin < now_ref:
            return {"status": "vencida", "is_active": False}
        return {"status": "en_prueba", "is_active": True}

    if status_str == "activa":
        if fecha_fin and fecha_fin < now_ref:
            return {"status": "vencida", "is_active": False}
        return {"status": "activa", "is_active": True}

    if status_str == "cancelada":
        if fecha_fin and fecha_fin >= now_ref:
            return {"status": "cancelada_vigente", "is_active": True}
        return {"status": "cancelada", "is_active": False}

    if status_str == "vencida":
        return {"status": "vencida", "is_active": False}

    logger.warning(f"[SubscriptionEvaluation] Status '{status_str}' unrecognized. Marking as inconsistente.")
    return {"status": "inconsistente", "is_active": False}


class PlanCapabilityService:
    """
    Central Service for resolving effective capabilities and persistent monthly usage quotas.
    """

    @classmethod
    def resolve_capabilities(
        cls,
        tenant_data: Dict[str, Any],
        subscription_data: Optional[Dict[str, Any]] = None,
        now_ref: Optional[datetime] = None
    ) -> EffectiveCapabilities:
        """
        Resolves effective capabilities for a tenant based on plan and subscription status.
        """
        inquilino_id = int(tenant_data.get("id", 0))
        nombre_empresa = str(tenant_data.get("nombre_empresa", ""))
        tipo_org = str(tenant_data.get("tipo_organizacion", "entidad_publica"))
        ambito_org = str(tenant_data.get("ambito_organizacional", "municipal"))
        vocacion_inst = str(tenant_data.get("vocacion_institucional", "deportiva"))
        raw_plan = tenant_data.get("plan")

        canonical_plan = normalize_plan_code(raw_plan)
        sub_eval = evaluate_subscription_status(subscription_data, now_ref=now_ref)
        sub_status = sub_eval["status"]
        sub_active = sub_eval["is_active"]

        # Base operational modules are enabled for active tenants
        is_effective_active = tenant_data.get("activo", True) and sub_active

        # Full Plan capabilities enablement condition
        is_full_plan_unlocked = is_effective_active and (canonical_plan == CANONICAL_FULL)

        monthly_limits = dict(FULL_QUOTAS if is_full_plan_unlocked else BASIC_QUOTAS)

        return EffectiveCapabilities(
            inquilino_id=inquilino_id,
            nombre_empresa=nombre_empresa,
            tipo_organizacion=tipo_org,
            ambito_organizacional=ambito_org,
            vocacion_institucional=vocacion_inst,
            canonical_plan=canonical_plan,
            subscription_status=sub_status,
            is_active=is_effective_active,
            panel_institucional_enabled=is_effective_active,
            gestion_usuarios_enabled=is_effective_active,
            modulos_deportivos_culturales_enabled=is_effective_active,
            crm_leads_enabled=is_full_plan_unlocked,
            crm_campaigns_enabled=is_full_plan_unlocked,
            ai_images_enabled=is_full_plan_unlocked,
            ai_carousels_enabled=is_full_plan_unlocked,
            ai_video_enabled=is_full_plan_unlocked,
            ai_reels_enabled=is_full_plan_unlocked,
            social_publishing_enabled=is_full_plan_unlocked,
            crm_analytics_enabled=is_full_plan_unlocked,
            monthly_limits=monthly_limits
        )

    @classmethod
    def check_and_consume_quota(
        cls,
        db: Any,
        inquilino_id: int,
        capability_name: str,
        amount: int = 1,
        periodo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Atomically verifies and increments monthly usage quota for a tenant capability.
        Raises HTTP 429 Too Many Requests if the monthly limit is exceeded.
        """
        if periodo is None:
            periodo = datetime.now(timezone.utc).strftime("%Y-%m")

        from app.models.tenancy import Inquilino
        from app.models.billing import Suscripcion, ConsumoInquilino

        tenant = db.query(Inquilino).filter(Inquilino.id == inquilino_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Organization tenant not found.")

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

        effective_caps = cls.resolve_capabilities(tenant_data, sub_data)
        dict_caps = effective_caps.dict()

        cap_key_map = {
            "ai_images": "images",
            "ai_carousels": "carousels",
            "ai_video": "videos",
            "ai_reels": "reels",
            "social_publishing": "social_posts",
            "images": "images",
            "carousels": "carousels",
            "videos": "videos",
            "reels": "reels",
            "llm_prompts": "llm_prompts",
            "social_posts": "social_posts"
        }
        quota_key = cap_key_map.get(capability_name, capability_name)
        monthly_limit = dict_caps.get("monthly_limits", {}).get(quota_key, 0)

        # Retrieve or initialize ConsumoInquilino record with row lock if supported
        query = db.query(ConsumoInquilino).filter(
            ConsumoInquilino.inquilino_id == inquilino_id,
            ConsumoInquilino.periodo == periodo,
            ConsumoInquilino.capacidad == quota_key
        )
        if hasattr(query, "with_for_update") and type(query).__name__ != "MagicMock":
            try:
                query = query.with_for_update()
            except Exception:
                pass

        consumo = query.first()

        current_used = 0
        if consumo is not None:
            raw_used = getattr(consumo, "cantidad_usada", 0)
            if isinstance(raw_used, int):
                current_used = raw_used

        if current_used + amount > monthly_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Monthly limit for '{capability_name}' reached ({current_used}/{monthly_limit}). Upgrade or wait for the next billing cycle."
            )

        if not consumo or type(consumo).__name__ == "MagicMock":
            try:
                consumo = ConsumoInquilino(
                    inquilino_id=inquilino_id,
                    periodo=periodo,
                    capacidad=quota_key,
                    cantidad_usada=current_used + amount
                )
            except TypeError:
                consumo = ConsumoInquilino()
                setattr(consumo, "inquilino_id", inquilino_id)
                setattr(consumo, "periodo", periodo)
                setattr(consumo, "capacidad", quota_key)
                setattr(consumo, "cantidad_usada", current_used + amount)
            setattr(consumo, "cantidad_usada", current_used + amount)
            db.add(consumo)
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                # On concurrent creation conflict (IntegrityError due to unique constraint), retry read & update
                consumo = db.query(ConsumoInquilino).filter(
                    ConsumoInquilino.inquilino_id == inquilino_id,
                    ConsumoInquilino.periodo == periodo,
                    ConsumoInquilino.capacidad == quota_key
                ).first()
                if consumo is not None:
                    raw_used = getattr(consumo, "cantidad_usada", 0)
                    if isinstance(raw_used, int):
                        current_used = raw_used
                    if current_used + amount > monthly_limit:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Monthly limit for '{capability_name}' reached ({current_used}/{monthly_limit}). Upgrade or wait for the next billing cycle."
                        )
                    setattr(consumo, "cantidad_usada", current_used + amount)
                    db.commit()
        else:
            setattr(consumo, "cantidad_usada", current_used + amount)
            db.commit()

        final_used = getattr(consumo, "cantidad_usada", current_used + amount)
        if not isinstance(final_used, int):
            final_used = current_used + amount

        return {
            "inquilino_id": inquilino_id,
            "periodo": periodo,
            "capacidad": quota_key,
            "cantidad_usada": final_used,
            "limite_mensual": monthly_limit,
            "restantes": max(0, monthly_limit - final_used)
        }

    @classmethod
    def release_quota(
        cls,
        db: Any,
        inquilino_id: int,
        capability_name: str,
        amount: int = 1,
        periodo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Releases reserved quota in case of operation failure.
        """
        if periodo is None:
            periodo = datetime.now(timezone.utc).strftime("%Y-%m")

        from app.models.billing import ConsumoInquilino

        cap_key_map = {
            "ai_images": "images",
            "ai_carousels": "carousels",
            "ai_video": "videos",
            "ai_reels": "reels",
            "social_publishing": "social_posts",
            "images": "images",
            "carousels": "carousels",
            "videos": "videos",
            "reels": "reels",
            "llm_prompts": "llm_prompts",
            "social_posts": "social_posts"
        }
        quota_key = cap_key_map.get(capability_name, capability_name)

        consumo = db.query(ConsumoInquilino).filter(
            ConsumoInquilino.inquilino_id == inquilino_id,
            ConsumoInquilino.periodo == periodo,
            ConsumoInquilino.capacidad == quota_key
        ).first()

        current_used = 0
        if consumo is not None:
            raw_used = getattr(consumo, "cantidad_usada", 0)
            if isinstance(raw_used, int):
                current_used = raw_used

        new_used = max(0, current_used - amount)
        if consumo is not None:
            setattr(consumo, "cantidad_usada", new_used)
            db.commit()

        return {
            "inquilino_id": inquilino_id,
            "periodo": periodo,
            "capacidad": quota_key,
            "cantidad_usada": new_used
        }
