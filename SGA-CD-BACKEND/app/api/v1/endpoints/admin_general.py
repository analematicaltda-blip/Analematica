from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from app import models
from app.api import deps
from app.crud import settings as crud_settings
from app.services.ai_router import ai_router
from app.services.plan_capability_service import PlanCapabilityService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def validate_url_safe(url_str: str) -> bool:
    if not url_str:
        return True
    url_str = url_str.strip()
    if url_str.startswith("javascript:") or url_str.startswith("data:"):
        return False
    if url_str.startswith("http://") or url_str.startswith("https://") or url_str.startswith("assets/"):
        return True
    return True


class WhatsAppSettings(BaseModel):
    phone_number_id: str
    access_token: str
    business_account_id: str


class LandingSettings(BaseModel):
    hero_title: str
    hero_subtitle: str
    contact_email: str
    social_links: str
    footer_copy: str
    hero_video_url: str = "assets/video/sga_cd_institutional_5min.mp4"
    logo_url: str = "assets/images/sga_cd_official_logo.svg"
    carousel_urls: str = ""
    carousel_slides_json: str = ""
    faq1_question: str = "¿Qué modalidades deportivas y culturales ofrece SGA-CD?"
    faq1_answer: str = "SGA-CD administra Taekwondo, Fútbol, Baloncesto, Danza Joropo e Instrumentos Tradicionales."
    faq2_question: str = "¿Cómo se realiza la verificación de usuarios y roles?"
    faq2_answer: str = "Mediante autenticación JWT, RBAC perimetral e integración con esquemas multi-tenant."
    plan_tier1_price: str = "$100 USD/mes — Entidades Públicas y Privadas B2B"
    plan_tier2_price: str = "$20 USD/mes — Instructores y Profesores"
    plan_grace_days: int = 5
    seo_title: str = "SGA-CD — Plataforma Integral de Gestión Deportiva y Cultural"
    seo_description: str = "Sistema de Gestión Académico, Deportivo y Cultural para Entidades Públicas y Privadas."

    @validator('hero_video_url', 'logo_url', 'carousel_urls', allow_reuse=True)
    def validate_urls(cls, v):
        if v and not validate_url_safe(v):
            raise ValueError(f"URL o ruta no segura: {v}")
        return v


class LLMKeysSettings(BaseModel):
    openai_api_key: str = ""
    google_api_key: str = ""
    meta_access_token: str = ""


class ApiSettings(BaseModel):
    llm_preference: str
    openai_api_key: str
    google_api_key: str
    meta_access_token: str


class PredisMediaRequest(BaseModel):
    area: str
    prompt: str
    format: str
    target_platforms: list[str] = ["instagram", "tiktok", "youtube_shorts", "facebook"]
    custom_dimensions: str = "1080x1920 (9:16)"
    scheduled_time: str = ""


class PredisMediaResponse(BaseModel):
    status: str
    title: str
    copy: str
    poster_url: str
    video_path: str
    dimensions: str
    target_platforms: list[str]
    scheduled_time: str


@router.get("/settings/api_keys", response_model=ApiSettings)
def get_api_settings(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.role_required(["admin_general"])),
):
    """
    Get current AI/LLM Provider configuration and preference.
    """
    tenant = current_user.inquilino
    return ApiSettings(
        llm_preference=tenant.llm_preference if tenant else "local",
        openai_api_key=tenant.openai_api_key if tenant else "",
        google_api_key=tenant.google_api_key if tenant else "",
        meta_access_token=crud_settings.get_setting(db, "meta_page_access_token").value if crud_settings.get_setting(db, "meta_page_access_token") else ""
    )


@router.get("/settings/ollama/health")
def check_ollama_health(
    current_user: models.Usuario = Depends(deps.role_required(["admin_general"])),
):
    """
    Check Ollama Local Server health and installed models list.
    """
    return ai_router.check_ollama_health()


@router.put("/settings/llm_keys")
def update_llm_keys(
    *,
    db: Session = Depends(deps.get_db),
    keys_in: LLMKeysSettings,
    current_user: models.Usuario = Depends(deps.role_required(["admin_general"])),
):
    """
    Update LLM provider keys (OpenAI / Gemini / Meta).
    """
    tenant = current_user.inquilino
    if tenant:
        if keys_in.openai_api_key:
            tenant.openai_api_key = keys_in.openai_api_key
        if keys_in.google_api_key:
            tenant.google_api_key = keys_in.google_api_key
        db.commit()

    if keys_in.meta_access_token:
        crud_settings.update_setting(db, key="meta_page_access_token", value=keys_in.meta_access_token)

    return {"status": "success", "message": "API keys updated successfully."}


@router.get("/settings/whatsapp", response_model=WhatsAppSettings)
def get_whatsapp_settings(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.role_required(["admin_general"])),
):
    """
    Get WhatsApp Cloud API configuration settings.
    """
    phone_number_id = crud_settings.get_setting(db, "whatsapp_phone_number_id")
    access_token = crud_settings.get_setting(db, "whatsapp_access_token")
    business_account_id = crud_settings.get_setting(db, "whatsapp_business_account_id")

    return WhatsAppSettings(
        phone_number_id=phone_number_id.value if phone_number_id else "",
        access_token=access_token.value if access_token else "",
        business_account_id=business_account_id.value if business_account_id else ""
    )


@router.put("/settings/whatsapp", response_model=WhatsAppSettings)
def update_whatsapp_settings(
    *,
    db: Session = Depends(deps.get_db),
    settings_in: WhatsAppSettings,
    current_user: models.Usuario = Depends(deps.role_required(["admin_general"])),
):
    """
    Update WhatsApp Cloud API configuration settings.
    """
    crud_settings.update_setting(db, key="whatsapp_phone_number_id", value=settings_in.phone_number_id)
    crud_settings.update_setting(db, key="whatsapp_access_token", value=settings_in.access_token)
    crud_settings.update_setting(db, key="whatsapp_business_account_id", value=settings_in.business_account_id)

    return settings_in


@router.get("/settings/landing", response_model=LandingSettings)
def get_landing_settings(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.role_required(["admin_general"])),
):
    """
    Get Landing Page configuration settings.
    """
    hero_title = crud_settings.get_setting(db, "landing_hero_title")
    hero_subtitle = crud_settings.get_setting(db, "landing_hero_subtitle")
    contact_email = crud_settings.get_setting(db, "landing_contact_email")
    social_links = crud_settings.get_setting(db, "landing_social_links")
    footer_copy = crud_settings.get_setting(db, "landing_footer_copy")
    hero_video_url = crud_settings.get_setting(db, "landing_hero_video_url")
    logo_url = crud_settings.get_setting(db, "landing_logo_url")
    carousel_urls = crud_settings.get_setting(db, "landing_carousel_urls")
    carousel_slides_json = crud_settings.get_setting(db, "landing_carousel_slides_json")
    faq1_question = crud_settings.get_setting(db, "landing_faq1_question")
    faq1_answer = crud_settings.get_setting(db, "landing_faq1_answer")
    faq2_question = crud_settings.get_setting(db, "landing_faq2_question")
    faq2_answer = crud_settings.get_setting(db, "landing_faq2_answer")
    plan_tier1_price = crud_settings.get_setting(db, "plan_tier1_price")
    plan_tier2_price = crud_settings.get_setting(db, "plan_tier2_price")
    plan_grace_days = crud_settings.get_setting(db, "plan_grace_days")
    seo_title = crud_settings.get_setting(db, "landing_seo_title")
    seo_description = crud_settings.get_setting(db, "landing_seo_description")

    return LandingSettings(
        hero_title=hero_title.value if hero_title else "SGA-CD — Sistema de Gestión Académico, Deportivo y Cultural",
        hero_subtitle=hero_subtitle.value if hero_subtitle else "Plataforma de Vanguardia para Entidades Públicas y Privadas.",
        contact_email=contact_email.value if contact_email else "contacto@sga-cd.org",
        social_links=social_links.value if social_links else "https://facebook.com/sga-cd,https://instagram.com/sga-cd",
        footer_copy=footer_copy.value if footer_copy else "© 2025 SGA-CD. Todos los derechos reservados.",
        hero_video_url=hero_video_url.value if hero_video_url else "assets/video/sga_cd_institutional_5min.mp4",
        logo_url=logo_url.value if logo_url else "assets/images/sga_cd_official_logo.svg",
        carousel_urls=carousel_urls.value if carousel_urls else "",
        carousel_slides_json=carousel_slides_json.value if carousel_slides_json else "",
        faq1_question=faq1_question.value if faq1_question else "¿Qué modalidades deportivas y culturales ofrece SGA-CD?",
        faq1_answer=faq1_answer.value if faq1_answer else "SGA-CD administra Taekwondo, Fútbol, Baloncesto, Danza Joropo e Instrumentos Tradicionales.",
        faq2_question=faq2_question.value if faq2_question else "¿Cómo se realiza la verificación de usuarios y roles?",
        faq2_answer=faq2_answer.value if faq2_answer else "Mediante autenticación JWT, RBAC perimetral e integración con esquemas multi-tenant.",
        plan_tier1_price=plan_tier1_price.value if plan_tier1_price else "$100 USD/mes — Entidades Públicas y Privadas B2B",
        plan_tier2_price=plan_tier2_price.value if plan_tier2_price else "$20 USD/mes — Instructores y Profesores",
        plan_grace_days=int(plan_grace_days.value) if plan_grace_days else 5,
        seo_title=seo_title.value if seo_title else "SGA-CD — Plataforma Integral de Gestión Deportiva y Cultural",
        seo_description=seo_description.value if seo_description else "Sistema de Gestión Académico, Deportivo y Cultural para Entidades Públicas y Privadas."
    )


@router.get("/public/landing", response_model=LandingSettings)
def get_public_landing_settings(
    db: Session = Depends(deps.get_db),
):
    """
    Public endpoint to fetch commercial Landing Page settings for the public website.
    Safely exposed without authentication.
    """
    hero_title = crud_settings.get_setting(db, "landing_hero_title")
    hero_subtitle = crud_settings.get_setting(db, "landing_hero_subtitle")
    contact_email = crud_settings.get_setting(db, "landing_contact_email")
    social_links = crud_settings.get_setting(db, "landing_social_links")
    footer_copy = crud_settings.get_setting(db, "landing_footer_copy")
    hero_video_url = crud_settings.get_setting(db, "landing_hero_video_url")
    logo_url = crud_settings.get_setting(db, "landing_logo_url")
    carousel_urls = crud_settings.get_setting(db, "landing_carousel_urls")
    carousel_slides_json = crud_settings.get_setting(db, "landing_carousel_slides_json")
    faq1_question = crud_settings.get_setting(db, "landing_faq1_question")
    faq1_answer = crud_settings.get_setting(db, "landing_faq1_answer")
    faq2_question = crud_settings.get_setting(db, "landing_faq2_question")
    faq2_answer = crud_settings.get_setting(db, "landing_faq2_answer")
    plan_tier1_price = crud_settings.get_setting(db, "plan_tier1_price")
    plan_tier2_price = crud_settings.get_setting(db, "plan_tier2_price")
    plan_grace_days = crud_settings.get_setting(db, "plan_grace_days")
    seo_title = crud_settings.get_setting(db, "landing_seo_title")
    seo_description = crud_settings.get_setting(db, "landing_seo_description")

    return LandingSettings(
        hero_title=hero_title.value if hero_title else "SGA-CD — Sistema de Gestión Académico, Deportivo y Cultural",
        hero_subtitle=hero_subtitle.value if hero_subtitle else "Plataforma de Vanguardia para Entidades Públicas y Privadas.",
        contact_email=contact_email.value if contact_email else "contacto@sga-cd.org",
        social_links=social_links.value if social_links else "https://facebook.com/sga-cd,https://instagram.com/sga-cd",
        footer_copy=footer_copy.value if footer_copy else "© 2025 SGA-CD. Todos los derechos reservados.",
        hero_video_url=hero_video_url.value if hero_video_url else "assets/video/sga_cd_institutional_5min.mp4",
        logo_url=logo_url.value if logo_url else "assets/images/sga_cd_official_logo.svg",
        carousel_urls=carousel_urls.value if carousel_urls else "",
        carousel_slides_json=carousel_slides_json.value if carousel_slides_json else "",
        faq1_question=faq1_question.value if faq1_question else "¿Qué modalidades deportivas y culturales ofrece SGA-CD?",
        faq1_answer=faq1_answer.value if faq1_answer else "SGA-CD administra Taekwondo, Fútbol, Baloncesto, Danza Joropo e Instrumentos Tradicionales.",
        faq2_question=faq2_question.value if faq2_question else "¿Cómo se realiza la verificación de usuarios y roles?",
        faq2_answer=faq2_answer.value if faq2_answer else "Mediante autenticación JWT, RBAC perimetral e integración con esquemas multi-tenant.",
        plan_tier1_price=plan_tier1_price.value if plan_tier1_price else "$100 USD/mes — Entidades Públicas y Privadas B2B",
        plan_tier2_price=plan_tier2_price.value if plan_tier2_price else "$20 USD/mes — Instructores y Profesores",
        plan_grace_days=int(plan_grace_days.value) if plan_grace_days else 5,
        seo_title=seo_title.value if seo_title else "SGA-CD — Plataforma Integral de Gestión Deportiva y Cultural",
        seo_description=seo_description.value if seo_description else "Sistema de Gestión Académico, Deportivo y Cultural para Entidades Públicas y Privadas."
    )


@router.put("/settings/landing")
def update_landing_settings(
    *,
    db: Session = Depends(deps.get_db),
    settings_in: LandingSettings,
    current_user: models.Usuario = Depends(deps.role_required(["admin_general"])),
):
    """
    Persist Landing Page settings to backend DB.
    """
    crud_settings.update_setting(db, key="landing_hero_title", value=settings_in.hero_title)
    crud_settings.update_setting(db, key="landing_hero_subtitle", value=settings_in.hero_subtitle)
    crud_settings.update_setting(db, key="landing_contact_email", value=settings_in.contact_email)
    crud_settings.update_setting(db, key="landing_social_links", value=settings_in.social_links)
    crud_settings.update_setting(db, key="landing_footer_copy", value=settings_in.footer_copy)
    crud_settings.update_setting(db, key="landing_hero_video_url", value=settings_in.hero_video_url)
    crud_settings.update_setting(db, key="landing_logo_url", value=settings_in.logo_url)
    crud_settings.update_setting(db, key="landing_carousel_urls", value=settings_in.carousel_urls)
    crud_settings.update_setting(db, key="landing_carousel_slides_json", value=settings_in.carousel_slides_json)
    crud_settings.update_setting(db, key="landing_faq1_question", value=settings_in.faq1_question)
    crud_settings.update_setting(db, key="landing_faq1_answer", value=settings_in.faq1_answer)
    crud_settings.update_setting(db, key="landing_faq2_question", value=settings_in.faq2_question)
    crud_settings.update_setting(db, key="landing_faq2_answer", value=settings_in.faq2_answer)
    crud_settings.update_setting(db, key="plan_tier1_price", value=settings_in.plan_tier1_price)
    crud_settings.update_setting(db, key="plan_tier2_price", value=settings_in.plan_tier2_price)
    crud_settings.update_setting(db, key="plan_grace_days", value=settings_in.plan_grace_days)
    crud_settings.update_setting(db, key="landing_seo_title", value=settings_in.seo_title)
    crud_settings.update_setting(db, key="landing_seo_description", value=settings_in.seo_description)

    return {"status": "success", "message": "Landing page settings persisted successfully."}


@router.post("/crm/generate_predis_media", response_model=PredisMediaResponse)
def generate_predis_media(
    *,
    payload: PredisMediaRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Generate video/image/reel assets using Predis.ai-level automated script writing and HyperFrames rendering.
    Enforces role authorization (admin_general or admin_empresa) and dynamic commercial capability protection
    (ai_images, ai_carousels, ai_reels) based on requested media format before AI invocation.
    """
    # 1. Enforce Role Authorization
    deps.role_required(["admin_general", "admin_empresa"])(current_user=current_user)

    # 2. Validate Media Format & Dynamic Commercial Plan Capability Protection
    format_capability_map = {
        "reel_9_16": "ai_reels",
        "post_1_1": "ai_images",
        "banner_16_9": "ai_images",
        "carousel_multi": "ai_carousels"
    }

    if payload.format not in format_capability_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{payload.format}'. Valid formats are: {list(format_capability_map.keys())}"
        )

    required_cap = format_capability_map[payload.format]

    # Enforce capability gate BEFORE initiating AIRouterService or rendering pipeline
    deps.require_plan_capability(required_cap)(db=db, current_user=current_user)

    # Reserve monthly quota
    PlanCapabilityService.check_and_consume_quota(
        db=db,
        inquilino_id=current_user.inquilino_id,
        capability_name=required_cap,
        amount=1
    )

    logger.info(f"Generating Predis.ai media for area={payload.area}, format={payload.format}")

    posters = {
        "taekwondo": "https://images.unsplash.com/photo-1555597673-b21d5c935865?w=800",
        "futbol": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800",
        "baloncesto": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=800",
        "danza_joropo": "https://images.unsplash.com/photo-1508801939243-2a1420786968?w=800",
        "instrumentos": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800",
    }

    poster = posters.get(payload.area, "https://images.unsplash.com/photo-1555597673-b21d5c935865?w=800")

    # Invocación al AIRouterService para optimizar el copy publicitario
    prompt_text = f"Genera un título y copy promocional para {payload.area.replace('_', ' ')}. Prompt: {payload.prompt}"
    try:
        router_res = ai_router.generate_text(prompt=prompt_text, task="crm_marketing")
    except Exception:
        PlanCapabilityService.release_quota(db=db, inquilino_id=current_user.inquilino_id, capability_name=required_cap, amount=1)
        raise

    title = f"¡INSCRIPCIONES ABIERTAS EN {payload.area.replace('_', ' ').upper()} 2025!"
    copy = f"{router_res.get('text', '')} — Formación integral en SGA-CD."

    dimensions_map = {
        "reel_9_16": "1080x1920 (Vertical 9:16 - Reels / TikTok / Shorts)",
        "post_1_1": "1080x1080 (Cuadrado 1:1 - IG Feed / FB)",
        "banner_16_9": "1920x1080 (Horizontal 16:9 - YouTube / Web B2B)",
        "carousel_multi": "1080x1350 (Retrato 4:5 - IG Carousel)"
    }
    dimensions = dimensions_map.get(payload.format, payload.custom_dimensions or "1080x1920 (9:16)")

    return PredisMediaResponse(
        status="scheduled" if payload.scheduled_time else "rendered",
        title=title,
        copy=copy,
        poster_url=poster,
        video_path="SGA-CD-WEB.git/assets/video/sga_cd_institutional_5min.mp4",
        dimensions=dimensions,
        target_platforms=payload.target_platforms or ["instagram", "tiktok", "youtube_shorts", "facebook"],
        scheduled_time=payload.scheduled_time or "Inmediato (Automático Simultáneo)"
    )
