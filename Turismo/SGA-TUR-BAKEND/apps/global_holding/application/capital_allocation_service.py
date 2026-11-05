import logging
from decimal import Decimal
from django.utils import timezone
from ..domain.models import GlobalCapitalAllocator, JurisdictionConfig
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class CapitalAllocationService:
    """
    Core strategic engine of Phase 10.
    Determines and executes capital distribution across the holding.
    """

    @staticmethod
    def run_global_rebalance(tenant_id):
        """
        Analyzes ROIC and risk country-by-country and adjusts allocation limits.
        """
        allocators = GlobalCapitalAllocator.objects.filter(tenant_id=tenant_id)

        for alloc in allocators:
            # 1. Fetch Country Autonomy
            config = JurisdictionConfig.objects.filter(country_code=alloc.country_code).first()

            # 2. Logic: If risk > 70, reduce allocation limit by 20%
            if alloc.risk_score > Decimal('70.0'):
                new_limit = alloc.allocation_limit * Decimal('0.8')
                logger.warning(f"Global Holding: Reducing allocation for {alloc.country_code} due to risk.")
                alloc.allocation_limit = new_limit
                alloc.save()

                # 3. Trigger Intercompany Repatriation if current > new limit
                if alloc.current_allocation > new_limit:
                    amount_to_repatriate = alloc.current_allocation - new_limit
                    CapitalAllocationService._repatriate_capital(tenant_id, alloc.entity_id, amount_to_repatriate)

    @staticmethod
    def _repatriate_capital(tenant_id, entity_id, amount):
        """
        Executes intercompany transfer from subsidiary to holding.
        """
        logger.info(f"Global Holding: Repatriating {amount} from entity {entity_id}")

        # Emitting global event for financial execution
        EventBus.emit("GLOBAL_CAPITAL_REPATRIATION_TRIGGERED", {
            "tenant_id": str(tenant_id),
            "source_entity_id": str(entity_id),
            "amount": str(amount),
            "reason": "Strategic risk-adjusted rebalancing"
        })
