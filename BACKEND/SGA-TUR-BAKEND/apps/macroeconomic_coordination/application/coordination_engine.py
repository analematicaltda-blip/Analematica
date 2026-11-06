import logging
import hashlib
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import CapitalCoordinationNode, StabilizationProtocol

logger = logging.getLogger(__name__)

class CoordinationEngineService:
    """
    Liquidity & Capital Coordination Engine - Phase 24.3.
    Simula flujos de capital y coordina mecanismos privados de estabilización.
    """

    @staticmethod
    @transaction.atomic
    def simulate_capital_flows(node_id, stress_scenario='VOLATILITY_SPIKE'):
        """
        Simula flujos de capital bajo escenarios de estrés y recomienda buffers.
        """
        node = CapitalCoordinationNode.objects.get(id=node_id)

        # Simulation logic
        if stress_scenario == 'VOLATILITY_SPIKE':
            required_buffer = node.current_private_buffer * Decimal('0.30')
        else:
            required_buffer = node.current_private_buffer * Decimal('0.10')

        node.required_stabilization_buffer = required_buffer
        node.last_flow_simulation_hash = hashlib.sha256(f"{stress_scenario}-{timezone.now()}".encode()).hexdigest()

        if node.current_private_buffer < required_buffer:
            node.status = 'UNDER_BUFFERED'
            logger.warning(f"Coordination Engine: {node.name} requires buffer injection of {required_buffer - node.current_private_buffer}")
        else:
            node.status = 'STABLE'

        node.save()
        return required_buffer

    @staticmethod
    @transaction.atomic
    def activate_stabilization_protocol(protocol_code, reason="Manual"):
        """
        Activa un protocolo de estabilización conjunto Holding-Estado.
        """
        protocol = StabilizationProtocol.objects.get(protocol_code=protocol_code)

        # Logic: Verify activation threshold against current systemic risk
        # from .risk_service import SystemicRiskService
        # risk = SystemicRiskService.get_last_risk()

        protocol.last_activation_date = timezone.now()
        protocol.save()

        logger.warning(f"Coordination Engine: PROTOCOL {protocol_code} ACTIVATED. Reason: {reason}")

        # Action Plan Execution (Simulation)
        for action in protocol.action_plan.get('steps', []):
            logger.info(f"Coordination Engine: Executing stabilization step: {action}")

        return True

    @staticmethod
    def redistribute_private_liquidity(source_node_id, target_node_id, amount):
        """
        Redirige liquidez interna entre nodos de coordinación para cubrir cuellos de botella.
        """
        source = CapitalCoordinationNode.objects.get(id=source_node_id)
        target = CapitalCoordinationNode.objects.get(id=target_node_id)

        if source.current_private_buffer >= amount:
            source.current_private_buffer -= amount
            target.current_private_buffer += amount
            source.save()
            target.save()

            logger.info(f"Coordination Engine: Redistributed {amount} from {source.name} to {target.name}")
            return True
        return False
