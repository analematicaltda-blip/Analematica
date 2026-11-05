import logging
from decimal import Decimal
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from ..domain.kpi import KPI
from ..domain.alert import Alert
from ..domain.threshold import Threshold

logger = logging.getLogger(__name__)

class AnomalyService:
    """
    Service for automated anomaly detection and risk evaluation.
    """

    @staticmethod
    def run_detection(tenant_id, kpi_name):
        """
        Executes anomaly detection rules for a specific KPI.
        """
        latest_kpi = KPI.objects.filter(tenant_id=tenant_id, name=kpi_name).first()
        if not latest_kpi:
            return

        # 1. Historical Baseline (Moving Average 7 days)
        baseline = KPI.objects.filter(
            tenant_id=tenant_id,
            name=kpi_name,
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).aggregate(avg_value=Avg('value'))['avg_value'] or latest_kpi.value

        # 2. Threshold Check
        thresholds = Threshold.objects.filter(tenant_id=tenant_id, kpi_name=kpi_name, is_active=True)

        for t in thresholds:
            if AnomalyService._is_violated(latest_kpi.value, baseline, t):
                AnomalyService._trigger_anomaly_alert(latest_kpi, baseline, t)

    @staticmethod
    def _is_violated(current_value, baseline, threshold):
        if threshold.operator == Threshold.Operator.GREATER_THAN:
            return current_value > threshold.value
        elif threshold.operator == Threshold.Operator.LESS_THAN:
            return current_value < threshold.value
        elif threshold.operator == Threshold.Operator.PCT_CHANGE_DROP:
            # If current value is less than X% of baseline
            limit = baseline * (threshold.value / Decimal('100.0'))
            return current_value < limit
        return False

    @staticmethod
    def _trigger_anomaly_alert(kpi, baseline, threshold):
        logger.warning(f"ANOMALY DETECTED: {kpi.name} for tenant {kpi.tenant_id}")

        Alert.objects.create(
            tenant_id=kpi.tenant_id,
            severity=threshold.severity,
            title=f"Anomaly: {kpi.name} Deviation",
            description=(
                f"Current value {kpi.value} violates threshold {threshold.operator} "
                f"against baseline {baseline:.2f}."
            ),
            entity_scope="TENANT",
            correlation_id=kpi.id
        )
