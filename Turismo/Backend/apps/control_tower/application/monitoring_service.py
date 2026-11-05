import logging
from decimal import Decimal
from django.utils import timezone
from apps.core_erp.event_bus import EventBus
from ..domain.kpi import KPI
from ..domain.alert import Alert

logger = logging.getLogger(__name__)

class MonitoringService:
    """
    Application service for the Control Tower.
    Aggregates data across domains and manages the monitoring lifecycle.
    """

    @staticmethod
    def register_handlers():
        """
        Subscribes the Control Tower to relevant systemic events.
        """
        EventBus.subscribe("JOURNAL_POSTED", MonitoringService.handle_journal_posted)
        EventBus.subscribe("RESERVATION_CONFIRMED", MonitoringService.handle_reservation_confirmed)
        EventBus.subscribe("PAYMENT_FAILED", MonitoringService.handle_payment_failed)
        logger.info("Control Tower Monitoring Handlers registered.")

    @staticmethod
    def handle_journal_posted(payload):
        """
        Updates financial KPIs when a journal entry is posted.
        """
        tenant_id = payload.get('tenant_id')
        logger.info(f"Control Tower: Processing journal impact for tenant {tenant_id}")

        # In a real implementation, this would trigger an aggregation of Revenue/EBITDA
        MonitoringService.calculate_financial_kpis(tenant_id)

    @staticmethod
    def handle_reservation_confirmed(payload):
        """
        Updates operational KPIs.
        """
        tenant_id = payload.get('tenant_id')
        KPI.objects.create(
            tenant_id=tenant_id,
            name="DAILY_RESERVATIONS",
            category=KPI.MetricType.OPERATIONAL,
            value=Decimal('1.00'), # Incremental count in some aggregation logic
            unit="COUNT"
        )

    @staticmethod
    def handle_payment_failed(payload):
        """
        Triggers immediate strategic alerts.
        """
        tenant_id = payload.get('tenant_id')
        Alert.objects.create(
            tenant_id=tenant_id,
            severity=Alert.Severity.CRITICAL,
            title="Payment Failure Detected",
            description=f"Payment failed for reference {payload.get('reference')}. Potential revenue risk.",
            entity_scope="TENANT",
            source_event="PAYMENT_FAILED"
        )

    @staticmethod
    def calculate_financial_kpis(tenant_id):
        """
        Triggers aggregation from the Ledger.
        """
        from apps.core_erp.accounting.reports_engine import ReportsEngine

        today = timezone.now().date()
        pnl = ReportsEngine.get_p_and_l(tenant_id, today, today)

        revenue_kpi = KPI.objects.create(
            tenant_id=tenant_id,
            name="DAILY_REVENUE",
            category=KPI.MetricType.FINANCIAL,
            value=pnl['income'],
            unit="COP"
        )
        EventBus.emit("KPI_UPDATED", {
            "tenant_id": str(tenant_id),
            "name": "DAILY_REVENUE",
            "value": str(revenue_kpi.value),
            "correlation_id": str(revenue_kpi.id)
        })

        profit_kpi = KPI.objects.create(
            tenant_id=tenant_id,
            name="DAILY_NET_PROFIT",
            category=KPI.MetricType.FINANCIAL,
            value=pnl['net_profit'],
            unit="COP"
        )
        EventBus.emit("KPI_UPDATED", {
            "tenant_id": str(tenant_id),
            "name": "DAILY_NET_PROFIT",
            "value": str(profit_kpi.value),
            "correlation_id": str(profit_kpi.id)
        })
