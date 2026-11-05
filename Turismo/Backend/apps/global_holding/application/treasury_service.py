import logging
from decimal import Decimal
from ..domain.models import TreasuryPosition
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class GlobalTreasuryService:
    """
    Multi-Currency Autonomous Treasury (Phase 10).
    Manages global cash pooling and FX hedging automatically.
    """

    @staticmethod
    def run_cash_pooling(tenant_id):
        """
        Aggregates cash balances from multiple currencies and entities.
        """
        positions = TreasuryPosition.objects.filter(tenant_id=tenant_id)

        for pos in positions:
            logger.info(f"Global Treasury: Analyzing position for {pos.currency}")

            # Logic: If exposure > 20%, activate a hedge
            if pos.exposure_pct > Decimal('0.2000'):
                GlobalTreasuryService._activate_fx_hedge(tenant_id, pos)

    @staticmethod
    def _activate_fx_hedge(tenant_id, position):
        """
        Triggers an automated hedging operation.
        """
        hedge_amount = position.total_balance * Decimal('0.5') # Hedge 50% of exposure

        logger.warning(f"Global Treasury: ACTIVATING HEDGE for {position.currency} (Amount: {hedge_amount})")

        position.hedged_amount += hedge_amount
        position.save()

        EventBus.emit("GLOBAL_FX_HEDGE_ACTIVATED", {
            "tenant_id": str(tenant_id),
            "currency": position.currency,
            "hedge_amount": str(hedge_amount)
        })

    @staticmethod
    def execute_global_netting(tenant_id):
        """
        Clears intercompany debts to minimize FX conversion fees.
        """
        pass
