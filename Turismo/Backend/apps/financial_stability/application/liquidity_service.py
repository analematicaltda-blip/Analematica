import logging
from decimal import Decimal
from django.db import transaction
from ..models import LiquidityBuffer, RiskAnalyticsNode

logger = logging.getLogger(__name__)

class LiquidityStabilizationService:
    """
    Liquidity Stabilization Network (LSN) - Phase 25.3.
    Maneja buffers privados y protocolos de inyección preventiva temporal.
    """

    @staticmethod
    @transaction.atomic
    def activate_contingency_liquidity(node_id):
        """
        Activa líneas de contingencia si el estrés de liquidez supera el umbral.
        """
        node = RiskAnalyticsNode.objects.get(id=node_id)
        buffers = node.buffers.filter(is_locked=False)

        # Simulation: Check node liquidity stress (derived from Risk Index)
        stress_level = node.node_risk_index

        activated_amount = Decimal('0')
        for buffer in buffers:
            if stress_level >= buffer.activation_threshold:
                # Deploy 50% of available liquidity as emergency injection
                injection = buffer.available_liquidity * Decimal('0.5')
                buffer.available_liquidity -= injection
                buffer.save()

                activated_amount += injection
                logger.warning(f"LSN: ACTIVATED {injection} from {buffer.buffer_type} for Region {node.region_code}")

        return activated_amount

    @staticmethod
    @transaction.atomic
    def rebalance_global_liquidity(council_id):
        """
        Coordina el reequilibrio de capital entre regiones para estabilizar nodos bajo estrés.
        """
        # Integration with macroeconomic_coordination (Phase 24)
        # Placeholder for complex redistribution logic
        logger.info(f"LSN: Coordinating Global Liquidity Rebalance for Council {council_id}")
        return True

    @staticmethod
    def register_stabilization_buffer(node_id, b_type, capacity):
        """
        Registra un nuevo buffer de estabilización privado en una región.
        """
        buffer = LiquidityBuffer.objects.create(
            node_id=node_id,
            buffer_type=b_type,
            total_capacity=capacity,
            available_liquidity=capacity,
            activation_threshold=Decimal('0.75') # Default Red Level
        )
        return buffer
