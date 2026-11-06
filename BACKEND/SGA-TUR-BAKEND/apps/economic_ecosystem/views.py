from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import EconomicNode, EconomicFlow, InternalContract, EcosystemIncentive
from .serializers import (
    EconomicNodeSerializer, EconomicFlowSerializer,
    InternalContractSerializer, EcosystemIncentiveSerializer,
    EcosystemMetricsSerializer
)
from .application.orchestration_service import OrchestrationService
from .application.market_service import InternalMarketService
from .application.risk_service import RiskContainmentService

class EconomicNodeViewSet(viewsets.ModelViewSet):
    queryset = EconomicNode.objects.all()
    serializer_class = EconomicNodeSerializer

    @action(detail=False, methods=['post'], url_path='run-optimization')
    def run_optimization(self, request):
        result = OrchestrationService.run_ecosystem_optimization()
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='isolate')
    def isolate(self, request, pk=None):
        node = RiskContainmentService.isolate_node(pk, reason="Manual Command")
        return Response(EconomicNodeSerializer(node).data, status=status.HTTP_200_OK)

class EconomicFlowViewSet(viewsets.ModelViewSet):
    queryset = EconomicFlow.objects.all()
    serializer_class = EconomicFlowSerializer

class InternalContractViewSet(viewsets.ModelViewSet):
    queryset = InternalContract.objects.all()
    serializer_class = InternalContractSerializer

    @action(detail=True, methods=['post'], url_path='update-pricing')
    def update_pricing(self, request, pk=None):
        new_price = InternalMarketService.update_internal_pricing(pk)
        return Response({'new_unit_price': new_price}, status=status.HTTP_200_OK)

class EcosystemIncentiveViewSet(viewsets.ModelViewSet):
    queryset = EcosystemIncentive.objects.all()
    serializer_class = EcosystemIncentiveSerializer

    @action(detail=True, methods=['post'], url_path='process')
    def process_incentive(self, request, pk=None):
        incentive = self.get_object()
        results = InternalMarketService.process_performance_incentives(incentive.node.id)
        return Response({'results': results}, status=status.HTTP_200_OK)

class EcosystemDashboardViewSet(viewsets.ViewSet):
    """
    Panel Estratégico del Ecosistema Autónomo.
    """
    def list(self, request):
        nodes = EconomicNode.objects.all()
        active_nodes = nodes.filter(status='ACTIVE')
        isolated_nodes = nodes.filter(status='ISOLATED')

        # Simple metrics calculation for list
        total_value = sum(OrchestrationService.calculate_node_value(n) for n in active_nodes)
        global_risk = sum(n.risk_index for n in active_nodes) / (active_nodes.count() or 1)

        data = {
            "ecosystem_value": total_value,
            "global_risk": global_risk,
            "node_count": nodes.count(),
            "isolated_nodes": isolated_nodes.count()
        }

        serializer = EcosystemMetricsSerializer(data)
        return Response(serializer.data)
