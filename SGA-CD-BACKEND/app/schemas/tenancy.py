from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional

class TenantCreate(BaseModel):
    nombre_empresa: str
    tipo_organizacion: str = "entidad_publica"
    ambito_organizacional: str = "municipal"
    admin_nombre_completo: str
    admin_email: EmailStr
    admin_password: str

class Tenant(BaseModel):
    id: int
    nombre: str

    class Config:
        orm_mode = True

class TenantAdmin(BaseModel):
    id: int
    nombre_usuario: str
    correo: EmailStr

    class Config:
        orm_mode = True

class TenantCreateResponse(BaseModel):
    tenant: Tenant
    admin: TenantAdmin

class TenantCapabilitiesResponse(BaseModel):
    inquilino_id: int
    nombre_empresa: str
    tipo_organizacion: str
    ambito_organizacional: str
    vocacion_institucional: str = "deportiva"
    canonical_plan: str
    subscription_status: str
    is_active: bool
    panel_institucional_enabled: bool
    gestion_usuarios_enabled: bool
    modulos_deportivos_culturales_enabled: bool
    crm_leads_enabled: bool
    crm_campaigns_enabled: bool
    ai_images_enabled: bool
    ai_carousels_enabled: bool
    ai_video_enabled: bool
    ai_reels_enabled: bool
    social_publishing_enabled: bool
    crm_analytics_enabled: bool
    monthly_limits: Dict[str, int]
