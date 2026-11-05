from django.apps import AppConfig

class EconomicEcosystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.economic_ecosystem'
    verbose_name = 'Economic Ecosystem (Phase 18)'

    def ready(self):
        # Register signals for ecosystem events
        import apps.economic_ecosystem.infrastructure.signals  # noqa
