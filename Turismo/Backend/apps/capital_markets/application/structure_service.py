import logging
from decimal import Decimal
from django.utils import timezone
from ..domain.models import CapitalStructure, MarketRating
from apps.core_erp.accounting.reports_engine import ReportsEngine

logger = logging.getLogger(__name__)

class CapitalStructureOptimizationService:
    """
    Capital Structure Optimization Engine (CSOE) of Phase 16.
    Calculates WACC and recommends strategic capital adjustments.
    """

    @staticmethod
    def recalculate_wacc(tenant_id):
        """
        WACC = (E/V * Re) + (D/V * Rd * (1-T))
        """
        struct = CapitalStructure.objects.filter(tenant_id=tenant_id).first()
        if not struct: return

        # 1. Fetch market rates (Simulated for Phase 16)
        tax_rate = Decimal('0.33')
        cost_of_equity = Decimal('0.12') # Re
        cost_of_debt = Decimal('0.06')   # Rd

        total_value = struct.total_equity + struct.total_debt
        if total_value == 0: return

        equity_weight = struct.total_equity / total_value
        debt_weight = struct.total_debt / total_value

        # WACC calculation
        wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))

        struct.wacc = wacc
        struct.debt_to_equity = struct.total_debt / struct.total_equity if struct.total_equity > 0 else 0
        struct.save()

        logger.info(f"Capital Markets: WACC recalculated for {tenant_id}: {wacc:.4f}")
        return struct

    @staticmethod
    def suggest_optimizations(tenant_id):
        """
        Recommends refinancing or buybacks based on leverage targets.
        """
        struct = CapitalStructure.objects.filter(tenant_id=tenant_id).first()
        if not struct: return

        # If debt is too low compared to target, recommend bond issuance to lower WACC (tax shield)
        if struct.debt_to_equity < (struct.target_leverage * Decimal('0.8')):
            return {
                "recommendation": "BOND_ISSUANCE",
                "reason": "Current leverage is below optimal tax-shield target. Issuing debt will lower WACC.",
                "target_amount": str(struct.total_equity * Decimal('0.2'))
            }

        # If debt is too high, recommend buyback or deleveraging
        if struct.debt_to_equity > (struct.target_leverage * Decimal('1.2')):
            return {
                "recommendation": "DEBT_REPAYMENT",
                "reason": "Leverage exceeds risk threshold. High probability of rating downgrade.",
                "target_amount": str(struct.total_debt * Decimal('0.15'))
            }

        return {"recommendation": "MAINTAIN", "reason": "Capital structure is within optimal bounds."}
