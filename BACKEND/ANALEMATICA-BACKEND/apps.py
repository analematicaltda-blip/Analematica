from django.apps import AppConfig

class AdminPlataformaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin_plataforma'
    label = 'admin_plataforma'

    def ready(self):
        from .gestion_comercial.pool08 import identity_models, crm_models, opportunity_models, pricing_models, quotation_models, sales_models, payment_models, landing_models, capture_models, library_models, generation_models, email_campaign_models, mobile_message_models, analytics_models,army_models,ads_models,inbox_models,publishing_models

        try:
            from apps.core_erp import CORE_ERP_VERSION
            from django.core.exceptions import ImproperlyConfigured
            EXPECTED_CORE_VERSION = "1.0.0"
            if CORE_ERP_VERSION != EXPECTED_CORE_VERSION:
                 raise ImproperlyConfigured(
                     f"CORE_ERP_VERSION mismatch in admin_plataforma. "
                     f"Expected {EXPECTED_CORE_VERSION}, found {CORE_ERP_VERSION}"
                 )
        except ImportError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("FATAL: Core ERP not found.")
