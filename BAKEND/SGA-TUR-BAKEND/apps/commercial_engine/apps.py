from django.apps import AppConfig

class CommercialEngineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.commercial_engine"

    def ready(self):
        from apps.core_erp.event_bus import EventBus
        from .pipeline_engine import PipelineEngine
        from .kpi_engine import KPIEngine

        # Registrar Suscriptores
        EventBus.subscribe('LEAD_QUALIFIED', PipelineEngine.handle_qualification)
        EventBus.subscribe('SUBSCRIPTION_ACTIVATED', KPIEngine.handle_subscription_activated)
        EventBus.subscribe('LEAD_CONVERTED', KPIEngine.handle_lead_converted)

        # Logging de inicialización
        import logging
        logger = logging.getLogger(__name__)
        logger.info("COMMERCIAL ENGINE: Suscriptores de eventos registrados.")
