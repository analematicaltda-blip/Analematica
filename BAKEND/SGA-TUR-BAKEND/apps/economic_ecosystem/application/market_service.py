import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import EconomicNode, InternalContract, EcosystemIncentive

logger = logging.getLogger(__name__)

class InternalMarketService:
    """
    Microeconomía Corporativa Computacional (Fase 18.2).
    Gestiona precios dinámicos, transfer pricing e incentivos sistémicos.
    """

    @staticmethod
    @transaction.atomic
    def update_internal_pricing(contract_id):
        """
        Calcula el precio dinámico óptimo para un contrato intra-holding.
        Factoriza oferta interna vs demanda externa.
        """
        contract = InternalContract.objects.get(id=contract_id)
        if contract.pricing_model != 'DYNAMIC':
            return contract.current_unit_price

        # EOE Logic: Base Cost * (1 + Efficiency_Seller) * (1 - Criticality_Buyer)
        base_cost = contract.seller.current_cost / Decimal('100') # Sample unit cost
        efficiency_factor = Decimal('1.0') + contract.seller.efficiency_score
        criticality_factor = Decimal('1.0') - contract.buyer.systemic_importance

        # New Price optimized for systemic margin
        new_price = base_cost * efficiency_factor * (Decimal('1.0') + (contract.markup_percentage / Decimal('100')))

        contract.current_unit_price = new_price
        contract.save()

        logger.info(f"MarketService: Updated Dynamic Price for Contract {contract.id} to {new_price}")
        return new_price

    @staticmethod
    @transaction.atomic
    def process_performance_incentives(node_id):
        """
        Evalúa y aplica incentivos basados en tokens (Fase 17 integration).
        """
        node = EconomicNode.objects.get(id=node_id)
        incentives = EcosystemIncentive.objects.filter(node=node, status='PENDING')

        results = []
        for incentive in incentives:
            # 1. Check if threshold is met (placeholder for complex KPI check)
            performance_kpi = node.efficiency_score * Decimal('100')

            if performance_kpi >= incentive.threshold_value:
                # 2. Grant Tokenized Reward (Integration with Phase 17)
                from apps.tokenization.application.issuance_service import IssuanceService
                try:
                    # Grant internal "PERFORMANCE" tokens
                    IssuanceService.issue_units(
                        node.entity_id or node.id,
                        str(incentive.incentive_value),
                        "ECO_PERF_TOKEN"
                    )
                    incentive.status = 'APPLIED'
                    incentive.applied_at = timezone.now()
                    incentive.save()
                    results.append(f"Applied reward for {incentive.metric_linked}")
                except Exception as e:
                    logger.error(f"Error issuing performance tokens: {e}")
                    incentive.status = 'FAILED'
                    incentive.save()
            else:
                results.append(f"Threshold not met for {incentive.metric_linked}")

        return results

    @staticmethod
    def allocate_internal_contract(buyer_id, seller_id, markup=10.0):
        """
        Formaliza una relación económica interna orquestada por el holding.
        """
        buyer = EconomicNode.objects.get(id=buyer_id)
        seller = EconomicNode.objects.get(id=seller_id)

        contract = InternalContract.objects.create(
            buyer=buyer,
            seller=seller,
            pricing_model='DYNAMIC',
            markup_percentage=Decimal(str(markup))
        )

        # Trigger initial pricing
        InternalMarketService.update_internal_pricing(contract.id)
        return contract
