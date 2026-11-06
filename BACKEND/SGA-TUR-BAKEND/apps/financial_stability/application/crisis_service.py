import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import CrisisCase, RiskAnalyticsNode

logger = logging.getLogger(__name__)

class CrisisContainmentService:
    """
    Crisis Containment & Segmentation Protocol - Phase 25.5.
    Identifica epicentros de crisis y activa aislamiento automático.
    """

    @staticmethod
    @transaction.atomic
    def initiate_containment_protocol(node_id, magnitude):
        """
        Inicia el protocolo automático ante crisis sistémica.
        """
        node = RiskAnalyticsNode.objects.get(id=node_id)

        crisis = CrisisCase.objects.create(
            epicenter_node=node,
            crisis_magnitude=Decimal(str(magnitude)),
            containment_status='IDENTIFIED'
        )

        logger.error(f"Crisis Containment: IDENTIFIED epicentre in {node.region_code}. Magnitude: {magnitude}")

        # 1. Active Segmentation (Aislamiento parcial)
        CrisisContainmentService._activate_segmentation(crisis)

        # 2. Activate regional buffers via LSN
        from .liquidity_service import LiquidityStabilizationService
        LiquidityStabilizationService.activate_contingency_liquidity(node_id)

        # Notify Control Tower (Phase C)
        from apps.control_tower.application.anomaly_service import AnomalyService
        AnomalyService.detect_anomaly(
            metric="financial_stability_crisis",
            value=float(magnitude),
            threshold=0.8,
            severity="CRITICAL",
            description=f"Global Financial Crisis Protocol activated for {node.region_code}"
        )

        return crisis

    @staticmethod
    def _activate_segmentation(crisis):
        """
        Aísla temporalmente el nodo epicentro para detener el contagio.
        """
        crisis.containment_status = 'ISOLATING'
        crisis.isolated_nodes_count = 1
        crisis.save()

        # Simulation: Neutralize interconnectedness
        node = crisis.epicenter_node
        node.interconnectedness_score = Decimal('0.05')
        node.save()

        logger.warning(f"Crisis Containment: Epicenter {node.region_code} isolated. Interconnectedness neutralized.")

    @staticmethod
    def resolve_stability_crisis(crisis_id, report_text):
        """
        Restaura la estabilidad tras la contención del shock.
        """
        crisis = CrisisCase.objects.get(id=crisis_id)
        crisis.containment_status = 'RESOLVED'
        crisis.time_to_containment = timezone.now() - crisis.created_at
        crisis.resolution_report = report_text
        crisis.save()

        logger.info(f"Crisis Containment: Stability RESTORED for case {crisis_id}.")
        return True
