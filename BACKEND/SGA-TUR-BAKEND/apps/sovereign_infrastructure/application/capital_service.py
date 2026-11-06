import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import JurisdictionalNode, CapitalShield

logger = logging.getLogger(__name__)

class CapitalShieldService:
    """
    Multi-Sovereign Capital Shield - Phase 19.2.
    Distribuye el capital corporativo en vehículos regionales, centros estratégicos y monedas múltiples.
    Evita concentración en una sola jurisdicción y dependencia bancaria única.
    """

    @staticmethod
    def calculate_concentration_index(jurisdiction_code):
        """
        Calcula el índice de concentración de capital en una sola jurisdicción.
        """
        total_holding_value = sum(s.current_value for s in CapitalShield.objects.all())
        jurisdiction_value = sum(s.current_value for s in CapitalShield.objects.filter(node__country_code=jurisdiction_code))

        if total_holding_value > 0:
            concentration_index = (jurisdiction_value / total_holding_value).quantize(Decimal('0.0001'))
        else:
            concentration_index = Decimal('0.0')

        logger.info(f"Capital Shield: Concentration Index for {jurisdiction_code}: {concentration_index}")
        return concentration_index

    @staticmethod
    @transaction.atomic
    def distribute_capital(total_amount, currency='USD', target_nodes_count=3):
        """
        Distribuye un nuevo monto de capital entre los nodos regionales más estables.
        """
        stable_nodes = JurisdictionalNode.objects.filter(
            level__in=['REGIONAL', 'ROOT'],
            is_active=True,
            stability_index__gt=Decimal('0.7')
        ).order_by('-stability_index')[:target_nodes_count]

        if not stable_nodes:
            logger.error("Capital Shield: No stable nodes found for capital distribution.")
            return False

        distributed_amount = total_amount / Decimal(str(stable_nodes.count()))

        for node in stable_nodes:
            # Create or update traditional capital shield
            shield, created = CapitalShield.objects.get_or_create(
                node=node,
                asset_type='TRADITIONAL',
                currency=currency,
                defaults={'current_value': Decimal('0')}
            )

            shield.current_value += distributed_amount
            shield.save()

            logger.info(f"Capital Shield: Distributed {distributed_amount} {currency} to {node.name}")

        return True

    @staticmethod
    @transaction.atomic
    def tokenize_excess_capital(node_id, threshold_amount=1000000, currency='USD'):
        """
        Tokeniza el excedente de capital tradicional para moverlo a la infraestructura programable (Fase 17).
        """
        node = JurisdictionalNode.objects.get(id=node_id)
        traditional_shield = node.capital_shields.filter(asset_type='TRADITIONAL', currency=currency).first()

        if traditional_shield and traditional_shield.current_value > threshold_amount:
            excess = traditional_shield.current_value - threshold_amount

            # 1. Update Traditional Shield
            traditional_shield.current_value -= excess
            traditional_shield.save()

            # 2. Create/Update Tokenized Shield
            tokenized_shield, created = CapitalShield.objects.get_or_create(
                node=node,
                asset_type='TOKENIZED',
                currency=f"{currency}_ON_CHAIN",
                defaults={'current_value': Decimal('0')}
            )

            tokenized_shield.current_value += excess
            tokenized_shield.save()

            logger.warning(f"Capital Shield: TOKENIZED {excess} {currency} in {node.name}")

            # 3. Trigger Token Issuance (Phase 17)
            # Placeholder for actual token issuance logic
            from apps.tokenization.application.issuance_service import IssuanceService
            IssuanceService.issue_units(node.id, str(excess), f"{currency}_TOKEN")

            return excess
        return Decimal('0')
