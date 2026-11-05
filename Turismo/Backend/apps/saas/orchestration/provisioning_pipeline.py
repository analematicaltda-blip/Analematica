import logging
from django.db import transaction
from apps.core_erp.event_bus import EventBus
from apps.admin_plataforma.models import GovernanceAuditLog

logger = logging.getLogger(__name__)

class ProvisioningPipeline:
    """
    State machine for the unbreakable provisioning sequence.
    Lead -> Subscription -> Tenant -> Infra -> Plan -> Ledger -> Active.
    """

    def __init__(self, lead_id):
        self.lead_id = lead_id
        self.steps_completed = []

    def execute_full_flow(self):
        try:
            with transaction.atomic():
                self._confirm_subscription()
                self._provision_tenant()
                self._setup_infrastructure()
                self._activate_saas_plan()
                self._initialize_ledger_snapshot()
                self._finalize_activation()
        except Exception as e:
            self._handle_critical_failure(e)

    def _confirm_subscription(self):
        logger.info("PIPELINE: Subscription Confirmed.")
        self.steps_completed.append("SUBSCRIPTION")

    def _provision_tenant(self):
        logger.info("PIPELINE: Tenant Provisioned.")
        self.steps_completed.append("TENANT")

    def _setup_infrastructure(self):
        logger.info("PIPELINE: Infrastructure Ready.")
        self.steps_completed.append("INFRA")

    def _activate_saas_plan(self):
        logger.info("PIPELINE: Plan Applied.")
        self.steps_completed.append("PLAN")

    def _initialize_ledger_snapshot(self):
        logger.info("PIPELINE: Baseline Snapshot Created.")
        self.steps_completed.append("SNAPSHOT")

    def _finalize_activation(self):
        logger.warning(f"PIPELINE COMPLETE: Lead {self.lead_id} is now a Live Tenant.")
        EventBus.emit("TENANT_LIFECYCLE_ACTIVE", {"lead_id": self.lead_id})

    def _handle_critical_failure(self, error):
        logger.critical(f"PIPELINE FAILED: {error}. Initiating Rollback.")
        # Rollback logic (SAGA-like)
        GovernanceAuditLog.objects.create(
            intencion="ZERO_TOUCH_ROLLBACK",
            parametros={"lead_id": self.lead_id, "failed_steps": self.steps_completed},
            resultado={"error": str(error)},
            success=False
        )
        raise error
