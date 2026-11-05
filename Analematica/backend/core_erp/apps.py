from django.apps import AppConfig

class CoreErpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_erp'
    verbose_name = 'Core ERP Systemic'

    def ready(self):
        from .accounting.handlers import StandardAccountingHandlers
        StandardAccountingHandlers.register_all()

        # EOS Activation: Automated Consolidation
        from .consolidation.event_processor import ConsolidationEventProcessor
        ConsolidationEventProcessor.start_listening()

        # Hardening 100%: Tenant Lifecycle
        from .tenancy.lifecycle_engine import TenantLifecycleEngine
        TenantLifecycleEngine.start_listening()

        # Phase 4: Security Monitoring
        from api.signals import register_security_monitors
        register_security_monitors()
