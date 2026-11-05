from django.apps import AppConfig


class EcosystemOptimizationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ecosystem_optimization"

    def ready(self):
        import apps.ecosystem_optimization.signals
