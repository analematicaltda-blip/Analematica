from django.apps import AppConfig

class ComercialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.comercial'
    label = 'comercial'
    verbose_name = 'Gestión Comercial Corporativa'

    def ready(self):
        import apps.comercial.signals.subscription_signals
        import apps.comercial.signals.handlers
