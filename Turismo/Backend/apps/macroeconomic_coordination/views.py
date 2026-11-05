from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import MacroCouncil, SystemicRiskIndicator, CapitalCoordinationNode, EconomicModelSnapshot, StabilizationProtocol
from .serializers import (
    MacroCouncilSerializer, SystemicRiskIndicatorSerializer,
    CapitalCoordinationNodeSerializer, EconomicModelSnapshotSerializer,
    StabilizationProtocolSerializer, MacroDashboardSerializer
)
from .application.risk_service import SystemicRiskService
from .application.coordination_engine import CoordinationEngineService
from .application.modeling_service import MacroModelingService

class MacroCouncilViewSet(viewsets.ModelViewSet):
    queryset = MacroCouncil.objects.all()
    serializer_class = MacroCouncilSerializer

class SystemicRiskViewSet(viewsets.ModelViewSet):
    queryset = SystemicRiskIndicator.objects.all()
    serializer_class = SystemicRiskIndicatorSerializer

    @action(detail=False, methods=['post'], url_path='analyze')
    def run_analysis(self, request):
        council_id = request.data.get('council_id')
        indicator = SystemicRiskService.analyze_systemic_risk(council_id)
        return Response(SystemicRiskIndicatorSerializer(indicator).data, status=status.HTTP_201_CREATED)

class CapitalCoordinationViewSet(viewsets.ModelViewSet):
    queryset = CapitalCoordinationNode.objects.all()
    serializer_class = CapitalCoordinationNodeSerializer

    @action(detail=True, methods=['post'], url_path='simulate-stress')
    def simulate_stress(self, request, pk=None):
        scenario = request.data.get('scenario', 'VOLATILITY_SPIKE')
        required = CoordinationEngineService.simulate_capital_flows(pk, scenario)
        return Response({'required_buffer': required}, status=status.HTTP_200_OK)

class EconomicModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EconomicModelSnapshot.objects.all()
    serializer_class = EconomicModelSnapshotSerializer

    @action(detail=False, methods=['post'], url_path='run-simulation')
    def run_simulation(self, request):
        m_type = request.data.get('model_type', 'DSGE_EXTENDED')
        snapshot = MacroModelingService.run_macro_simulation(m_type)
        return Response(EconomicModelSnapshotSerializer(snapshot).data, status=status.HTTP_201_CREATED)

class StabilizationProtocolViewSet(viewsets.ModelViewSet):
    queryset = StabilizationProtocol.objects.all()
    serializer_class = StabilizationProtocolSerializer

    @action(detail=True, methods=['post'], url_path='activate')
    def activate_protocol(self, request, pk=None):
        protocol = self.get_object()
        result = CoordinationEngineService.activate_stabilization_protocol(protocol.protocol_code)
        return Response({'activated': result}, status=status.HTTP_200_OK)

class MacroDashboardViewSet(viewsets.ViewSet):
    """
    Panel de Coordinación Macroecómica Público-Privada (Fase 24.10).
    """
    def list(self, request):
        indicators = SystemicRiskIndicator.objects.order_by('-timestamp').first()
        snapshot = EconomicModelSnapshot.objects.order_by('-generated_at').first()
        nodes = CapitalCoordinationNode.objects.all()

        data = {
            "aggregated_systemic_risk": indicators.net_systemic_risk if indicators else Decimal('0.15'),
            "macro_stability_index": snapshot.macro_stability_index if snapshot else Decimal('0.85'),
            "private_buffer_total": sum(n.current_private_buffer for n in nodes),
            "active_stabilization_protocols": StabilizationProtocol.objects.filter(last_activation_date__isnull=False).count(),
            "coordination_level": 1
        }

        serializer = MacroDashboardSerializer(data)
        return Response(serializer.data)
