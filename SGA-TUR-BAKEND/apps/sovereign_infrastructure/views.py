from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JurisdictionalNode, RegulatoryProfile, CapitalShield, DigitalInfraBackup, CorporateConstitution
from .serializers import (
    JurisdictionalNodeSerializer, RegulatoryProfileSerializer,
    CapitalShieldSerializer, DigitalInfraBackupSerializer,
    CorporateConstitutionSerializer, SovereignDashboardSerializer
)
from .application.regulatory_service import RegulatoryIntelligenceService
from .application.capital_service import CapitalShieldService
from .application.infra_service import DigitalInfrastructureService

class JurisdictionalNodeViewSet(viewsets.ModelViewSet):
    queryset = JurisdictionalNode.objects.all()
    serializer_class = JurisdictionalNodeSerializer

    @action(detail=True, methods=['post'], url_path='simulate-shock')
    def simulate_shock(self, request, pk=None):
        node = self.get_object()
        shock_type = request.data.get('shock_type', 'TAX_HIKE')
        result = RegulatoryIntelligenceService.simulate_regulatory_impact(node.country_code, shock_type)
        return Response({'affected_nodes': result}, status=status.HTTP_200_OK)

class RegulatoryProfileViewSet(viewsets.ModelViewSet):
    queryset = RegulatoryProfile.objects.all()
    serializer_class = RegulatoryProfileSerializer

class CapitalShieldViewSet(viewsets.ModelViewSet):
    queryset = CapitalShield.objects.all()
    serializer_class = CapitalShieldSerializer

    @action(detail=False, methods=['post'], url_path='distribute')
    def distribute_capital(self, request):
        amount = request.data.get('amount', 0)
        currency = request.data.get('currency', 'USD')
        result = CapitalShieldService.distribute_capital(amount, currency)
        return Response({'success': result}, status=status.HTTP_200_OK)

class DigitalInfraBackupViewSet(viewsets.ModelViewSet):
    queryset = DigitalInfraBackup.objects.all()
    serializer_class = DigitalInfraBackupSerializer

    @action(detail=False, methods=['post'], url_path='check-redundancy')
    def check_redundancy(self, request):
        failures = DigitalInfrastructureService.perform_systemic_redundancy_check()
        return Response({'failures_detected': failures}, status=status.HTTP_200_OK)

class CorporateConstitutionViewSet(viewsets.ModelViewSet):
    queryset = CorporateConstitution.objects.all()
    serializer_class = CorporateConstitutionSerializer

class SovereignDashboardViewSet(viewsets.ViewSet):
    """
    Panel Estratégico de Resiliencia Soberana (Fase 19.9).
    """
    def list(self, request):
        nodes = JurisdictionalNode.objects.filter(level='ROOT', is_active=True).first()
        resilience_score = Decimal('0')
        if nodes:
            resilience_score = RegulatoryIntelligenceService.calculate_sovereign_resilience(nodes.id)

        technical_independence = DigitalInfrastructureService.calculate_technical_independence_index()
        capital_shield_total = sum(s.current_value for s in CapitalShield.objects.all())

        data = {
            "resilience_score": resilience_score,
            "technical_independence": technical_independence,
            "capital_shield_total": capital_shield_total,
            "active_jurisdictions": JurisdictionalNode.objects.values('country_code').distinct().count(),
            "active_backups": DigitalInfraBackup.objects.filter(sync_status='ACTIVE').count()
        }

        serializer = SovereignDashboardSerializer(data)
        return Response(serializer.data)
