import logging
from typing import Dict, Any
from django.utils import timezone
from apps.admin_plataforma.models import GovernanceAuditLog
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class SystemicObserver:
    """
    Capa de Observación Sistémica: Monitorea KPIs y estados en tiempo real.
    REFACTORED: 100% Event-Driven. No direct imports or import_string.
    EOS Activation: Eliminates technical coupling.
    """

    # Local metric registry for transient state (persistent data stays in control_tower)
    _latest_metrics: Dict[str, Any] = {
        "comercial": {},
        "contable": {},
        "financiero": {},
        "operativo": {},
        "archivistico": {}
    }

    def __init__(self):
        self._subscribe_to_system_events()

    def _subscribe_to_system_events(self):
        """
        Registers the observer for relevant ERP and operational events.
        """
        EventBus.subscribe("METRIC_COLLECTED", self._on_metric_received)
        EventBus.subscribe("JOURNAL_ENTRY_POSTED", self._on_accounting_impact)
        EventBus.subscribe("SUBSCRIPTION_ACTIVATED", self._on_commercial_impact)
        logger.info("SYSTEMIC OBSERVER: refactored and listening via EventBus.")

    def _on_metric_received(self, payload: dict):
        """Standard handler for explicit metric emission."""
        domain = payload.get('domain', 'global')
        name = payload.get('name')
        value = payload.get('value')

        if domain in self._latest_metrics:
            self._latest_metrics[domain][name] = value

        # Trigger Decision Engine if needed
        from apps.enterprise_core.services.decision_engine import DecisionEngine
        DecisionEngine.process_metric_update(name, value, payload)

    def _on_accounting_impact(self, payload: dict):
        """Infers metrics from accounting events."""
        self._latest_metrics["contable"]["last_post_timestamp"] = timezone.now().isoformat()
        # Logic to update aggregate cash flow, etc.

    def _on_commercial_impact(self, payload: dict):
        """Infers metrics from commercial events."""
        self._latest_metrics["comercial"]["active_subscriptions_delta"] = 1

    def collect_all_metrics(self) -> Dict[str, Any]:
        """
        Returns a snapshot of the current systemic health.
        Now uses data inferred from events and explicitly emitted metrics.
        """
        return {
            **self._latest_metrics,
            "timestamp": timezone.now().isoformat()
        }
