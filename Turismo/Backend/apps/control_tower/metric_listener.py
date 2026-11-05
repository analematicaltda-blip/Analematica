import logging
from apps.core_erp.event_bus import EventBus
from .models import KPI
from .alert_engine import AlertEngine

logger = logging.getLogger(__name__)

class MetricListener:
    """
    Subscribes to system events to update the Control Tower.
    Decouples observation from operational domains.
    """

    @staticmethod
    def start_listening():
        EventBus.subscribe("METRIC_COLLECTED", MetricListener.on_metric_received)
        EventBus.subscribe("ANOMALY_DETECTED", MetricListener.on_anomaly)
        logger.info("CONTROL TOWER: Metric Listener active.")

    @staticmethod
    def on_metric_received(payload: dict):
        name = payload.get('name')
        value = payload.get('value')
        tenant_id = payload.get('tenant_id')

        # Persist KPI Snapshot
        KPI.objects.create(
            name=name,
            value=value,
            category='OPERATIONAL',
            tenant_id=tenant_id
        )

        # Trigger Alert Engine evaluation
        AlertEngine.evaluate_metric(name, value, tenant_id)

    @staticmethod
    def on_anomaly(payload: dict):
        # Create blocking alerts for anomalies
        pass
