from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import StateEntity, IntegrationProtocol, SovereignComplianceNode, InfrastructureProject, JointGovernanceCommittee
from .serializers import (
    StateEntitySerializer, IntegrationProtocolSerializer,
    SovereignComplianceNodeSerializer, InfrastructureProjectSerializer,
    JointGovernanceCommitteeSerializer, StateDashboardSerializer
)
from .application.interop_service import InteroperabilityService
from .application.compliance_service import SovereignComplianceService
from .application.governance_service import JointGovernanceService
from .application.crisis_service import CrisisCoordinationService

class StateEntityViewSet(viewsets.ModelViewSet):
    queryset = StateEntity.objects.all()
    serializer_class = StateEntitySerializer

    @action(detail=True, methods=['post'], url_path='validate-identity')
    def validate_identity(self, request, pk=None):
        cert_data = request.data.get('cert_data', {})
        result = InteroperabilityService.validate_institutional_identity(pk, cert_data)
        return Response({'is_certified': result}, status=status.HTTP_200_OK)

class IntegrationProtocolViewSet(viewsets.ModelViewSet):
    queryset = IntegrationProtocol.objects.all()
    serializer_class = IntegrationProtocolSerializer

class SovereignComplianceNodeViewSet(viewsets.ModelViewSet):
    queryset = SovereignComplianceNode.objects.all()
    serializer_class = SovereignComplianceNodeSerializer

    @action(detail=True, methods=['post'], url_path='run-audit')
    def run_audit(self, request, pk=None):
        node = self.get_object()
        utility = SovereignComplianceService.run_compliance_audit(node.jurisdiction)
        return Response({'integrated_utility': utility}, status=status.HTTP_200_OK)

class InfrastructureProjectViewSet(viewsets.ModelViewSet):
    queryset = InfrastructureProject.objects.all()
    serializer_class = InfrastructureProjectSerializer

    @action(detail=True, methods=['post'], url_path='mobilize-crisis-funds')
    def mobilize_funds(self, request, pk=None):
        amount = Decimal(str(request.data.get('amount', 0)))
        reason = request.data.get('reason', 'Emergency Support')
        result = CrisisCoordinationService.mobilize_crisis_liquidity(pk, amount, reason)
        return Response({'success': result}, status=status.HTTP_200_OK)

class JointGovernanceCommitteeViewSet(viewsets.ModelViewSet):
    queryset = JointGovernanceCommittee.objects.all()
    serializer_class = JointGovernanceCommitteeSerializer

    @action(detail=True, methods=['post'], url_path='activate-intervention')
    def activate_intervention(self, request, pk=None):
        result = JointGovernanceService.activate_state_intervention(pk)
        return Response({'intervention_active': result}, status=status.HTTP_200_OK)

class StateDashboardViewSet(viewsets.ViewSet):
    """
    Panel de Integración Estructural Holding-Estado (Fase 21.9).
    """
    def list(self, request):
        entities = StateEntity.objects.all()
        projects = InfrastructureProject.objects.all()
        compliance_nodes = SovereignComplianceNode.objects.all()

        # Aggregate Metrics
        avg_compliance = sum(e.compliance_score for e in entities) / (entities.count() or 1)
        total_utility = sum(SovereignComplianceService.calculate_integrated_utility(n.id) for n in compliance_nodes)
        total_commitment = sum(p.capital_committed for p in projects.filter(status='ACTIVE'))

        data = {
            "compliance_score": avg_compliance,
            "integrated_utility": total_utility,
            "infrastructure_commitment": total_commitment,
            "certified_entities": entities.filter(is_certified=True).count(),
            "active_projects": projects.filter(status='ACTIVE').count()
        }

        serializer = StateDashboardSerializer(data)
        return Response(serializer.data)
