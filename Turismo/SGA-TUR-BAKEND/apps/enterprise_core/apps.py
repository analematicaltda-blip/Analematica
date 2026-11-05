from django.apps import AppConfig

class EnterpriseCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.enterprise_core'
    verbose_name = 'Enterprise Core - Decision Engine'

    def ready(self):
        from .services.metric_listener import MetricListener
        MetricListener.start_listening()
