from django.apps import AppConfig

class ControlTowerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.control_tower'
    verbose_name = 'Control Tower - Executive Governance'

    def ready(self):
        # Registration of event listeners for Phase C
        from .application.monitoring_service import MonitoringService
        MonitoringService.register_handlers()

        # Signals for Alert Dispatching
        import apps.control_tower.signals

        # EOS Activation: Metric Registry & Listener
        from .metric_listener import MetricListener
        MetricListener.start_listening()
