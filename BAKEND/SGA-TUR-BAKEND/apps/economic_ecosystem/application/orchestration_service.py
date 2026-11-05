import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import EconomicNode, EconomicFlow, InternalContract, EcosystemIncentive

logger = logging.getLogger(__name__)

class OrchestrationService:
    """
    Cerebro macroeconómico del Holding (EOE).
    Optimiza la asignación de recursos y maximiza el valor sistémico.
    """

    @staticmethod
    @transaction.atomic
    def run_ecosystem_optimization():
        """
        Ejecuta el ciclo de optimización global.
        Calcula Efficiency, Margins y Systemic Risk.
        """
        nodes = EconomicNode.objects.filter(status='ACTIVE')
        total_value = Decimal('0')
        systemic_risk_aggregate = Decimal('0')

        for node in nodes:
            # 1. Update node metrics based on flows
            OrchestrationService._update_node_performance(node)

            # 2. Calculate individual contribution
            # Value = (Efficiency * Margin) - (Risk * SystemicImportance)
            margin = node.current_revenue - node.current_cost
            efficiency = node.efficiency_score
            risk_impact = node.risk_index * node.systemic_importance

            node_contribution = OrchestrationService.calculate_node_value(node)
            total_value += node_contribution
            systemic_risk_aggregate += risk_impact

        logger.info(f"EOE: Optimization Cycle Complete. Ecosystem Value: {total_value}. Global Risk: {systemic_risk_aggregate}")
        return {
            "ecosystem_value": total_value,
            "global_risk": systemic_risk_aggregate,
            "node_count": nodes.count()
        }

    @staticmethod
    def calculate_node_value(node):
        """
        Modelo Matemático del Ecosistema (Fase 18.6).
        E_node = (Efficiency_i * Margin_i) - (SystemicRisk_i * Factor)
        """
        margin = node.current_revenue - node.current_cost
        efficiency = node.efficiency_score
        # Normalization factor for risk vs margin (systemic impact)
        risk_penalty = node.risk_index * node.systemic_importance * Decimal('1000000')
        return (efficiency * margin) - risk_penalty

    @staticmethod
    def _update_node_performance(node):
        """
        Calcula métricas de performance real basada en flujos y contratos.
        """
        # Calcular ingresos reales desde flujos entrantes y ventas internas
        incoming_value = sum(f.value_per_period for f in node.incoming_flows.filter(is_active=True))
        outgoing_value = sum(f.value_per_period for f in node.outgoing_flows.filter(is_active=True))

        # Ajustar Efficiency Score
        # Si tiene más demanda de la que puede suplir (demand_forecast > revenue), la eficiencia baja por cuellos de botella
        if node.demand_forecast > 0:
            utilization = node.current_revenue / node.demand_forecast
            if 0.8 <= utilization <= 1.1:
                node.efficiency_score = Decimal('0.95')
            elif utilization < 0.8:
                node.efficiency_score = Decimal('0.70') # Under-utilization
            else:
                node.efficiency_score = Decimal('0.85') # Over-capacity stress

        # Ajustar Risk Index basado en dependencias
        dependency_count = len(node.supply_dependencies)
        if dependency_count > 5:
            node.risk_index = Decimal('0.60') # High supply chain risk
        elif dependency_count == 0 and node.node_type == 'OPERATIONAL':
            node.risk_index = Decimal('0.80') # Critical lack of data on dependencies
        else:
            node.risk_index = Decimal('0.20')

        node.save()

    @staticmethod
    def allocate_resources(source_node_id, target_node_id, amount, flow_type='CAPITAL'):
        """
        Redirecciona dinámicamente flujos económicos entre nodos.
        """
        source = EconomicNode.objects.get(id=source_node_id)
        target = EconomicNode.objects.get(id=target_node_id)

        flow, created = EconomicFlow.objects.get_or_create(
            source_node=source,
            target_node=target,
            flow_type=flow_type,
            defaults={'value_per_period': amount}
        )

        if not created:
            flow.value_per_period = amount
            flow.save()

        logger.info(f"EOE: Reallocated {amount} {flow_type} from {source.name} to {target.name}")
        return flow
