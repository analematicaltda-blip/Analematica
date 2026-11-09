import logging
from apps.core_erp.event_bus import EventBus
from .ledger_engine import LedgerEngine

logger = logging.getLogger(__name__)

class StandardAccountingHandlers:
    """
    Centralized event handlers for the LedgerEngine.
    Translates business events into Ledger impacts following Phase B flows.
    """

    @staticmethod
    def handle_business_event(event_type: str, payload: dict, *, actor=None):
        """
        Generic handler that delegates to LedgerEngine.
        """
        logger.info(f"Accounting Handler: Processing {event_type}")
        # Legacy producers without an authenticated/configured actor fail visibly.
        # Do not let the bus mark a failed accounting operation as processed.
        return LedgerEngine.post_event(event_type, payload, actor=actor)

    @staticmethod
    def register_all():
        """
        Registers all standard financial handlers in the EventBus.
        """
        standard_events = [
            'RESERVATION_CREATED',
            'RESERVATION_CONFIRMED',
            'RESERVATION_CANCELLED',
            'PAYMENT_RECEIVED',
            'SALE_COMPLETED',
            'PURCHASE_ORDER_POSTED',
            'PAYROLL_LIQUIDATED',
            'INVENTORY_ADJUSTED',
            'ASSET_DEPRECIATED',
            'LIQUIDATION',
            'SALE_CREATED',
            'PAYROLL_LIQUIDATED_V2',
            'SaaS_INVOICE_GENERATED',
            'BANK_FEE_REGISTERED'
        ]

        for event in standard_events:
            EventBus.subscribe(event, lambda p, et=event: StandardAccountingHandlers.handle_business_event(et, p))

        logger.info("Standard Accounting Handlers registered.")
