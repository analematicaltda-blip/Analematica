from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StrategyProposal, DecisionMatrix
from .serializers import StrategyProposalSerializer, DecisionMatrixSerializer
from .services.strategic_analysis import StrategicAnalysisService
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from api.permissions import IsSuperAdmin

class StrategyProposalViewSet(viewsets.ModelViewSet):
    queryset = StrategyProposal.objects.all()
    serializer_class = StrategyProposalSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    @action(detail=False, methods=['post'])
    def run_analysis(self, request):
        """Dispara un nuevo ciclo de análisis estratégico."""
        service = StrategicAnalysisService()
        proposals = service.run_full_audit()
        return Response({
            "message": f"Análisis completado. {len(proposals)} nuevas propuestas generadas.",
            "proposals": StrategyProposalSerializer(proposals, many=True).data
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        proposal = self.get_object()
        proposal.status = StrategyProposal.Status.APPROVED
        proposal.decidida_por = request.user
        proposal.justificacion_humana = request.data.get("justificacion", "Aprobado vía Tablero de Inteligencia.")
        proposal.save()
        return Response({"status": "APPROVED", "message": "Propuesta aprobada y lista para ejecución."})

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        proposal = self.get_object()
        kernel = GovernanceKernel(user=request.user)
        try:
            result = kernel.execute_strategic_proposal(str(proposal.id))
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DecisionMatrixViewSet(viewsets.ModelViewSet):
    queryset = DecisionMatrix.objects.all()
    serializer_class = DecisionMatrixSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
