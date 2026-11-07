"""Untrusted events cannot stand in for the administrator's two approvals."""
import logging
from apps.core_erp.event_bus import EventBus
from .services.wallet_service import WalletOperationUnavailable

logger=logging.getLogger(__name__)

class WalletEventHandlers:
    @staticmethod
    def handle_payment_request(payload):
        # Fail explicitly: do not let the bus mark an unexecuted payment successful.
        raise WalletOperationUnavailable()

    @staticmethod
    def register_all():
        EventBus.subscribe('WALLET_PAYMENT_REQUESTED',WalletEventHandlers.handle_payment_request)
        logger.info('Wallet event boundary registered; payment execution requires explicit approvals.')
