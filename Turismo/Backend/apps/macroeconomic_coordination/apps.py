from django.apps import AppConfig

class MacroeconomicCoordinationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.macroeconomic_coordination'
    verbose_name = 'Public-Private Macroeconomic Coordination (Phase 24)'

    def ready(self):
        # Initial SRO monitoring check
        pass
