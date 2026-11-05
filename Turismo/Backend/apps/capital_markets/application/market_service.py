import logging
from decimal import Decimal
from django.utils import timezone
from ..domain.models import DebtInstrument, EquityInstrument
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class DebtIssuanceService:
    """
    Autonomous Debt Issuance Engine (Phase 16).
    Handles bond issuance and covenant monitoring.
    """

    @staticmethod
    def issue_bond(tenant_id, amount, coupon_rate, maturity_date, instrument_type='BOND'):
        """
        Registers a new debt issuance and triggers financial impact.
        """
        bond = DebtInstrument.objects.create(
            tenant_id=tenant_id,
            instrument_type=instrument_type,
            principal_amount=amount,
            coupon_rate=coupon_rate,
            maturity_date=maturity_date,
            status='ISSUED'
        )

        logger.info(f"Debt Engine: New bond issued for {tenant_id} (ID: {bond.id})")

        # Trigger Ledger Impact (Increase Cash, Increase Debt)
        EventBus.emit("DEBT_ISSUANCE_EXECUTED", {
            "tenant_id": str(tenant_id),
            "amount": str(amount),
            "instrument_id": str(bond.id)
        })

        return bond

class EquityStrategyService:
    """
    Equity Strategy Engine (Phase 16).
    Handles shares, buybacks, and secondary offerings.
    """

    @staticmethod
    def execute_share_buyback(tenant_id, amount, market_price):
        """
        De-leverages or returns capital to shareholders automatically.
        """
        logger.warning(f"Equity Engine: Executing buyback for {tenant_id} - Total {amount}")

        EventBus.emit("EQUITY_BUYBACK_TRIGGERED", {
            "tenant_id": str(tenant_id),
            "amount": str(amount),
            "market_price": str(market_price)
        })

        return "BUYBACK_INITIATED"
