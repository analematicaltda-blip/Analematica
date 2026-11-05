from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from .models import SystemicRiskIndicator, StabilityAlert, MitigationScenario
from .serializers import IndicatorSerializer, AlertSerializer, ScenarioSerializer
from .services import StabilityMonitorService

class PeaceNetViewSet(viewsets.ViewSet):
    """
    Panel de Estabilidad Sistémica (Z-PEACE-NET).
    Permite monitorear indicadores y validar misiones de prevención.
    """
    permission_classes = [IsAdminUser]
    serializer_class = IndicatorSerializer

    @extend_schema(responses={200: serializers.JSONField()})
    @action(detail=False, methods=['get'])
    def status(self, request):
        indicators = SystemicRiskIndicator.objects.all()
        alerts = StabilityAlert.objects.filter(is_active=True)

        return Response({
            "infrastructure_status": "OPERATIONAL",
            "active_alerts_count": alerts.count(),
            "global_stability_index": 0.95 # Simulado
        })

    @extend_schema(responses={200: AlertSerializer})
    @action(detail=False, methods=['post'], url_path='scan-risks')
    def scan_risks(self, request):
        alert = StabilityMonitorService.analyze_indicators()
        if alert:
            return Response(AlertSerializer(alert).data)
        return Response({"message": "No se detectaron riesgos anómalos."})

    @extend_schema(responses={200: IndicatorSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='indicators')
    def list_indicators(self, request):
        indicators = SystemicRiskIndicator.objects.all()
        return Response(IndicatorSerializer(indicators, many=True).data)
