import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import EconomicNode, EconomicFlow

logger = logging.getLogger(__name__)

class RiskContainmentService:
    """
    Sistema Inmunológico Económico (Fase 18.5).
    Gestiona compartimentación y aislamiento automático ante shocks.
    """

    @staticmethod
    @transaction.atomic
    def analyze_systemic_contagion():
        """
        Evalúa si un shock en un nodo se está propagando por el ecosistema.
        Si RiskIndex > Threshold, activa aislamiento.
        """
        nodes = EconomicNode.objects.filter(status='ACTIVE')
        isolated_count = 0

        for node in nodes:
            # Propagate risk from upstream supply nodes
            # If an upstream node is under SHOCK, current node's risk increases
            upstream_shocks = node.supply_dependencies

            # Simple simulation: Check if any upstream node ID is in the "Shock" list
            # node.supply_dependencies could be a list of IDs or names
            # For this MVP, we analyze real node objects linked by Flows
            for flow in node.incoming_flows.filter(source_node__status='SHOCK'):
                node.risk_index += Decimal('0.30') # Risk increase by 30% per shock source
                logger.warning(f"Risk Service: Contagion detected in {node.name} from {flow.source_node.name}")

            if node.risk_index >= Decimal('0.85'):
                # Critical risk detected -> Trigger Auto-Isolation (Compartimentación)
                RiskContainmentService.isolate_node(node.id, "Systemic Contagion Risk")
                isolated_count += 1

        return isolated_count

    @staticmethod
    @transaction.atomic
    def isolate_node(node_id, reason="Manual"):
        """
        Aísla un nodo suspendiendo flujos económicos críticos para prevenir contagio.
        """
        node = EconomicNode.objects.get(id=node_id)
        node.status = 'ISOLATED'
        node.save()

        # Suspend all outgoing flows to protect the ecosystem
        node.outgoing_flows.filter(is_active=True).update(is_active=False)

        logger.error(f"Risk Service: ISOLATED NODE {node.name}. Reason: {reason}")

        # Trigger systemic alert to Control Tower
        from apps.control_tower.application.anomaly_service import AnomalyService
        AnomalyService.detect_anomaly(
            metric="node_isolation",
            value=1.0,
            threshold=0.0,
            severity="CRITICAL",
            description=f"Automated Isolation of Node {node.name} due to {reason}"
        )

        return node

    @staticmethod
    @transaction.atomic
    def simulate_macro_shock(shock_type='FX_SHOCK', intensity=0.5):
        """
        Simulación Escenarios Macro (Fase 18.7).
        Afecta Revenue/Costs de todos los nodos según el tipo de shock.
        """
        nodes = EconomicNode.objects.filter(status='ACTIVE')

        for node in nodes:
            node.status = 'SHOCK'
            if shock_type == 'FX_SHOCK':
                # Costs increase by intensity if importing
                node.current_cost *= (Decimal('1.0') + Decimal(str(intensity)))
            elif shock_type == 'SUPPLY_CHAIN_SHOCK':
                # Efficiency drops
                node.efficiency_score *= (Decimal('1.0') - Decimal(str(intensity)))

            node.save()

        logger.info(f"Risk Service: Macro Shock {shock_type} applied with intensity {intensity}")

        # Run systemic evaluation after shock
        return RiskContainmentService.analyze_systemic_contagion()
