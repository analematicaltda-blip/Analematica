from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import ThreatNode, ThreatEdge, PredictiveScenario, PreventiveHardening
from .serializers import ThreatNodeSerializer, PredictiveScenarioSerializer, PreventiveHardeningSerializer

class ThreatNodeViewSet(viewsets.ModelViewSet):
    queryset = ThreatNode.objects.all()
    serializer_class = ThreatNodeSerializer
    permission_classes = [IsAdminUser]

class PredictiveScenarioViewSet(viewsets.ModelViewSet):
    queryset = PredictiveScenario.objects.all()
    serializer_class = PredictiveScenarioSerializer
    permission_classes = [IsAdminUser]

class PreventiveHardeningViewSet(viewsets.ModelViewSet):
    queryset = PreventiveHardening.objects.all()
    serializer_class = PreventiveHardeningSerializer
    permission_classes = [IsAdminUser]
