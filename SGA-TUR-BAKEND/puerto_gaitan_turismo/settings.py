"""
Django settings for puerto_gaitan_turismo project.
"""

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Soporte e integración de microservicios ERP de GATuristica
import sys
import types
import importlib.util

REPO_ROOT = BASE_DIR.parent
GATURISTICA_BACKEND = REPO_ROOT / 'SGA-ERP-TUR-BAKEND'
if GATURISTICA_BACKEND.exists() and str(GATURISTICA_BACKEND) not in sys.path:
    sys.path.insert(0, str(GATURISTICA_BACKEND))
    # Vincular paquete apps.prestadores.mi_negocio al directorio SGA-ERP-TUR-BAKEND
    if 'apps.prestadores' not in sys.modules:
        apps_prestadores = types.ModuleType('apps.prestadores')
        apps_prestadores.__path__ = []
        sys.modules['apps.prestadores'] = apps_prestadores
    if 'apps.prestadores.mi_negocio' not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            'apps.prestadores.mi_negocio',
            str(GATURISTICA_BACKEND / '__init__.py'),
            submodule_search_locations=[str(GATURISTICA_BACKEND)]
        )
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules['apps.prestadores.mi_negocio'] = mod
            spec.loader.exec_module(mod)


# Cargar variables de entorno desde .env (para desarrollo local).
load_dotenv()

# --- Configuración de Seguridad y Entorno ---

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure--20v8f1jb-!a8l@l9-lnfqiebalcvq8rut^mj8@_m-uso36uop"
)

FIELD_ENCRYPTION_KEY = os.environ.get(
    "DJANGO_FIELD_ENCRYPTION_KEY",
    "pU4Wtwp-25i8a5v9M4wVw2H6jP5a_X-m3Nq8y7bK_cE="
).encode()

DEBUG = True

ALLOWED_HOSTS_str = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,.localhost,testserver")
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_str.split(",")]

# --- CSRF y Seguridad ---
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "daphne",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Terceros
    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "dj_rest_auth",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "anymail",
    "django_filters",
    "channels",
    "modeltranslation",

    # Mis Apps Core
    "api.apps.ApiConfig",
    "apps.core_erp.apps.CoreErpConfig",
    "apps.domain_business.apps.DomainBusinessConfig",
    "apps.prestadores.apps.PrestadoresConfig",
    "apps.core.catalogs.apps.CatalogsConfig",

    # Módulos de "Mi Negocio"
    "apps.prestadores.mi_negocio.gestion_comercial.apps.GestionComercialConfig",
    "apps.prestadores.mi_negocio.gestion_financiera.apps.GestionFinancieraConfig",
    "apps.prestadores.mi_negocio.gestion_contable.empresa.apps.EmpresaConfig",
    "apps.prestadores.mi_negocio.gestion_contable.nomina.apps.NominaConfig",
    "apps.prestadores.mi_negocio.gestion_contable.cierres.apps.CierresConfig",

    # Submódulos de Contabilidad
    "apps.prestadores.mi_negocio.gestion_contable.activos_fijos.apps.ActivosFijosConfig",
    "apps.prestadores.mi_negocio.gestion_contable.compras.apps.ComprasConfig",
    "apps.prestadores.mi_negocio.gestion_contable.contabilidad.apps.ContabilidadConfig",
    "apps.prestadores.mi_negocio.gestion_contable.inventario.apps.InventarioConfig",

    # Módulos de "Mi Negocio" - Implementados
    "apps.prestadores.mi_negocio.facturacion.apps.FacturacionConfig",
    "apps.companies.apps.CompaniesConfig",
    "apps.audit.apps.AuditConfig",
    "apps.prestadores.mi_negocio.gestion_archivistica.apps.GestionArchivisticaConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.sg_sst.apps.SgsstConfig",

    # Gestión Operativa Especializada (Normalizada Fase 8.5)
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.agencias.apps.AgenciasConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.agencias_de_viajes.apps.AgenciasDeViajesConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.alojamientos.apps.AlojamientosConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.arrendadoras_vehiculos.apps.ArrendadorasVehiculosConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.eventos.apps.EventosConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.gastronomia.apps.GastronomiaConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.guias.apps.GuiasConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.hoteles.apps.HotelesConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.operadores_turisticos.apps.OperadoresTuristicosConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.restaurantes.apps.RestaurantesConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.sitios_turisticos.apps.SitiosTuristicosConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.transporte.apps.TransporteConfig",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.transportes.apps.TransportesConfig",

    # App para el panel de administración de la plataforma
    "apps.admin_plataforma.apps.AdminPlataformaConfig",
    "apps.admin_plataforma.gestion_financiera.apps.AdminGestionFinancieraConfig",
    "apps.admin_plataforma.gestion_archivistica.apps.AdminGestionArchivisticaConfig",
    "apps.admin_plataforma.gestion_contable.contabilidad.apps.AdminContabilidadConfig",
    "apps.admin_plataforma.gestion_contable.inventario.apps.AdminInventoryConfig",
    "apps.admin_plataforma.gestion_contable.compras.apps.AdminProcurementConfig",
    "apps.admin_plataforma.gestion_contable.activos_fijos.apps.AdminFixedAssetsConfig",
    "apps.admin_plataforma.gestion_contable.nomina.apps.AdminPayrollConfig",
    "apps.admin_plataforma.gestion_contable.empresa.apps.AdminCompanyConfig",
    "apps.admin_plataforma.gestion_contable.presupuesto.apps.AdminBudgetConfig",
    "apps.admin_plataforma.gestion_contable.proyectos.apps.AdminProjectsConfig",
    "apps.admin_plataforma.gestion_operativa.apps.AdminGestionOperativaConfig",
    "apps.comercial.apps.ComercialConfig",
    "apps.admin_control_tower.apps.AdminControlTowerConfig",
    "apps.control_tower.apps.ControlTowerConfig",
    "apps.enterprise.apps.EnterpriseConfig",
    "apps.global_holding.apps.GlobalHoldingConfig",
    "apps.capital_markets.apps.CapitalMarketsConfig",
    "apps.tokenization.apps.TokenizationConfig",
    "apps.global_orchestration.apps.GlobalOrchestrationConfig",
    "apps.institutional_layer.apps.InstitutionalLayerConfig",
    "apps.commercial_engine.apps.CommercialEngineConfig",
    "apps.usage_billing.apps.UsageBillingConfig",
    "apps.treasury_automation.apps.TreasuryAutomationConfig",
    "apps.treasury.apps.TreasuryConfig",
    "apps.capital_markets_layer.apps.CapitalMarketsLayerConfig",

    "apps.sadi_agent.apps.SadiAgentConfig",
    "apps.sarita_agents.apps.SaritaAgentsConfig",

    "apps.web_funnel.apps.WebFunnelConfig",
    "apps.decision_intelligence.apps.DecisionIntelligenceConfig",
    "apps.ecosystem_optimization.apps.EcosystemOptimizationConfig",
    "apps.finanzas.apps.FinanzasConfig",
    "apps.defense_predictive.apps.DefensePredictiveConfig",
    "apps.defense_deception.apps.DefenseDeceptionConfig",
    "apps.international_interop.apps.InternationalInteropConfig",
    "apps.peace_net.apps.PeaceNetConfig",
    "apps.operational_treaties.apps.OperationalTreatiesConfig",
    "apps.governance_live.apps.GovernanceLiveConfig",
    "apps.operational_intelligence.apps.OperationalIntelligenceConfig",
    "apps.autonomous_operations.apps.AutonomousOperationsConfig",
    "apps.corporate_structure.apps.CorporateStructureConfig",
    "apps.capital_architecture.apps.CapitalArchitectureConfig",
    "apps.strategic_treasury.apps.StrategicTreasuryConfig",
    "apps.expansion_engine.apps.ExpansionEngineConfig",
    "apps.economic_ecosystem.apps.EconomicEcosystemConfig",
    "apps.sovereign_infrastructure.apps.SovereignInfrastructureConfig",
    "apps.meta_economic_network.apps.MetaEconomicNetworkConfig",
    "apps.state_integration.apps.StateIntegrationConfig",
    "apps.transnational_governance.apps.TransnationalGovernanceConfig",
    "apps.global_digital_infrastructure.apps.GlobalDigitalInfrastructureConfig",
    "apps.macroeconomic_coordination.apps.MacroeconomicCoordinationConfig",
    "apps.financial_stability.apps.FinancialStabilityConfig",
    "apps.enterprise_core.apps.EnterpriseCoreConfig",
    "apps.enterprise_governance.apps.EnterpriseGovernanceConfig",
    "apps.saas.apps.SaasOrchestrationConfig",
    "legacy_custody.apps.LegacyCustodyConfig",

    "apps.cart.apps.CartConfig",
    "apps.orders.apps.OrdersConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.wallet.apps.WalletConfig",
    "apps.delivery.apps.DeliveryConfig",

    # Optimizaciones Financieras 2026
    "apps.banking_integration.apps.BankingIntegrationConfig",
    "apps.analytics_engine.apps.AnalyticsEngineConfig",
    "apps.tourism_map.apps.TourismMapConfig",
    "apps.operational_mobile.apps.OperationalMobileConfig",
    "apps.turismo.apps.TurismoConfig",
    "apps.tourism_marketplace.apps.TourismMarketplaceConfig",
    "apps.tourism_intelligence.apps.TourismIntelligenceConfig",
    "apps.social.apps.SocialConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "api.middleware.entity_middleware.EntityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.common.security_hardening.SecurityHardeningMiddleware",
    "apps.defense_deception.middleware.DeceptionMiddleware",
    "apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions.TenantMiddleware",
    "apps.common.observability.middleware.ObservabilityMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "puerto_gaitan_turismo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "puerto_gaitan_turismo.wsgi.application"
ASGI_APPLICATION = "puerto_gaitan_turismo.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379/0')],
        },
    },
}

# Database
if "DATABASE_URL" in os.environ:
    DATABASES = {
        "default": dj_database_url.config(conn_max_age=600, ssl_require=False)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        },
        "wallet_db": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "wallet.sqlite3",
        },
        "delivery_db": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "delivery.sqlite3",
        },
    }

DATABASE_ROUTERS = ["puerto_gaitan_turismo.routers.DatabaseRouter"]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# Traducciones con modeltranslation
gettext = lambda s: s
LANGUAGES = (
    ("es", gettext("Español")),
    ("en", gettext("English")),
    ("pt", gettext("Português")),
    ("fr", gettext("Français")),
)
MODELTRANSLATION_DEFAULT_LANGUAGE = "es"
MODELTRANSLATION_PREPOPULATE_LANGUAGE = "es"

# Archivos estáticos y media
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Modelo de usuario personalizado
AUTH_USER_MODEL = "api.CustomUser"

# Requerido por dj-rest-auth y allauth
SITE_ID = 1

# --- Configuración de Terceros ---

# DJ-REST-AUTH & DJANGO-ALLAUTH
REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "sarita-auth",
    "JWT_AUTH_REFRESH_COOKIE": "sarita-refresh",
    "JWT_AUTH_HTTPONLY": True,
    "USER_DETAILS_SERIALIZER": "api.serializers.CustomUserDetailSerializer",
    'LOGIN_SERIALIZER': 'api.serializers.CustomLoginSerializer',
    'REGISTER_SERIALIZER': 'api.auth_serializers.LocationAwareRegisterSerializer',
}

ACCOUNT_LOGIN_METHODS = ['email']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # 'mandatory' en producción
ACCOUNT_SIGNUP_FIELDS = ['email', 'password1']
ACCOUNT_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

AUTHENTICATION_BACKENDS = [
    "allauth.account.auth_backends.AuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# MFA
MFA_ENABLED = True
ACCOUNT_LOGIN_ON_MFA_PASSWORD_VERIFIED = False

# DRF
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'DEFAULT_RENDERER_CLASSES': [
        'apps.common.renderers.EnterpriseJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'EXCEPTION_HANDLER': 'apps.common.exceptions.enterprise_exception_handler',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Sarita API - Mi Negocio',
    'DESCRIPTION': 'API para los módulos del panel "Mi Negocio"',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # Limitar la generación del esquema a las rutas de mi-negocio
    'URL_PATTERNS': [
        r'^/api/v1/mi-negocio/',
        r'^/api/v1/sales/',
        r'^/api/v1/finance/',
        r'^/api/v1/operations/',
        r'^/api/v1/payroll/',
        r'^/api/v1/agents/',
        r'^/api/v1/governance/',
    ],
    # Excluir explícitamente las rutas de la API pública que tienen problemas
    'URL_PATTERNS_EXCLUDE': [
        r'^/api/',
    ]
}

# Email con anymail
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = "noreply@puertogaitan.gov.co"
    ADMINS = [("Admin", "admin@example.com")]
else:
    EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
    ANYMAIL = {"SENDGRID_API_KEY": os.environ.get("SENDGRID_API_KEY")}
    DEFAULT_FROM_EMAIL = os.environ.get(
        "DEFAULT_FROM_EMAIL", "noreply@puertogaitan.gov.co"
    )
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    if ADMIN_EMAIL:
        ADMINS = [("Admin", ADMIN_EMAIL)]
    else:
        ADMINS = []

# SIMPLE JWT CONFIGURATION (RS256)
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "RS256",
    "SIGNING_KEY": open(BASE_DIR / "keys" / "jwt-private.pem").read(),
    "VERIFYING_KEY": open(BASE_DIR / "keys" / "jwt-public.pem").read(),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# --- CELERY ---
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    'notarize-batch-every-hour': {
        'task': 'notarize_pending_documents_batch',
        'schedule': 3600.0,  # Ejecutar cada hora
    },
    'broadcast-technical-metrics-every-minute': {
        'task': 'broadcast_system_metrics_task',
        'schedule': 60.0, # Pulso técnico cada minuto
    },
}

# --- Blockchain ---
POLYGON_RPC_URL = os.environ.get("POLYGON_RPC_URL")
SIGNER_PRIVATE_KEY = os.environ.get("SIGNER_PRIVATE_KEY")
NOTARY_CONTRACT_ADDRESS = os.environ.get("NOTARY_CONTRACT_ADDRESS")
NOTARY_CONTRACT_ABI = os.environ.get("NOTARY_CONTRACT_ABI")

# --- Application Secrets ---
GLOBAL_ENCRYPTION_PEPPER = os.environ.get("GLOBAL_ENCRYPTION_PEPPER")

# --- AWS ---
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")

# --- SADI Agent ---
SADI_AGENT_LLM_MODEL = os.environ.get("SADI_AGENT_LLM_MODEL", "gpt-4-turbo")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# --- FASE 4: Observabilidad Total (Logging Estructurado) ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'apps.common.observability.logging.EnterpriseJSONFormatter',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json' if not DEBUG else 'simple',
        },
        'file_audit': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/audit.log'),
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'apps.core_erp': {
            'handlers': ['console', 'file_audit'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.sarita_agents': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING', # Reducir verbosidad en producción
            'propagate': False,
        },
    },
}

# Asegurar existencia de directorio de logs
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.makedirs(os.path.join(BASE_DIR, 'logs'))
CELERY_TASK_ALWAYS_EAGER = True

# --- FASE H: Autenticación Empresarial ---
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# MFA Enhancements
ALLAUTH_MFA_ADAPTER = "allauth.mfa.adapter.DefaultMFAAdapter"
ALLAUTH_MFA_RECOVERY_CODES_COUNT = 10

# --- FASE H: Cifrado Extremo a Extremo ---
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
