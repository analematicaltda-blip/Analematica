import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import RiskAnalyticsNode, StabilityCouncil

logger = logging.getLogger(__name__)

class RiskAnalyticsService:
    """
    Systemic Risk Analytics Grid (SRAG) - Phase 25.2.
    Calcula indicadores de estabilidad financiera global y regional.
    """

    @staticmethod
    @transaction.atomic
    def run_systemic_audit(council_id):
        """
        Ejecuta un ciclo de auditoría de riesgo sistémico global.
        GRI = Sum(Exposure * Interconnectedness * Volatility)
        """
        council = StabilityCouncil.objects.get(id=council_id)
        nodes = council.risk_nodes.all()

        global_risk_aggregate = Decimal('0')

        for node in nodes:
            # Formula: Node Risk Index
            node_risk = (node.exposure_value * node.interconnectedness_score * node.volatility_index) / Decimal('1000000')
            node.node_risk_index = node_risk.quantize(Decimal('0.0001'))
            node.save()

            global_risk_aggregate += node_risk

        logger.info(f"SRAG: Systemic Audit Complete for {council.name}. Global Risk Index: {global_risk_aggregate}")

        # Update Council Status based on Global Risk
        if global_risk_aggregate > Decimal('0.85'):
            council.monitoring_status = 'RED'
        elif global_risk_aggregate > Decimal('0.50'):
            council.monitoring_status = 'YELLOW'
        else:
            council.monitoring_status = 'GREEN'

        council.last_stability_review = timezone.now()
        council.save()

        return global_risk_aggregate

    @staticmethod
    def identify_high_risk_epicenter(council_id):
        """
        Identifica el nodo con mayor riesgo relativo para contención (Phase 25.5).
        """
        council = StabilityCouncil.objects.get(id=council_id)
        return council.risk_nodes.order_by('-node_risk_index').first()
