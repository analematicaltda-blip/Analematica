from django.apps import AppConfig

class SaasOrchestrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.saas'
    verbose_name = 'SaaS Orchestration Engine'

    def ready(self):
        from .orchestration.tenant_orchestrator import TenantOrchestrator
        TenantOrchestrator.start_listening()
