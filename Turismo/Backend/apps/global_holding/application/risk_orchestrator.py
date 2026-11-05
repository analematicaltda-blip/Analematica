import logging
from ..domain.models import MacroScenario
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class GlobalRiskOrchestrator:
    """
    Global Risk Orchestration Layer (Phase 10).
    Monitors geopolitical and systemic risks.
    """

    @staticmethod
    def monitor_systemic_risks(tenant_id):
        """
        Scans active macro scenarios and triggers preventative workflows.
        """
        scenarios = MacroScenario.objects.filter(tenant_id=tenant_id, is_active_sim=True)

        for sc in scenarios:
            if sc.probability > 0.8: # High probability event
                logger.warning(f"Global Risk: HIGH PROBABILITY RISK DETECTED - {sc.title}")

                GlobalRiskOrchestrator._trigger_preventative_measures(tenant_id, sc)

    @staticmethod
    def _trigger_preventative_measures(tenant_id, scenario):
        """
        Executes structural adjustments to protect the holding.
        """
        # Logic to reduce country exposure automatically
        EventBus.emit("GLOBAL_RISK_MITIGATION_STARTED", {
            "tenant_id": str(tenant_id),
            "scenario": scenario.title,
            "risk_type": scenario.scenario_type
        })
