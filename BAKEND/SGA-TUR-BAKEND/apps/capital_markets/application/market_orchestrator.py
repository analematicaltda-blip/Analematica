import logging
from apps.core_erp.event_bus import EventBus
from .structure_service import CapitalStructureOptimizationService
from .market_service import DebtIssuanceService, EquityStrategyService

logger = logging.getLogger(__name__)

class MarketOrchestrator:
    """
    Main entry point for Capital Markets Integration (Phase 16).
    """

    @staticmethod
    def register_handlers():
        """
        Subscribes to strategic triggers.
        """
        EventBus.subscribe("PERIOD_CLOSED", MarketOrchestrator.handle_market_review)
        logger.info("Capital Markets Orchestrator registered.")

    @staticmethod
    def handle_market_review(payload):
        """
        Recalculates WACC and structural health at close.
        """
        tenant_id = payload.get('tenant_id')
        CapitalStructureOptimizationService.recalculate_wacc(tenant_id)
