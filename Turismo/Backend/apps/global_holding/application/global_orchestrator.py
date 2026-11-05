import logging
from apps.core_erp.event_bus import EventBus
from .capital_allocation_service import CapitalAllocationService
from .tax_optimization_service import TaxOptimizationService
from .treasury_service import GlobalTreasuryService
from .risk_orchestrator import GlobalRiskOrchestrator

logger = logging.getLogger(__name__)

class GlobalOrchestrator:
    """
    Main entry point for Global Holding Automation (Phase 10).
    Coordinates the execution of allocation, tax, and treasury engines.
    """

    @staticmethod
    def register_handlers():
        """
        Subscribes to high-level strategic events.
        """
        EventBus.subscribe("PERIOD_CLOSED", GlobalOrchestrator.handle_global_rebalance)
        EventBus.subscribe("KPI_UPDATED", GlobalOrchestrator.handle_strategic_update)
        logger.info("Global Holding Orchestrator registered.")

    @staticmethod
    def handle_global_rebalance(payload):
        """
        Triggered on monthly close.
        """
        tenant_id = payload.get('tenant_id')
        CapitalAllocationService.run_global_rebalance(tenant_id)
        TaxOptimizationService.optimize_transfer_pricing(tenant_id)

    @staticmethod
    def handle_strategic_update(payload):
        """
        Triggered on critical KPI updates.
        """
        tenant_id = payload.get('tenant_id')
        GlobalTreasuryService.run_cash_pooling(tenant_id)
        GlobalRiskOrchestrator.monitor_systemic_risks(tenant_id)
