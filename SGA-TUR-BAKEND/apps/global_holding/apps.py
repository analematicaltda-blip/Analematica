from django.apps import AppConfig

class GlobalHoldingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.global_holding'
    verbose_name = 'Autonomous Global Holding (Sarita Group)'

    def ready(self):
        # Registration of global orchestration listeners
        from .application.global_orchestrator import GlobalOrchestrator
        GlobalOrchestrator.register_handlers()
