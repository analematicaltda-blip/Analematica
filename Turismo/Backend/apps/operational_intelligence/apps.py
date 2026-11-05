from django.apps import AppConfig

class OperationalIntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.operational_intelligence'
    verbose_name = 'Operational Intelligence'

    def ready(self):
        from .data_collector import DataCollector
        DataCollector.initialize()
