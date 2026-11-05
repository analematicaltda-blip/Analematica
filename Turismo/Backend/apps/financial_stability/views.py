from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import StabilityCouncil, RiskAnalyticsNode, LiquidityBuffer, ShockAbsorptionPolicy, CrisisCase
from .serializers import (
    StabilityCouncilSerializer, RiskAnalyticsNodeSerializer,
    LiquidityBufferSerializer, ShockAbsorptionPolicySerializer,
    CrisisCaseSerializer, StabilityDashboardSerializer
)
from .application.analytics_service import RiskAnalyticsService
from .application.liquidity_service import LiquidityStabilizationService
from .application.crisis_service import CrisisContainmentService

class StabilityCouncilViewSet(viewsets.ModelViewSet):
    queryset = StabilityCouncil.objects.all()
    serializer_class = StabilityCouncilSerializer

    @action(detail=True, methods=['post'], url_path='run-systemic-audit')
    def run_audit(self, request, pk=None):
        gri = RiskAnalyticsService.run_systemic_audit(pk)
        return Response({'global_risk_index': gri}, status=status.HTTP_200_OK)

class RiskAnalyticsNodeViewSet(viewsets.ModelViewSet):
    queryset = RiskAnalyticsNode.objects.all()
    serializer_class = RiskAnalyticsNodeSerializer

class LiquidityBufferViewSet(viewsets.ModelViewSet):
    queryset = LiquidityBuffer.objects.all()
    serializer_class = LiquidityBufferSerializer

class ShockAbsorptionViewSet(viewsets.ModelViewSet):
    queryset = ShockAbsorptionPolicy.objects.all()
    serializer_class = ShockAbsorptionPolicySerializer

class CrisisCaseViewSet(viewsets.ModelViewSet):
    queryset = CrisisCase.objects.all()
    serializer_class = CrisisCaseSerializer

    @action(detail=False, methods=['post'], url_path='initiate-containment')
    def initiate_containment(self, request):
        node_id = request.data.get('node_id')
        magnitude = request.data.get('magnitude', 0.5)
        crisis = CrisisContainmentService.initiate_containment_protocol(node_id, magnitude)
        return Response(CrisisCaseSerializer(crisis).data, status=status.HTTP_201_CREATED)

class StabilityDashboardViewSet(viewsets.ViewSet):
    """
    Panel de Estabilidad Financiera Global Integrada (Fase 25.10).
    """
    def list(self, request):
        councils = StabilityCouncil.objects.all()
        crisis_cases = CrisisCase.objects.exclude(containment_status='RESOLVED')
        buffers = LiquidityBuffer.objects.all()

        # Aggregate Metrics
        total_liq = sum(b.available_liquidity for b in buffers)
        global_gri = sum(n.node_risk_index for n in RiskAnalyticsNode.objects.all()) # Simple sum for dashboard

        data = {
            "global_risk_index": global_gri,
            "monitoring_status": councils.first().monitoring_status if councils.exists() else "GREEN",
            "total_stabilization_liquidity": total_liq,
            "active_crisis_cases": crisis_cases.count(),
            "buffer_adequacy_ratio": Decimal('0.92') # Sample
        }

        serializer = StabilityDashboardSerializer(data)
        return Response(serializer.data)
