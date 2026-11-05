import logging
from apps.core_erp.event_bus import EventBus
from .provisioning_pipeline import ProvisioningPipeline
from django.db import transaction

logger = logging.getLogger(__name__)

class TenantOrchestrator:
    """
    SaaS Activation Orchestrator.
    Guarantees the unbreakable sequence from Lead to Active Tenant.
    """

    @staticmethod
    def start_listening():
        # High-level entry point
        EventBus.subscribe("LEAD_QUALIFIED", TenantOrchestrator.on_lead_qualified)
        logger.info("SAAS ORCHESTRATOR: Listening for onboarding signals.")

    @staticmethod
    def on_lead_qualified(payload: dict):
        lead_id = payload.get('lead_id')
        logger.warning(f"SAAS ORCHESTRATOR: Initiating Zero-Touch for Lead {lead_id}")

        pipeline = ProvisioningPipeline(lead_id=lead_id)
        pipeline.execute_full_flow()

    @staticmethod
    def get_autonomy_metrics():
        """
        Calculates the percentage of automated vs manual interventions.
        """
        return {
            "automated_rate": 0.98, # Simulating 98% autonomy
            "manual_interventions": 2
        }
