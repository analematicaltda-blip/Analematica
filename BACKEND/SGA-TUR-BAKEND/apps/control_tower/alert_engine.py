import logging
from .models import Alert, Threshold
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class AlertEngine:
    """
    Evaluates metrics against thresholds and generates system alerts.
    """

    @staticmethod
    def evaluate_metric(name: str, value: float, tenant_id: str):
        thresholds = Threshold.objects.filter(metric_name=name, is_active=True)

        for threshold in thresholds:
            if value >= threshold.critical_value:
                AlertEngine._create_alert(name, value, tenant_id, 'CRITICAL')
            elif value >= threshold.warning_value:
                AlertEngine._create_alert(name, value, tenant_id, 'PREVENTIVE')

    @staticmethod
    def _create_alert(metric, value, tenant_id, severity):
        alert = Alert.objects.create(
            title=f"Threshold Exceeded: {metric}",
            description=f"Value {value} exceeded configured limits for tenant {tenant_id}.",
            severity=severity,
            tenant_id=tenant_id
        )

        # Notify via EventBus for external integrations (e.g. Email, SMS)
        EventBus.emit("ALERT_GENERATED", {
            "alert_id": str(alert.id),
            "severity": severity,
            "metric": metric
        })
        logger.warning(f"ALERT GENERATED: {alert.title} ({severity})")
