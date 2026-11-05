from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import GovernanceBody, GovernanceMember, AlgorithmicAudit, DisputeCase, GovernanceStabilityMetric
from .serializers import (
    GovernanceBodySerializer, GovernanceMemberSerializer,
    AlgorithmicAuditSerializer, DisputeCaseSerializer,
    GovernanceStabilityMetricSerializer, GovernanceDashboardSerializer
)
from .application.oversight_service import AlgorithmicOversightService
from .application.harmonization_service import RegulatoryHarmonizationService
from .application.dispute_service import DisputeResolutionService

class GovernanceBodyViewSet(viewsets.ModelViewSet):
    queryset = GovernanceBody.objects.all()
    serializer_class = GovernanceBodySerializer

class GovernanceMemberViewSet(viewsets.ModelViewSet):
    queryset = GovernanceMember.objects.all()
    serializer_class = GovernanceMemberSerializer

class AlgorithmicAuditViewSet(viewsets.ModelViewSet):
    queryset = AlgorithmicAudit.objects.all()
    serializer_class = AlgorithmicAuditSerializer

    @action(detail=False, methods=['post'], url_path='run-audit')
    def run_audit(self, request):
        component = request.data.get('component')
        v_hash = request.data.get('version_hash')
        audit = AlgorithmicOversightService.audit_system_component(component, v_hash)
        return Response(AlgorithmicAuditSerializer(audit).data, status=status.HTTP_201_CREATED)

class DisputeCaseViewSet(viewsets.ModelViewSet):
    queryset = DisputeCase.objects.all()
    serializer_class = DisputeCaseSerializer

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve_dispute(self, request, pk=None):
        resolution = request.data.get('resolution')
        result = DisputeResolutionService.resolve_case(pk, resolution)
        return Response({'success': result}, status=status.HTTP_200_OK)

class GovernanceDashboardViewSet(viewsets.ViewSet):
    """
    Panel de Gobernanza Transnacional Híbrida (Fase 22.11).
    """
    def list(self, request):
        bodies = GovernanceBody.objects.all()
        disputes = DisputeCase.objects.exclude(status='RESOLVED')
        audits = AlgorithmicAudit.objects.filter(status='APPROVED')

        # Aggregate Metrics
        if bodies.exists():
            stability = sum(AlgorithmicOversightService.calculate_governance_stability(b.id) for b in bodies) / bodies.count()
        else:
            stability = Decimal('1.0')

        data = {
            "institutional_stability": stability,
            "active_disputes": disputes.count(),
            "certified_algorithms": audits.count(),
            "governance_level_active": 1, # Default Operational
            "audit_coverage": Decimal('0.85') # Sample
        }

        serializer = GovernanceDashboardSerializer(data)
        return Response(serializer.data)
