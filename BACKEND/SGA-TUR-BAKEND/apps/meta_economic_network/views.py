from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import MetaEcosystem, EcosystemInterdependence, InteroperabilityProtocol, GlobalUtilityMetric, MetaLiquidityPool
from .serializers import (
    MetaEcosystemSerializer, EcosystemInterdependenceSerializer,
    InteroperabilityProtocolSerializer, GlobalUtilityMetricSerializer,
    MetaLiquidityPoolSerializer, MetaDashboardSerializer
)
from .application.ceoe_service import CEOEService
from .application.incentive_service import IncentiveMatrixService
from .application.liquidity_service import MetaLiquidityService
from .application.risk_service import MetaRiskService

class MetaEcosystemViewSet(viewsets.ModelViewSet):
    queryset = MetaEcosystem.objects.all()
    serializer_class = MetaEcosystemSerializer

    @action(detail=False, methods=['post'], url_path='run-meta-orchestration')
    def run_orchestration(self, request):
        result = CEOEService.run_meta_orchestration()
        return Response(result, status=status.HTTP_200_OK)

class EcosystemInterdependenceViewSet(viewsets.ModelViewSet):
    queryset = EcosystemInterdependence.objects.all()
    serializer_class = EcosystemInterdependenceSerializer

class InteroperabilityProtocolViewSet(viewsets.ModelViewSet):
    queryset = InteroperabilityProtocol.objects.all()
    serializer_class = InteroperabilityProtocolSerializer

class GlobalUtilityMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GlobalUtilityMetric.objects.all()
    serializer_class = GlobalUtilityMetricSerializer

class MetaLiquidityPoolViewSet(viewsets.ModelViewSet):
    queryset = MetaLiquidityPool.objects.all()
    serializer_class = MetaLiquidityPoolSerializer

    @action(detail=True, methods=['post'], url_path='activate-emergency')
    def activate_emergency(self, request, pk=None):
        result = MetaLiquidityService.activate_emergency_pooling(pk)
        return Response({'success': result}, status=status.HTTP_200_OK)

class MetaDashboardViewSet(viewsets.ViewSet):
    """
    Panel de Coordinación Macro-Económica (Fase 20.8).
    """
    def list(self, request):
        ecosystems = MetaEcosystem.objects.all()
        active_ecosystems = ecosystems.filter(is_active=True)

        # Aggregate Metrics
        total_utility = sum(m.net_global_utility for m in GlobalUtilityMetric.objects.filter(period='2026-01')) # Sample
        if not total_utility: # Fallback calculation
            total_utility = sum(CEOEService.calculate_global_utility(e).net_global_utility for e in active_ecosystems)

        total_liquidity = sum(p.total_liquidity for p in MetaLiquidityPool.objects.all())
        health_index = Decimal('1.0') - (sum(e.risk_index for e in active_ecosystems) / (active_ecosystems.count() or 1))

        data = {
            "aggregate_global_utility": total_utility,
            "network_health_index": health_index,
            "total_network_liquidity": total_liquidity,
            "active_ecosystems": active_ecosystems.count(),
            "firewalls_active": MetaEcosystem.objects.filter(is_active=False).count() # Simplified
        }

        serializer = MetaDashboardSerializer(data)
        return Response(serializer.data)
