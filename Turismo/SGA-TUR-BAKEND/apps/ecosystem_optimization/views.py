from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    OptimizationProposal,
    PerformanceMetric,
    AutonomousAction,
    AutonomousExecutionLog,
    AutonomyControl
)
from .serializers import (
    OptimizationProposalSerializer,
    AutonomousActionSerializer,
    AutonomousExecutionLogSerializer,
    AutonomyControlSerializer
)
from .services.optimization_engine import OptimizationEngine
from .services.governance_optimizer import GovernanceOptimizer
from .services.autonomy_engine import AutonomyEngine
from api.permissions import IsSuperAdmin

class OptimizationProposalViewSet(viewsets.ModelViewSet):
    queryset = OptimizationProposal.objects.all()
    serializer_class = OptimizationProposalSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    @action(detail=False, methods=['post'])
    def run_cycle(self, request):
        """Ejecuta el ciclo de optimización del ecosistema."""
        engine = OptimizationEngine()
        proposals = engine.run_optimization_cycle()
        return Response({
            "message": f"Ciclo completado. {len(proposals)} nuevas optimizaciones propuestas.",
            "proposals": OptimizationProposalSerializer(proposals, many=True).data
        })

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Aprueba y ejecuta la optimización."""
        optimizer = GovernanceOptimizer(user=request.user)
        justification = request.data.get("justificacion", "Aplicado vía Consola de Optimización.")
        try:
            optimizer.approve_optimization(pk, justification)
            optimizer.execute_optimization(pk)
            return Response({"status": "EXECUTED", "message": "Ajuste sistémico aplicado correctamente."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AutonomousActionViewSet(viewsets.ModelViewSet):
    queryset = AutonomousAction.objects.all()
    serializer_class = AutonomousActionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """Dispara manualmente una ejecución autónoma (Nivel 2)."""
        action = self.get_object()
        try:
            result = AutonomyEngine.execute_autonomous_action(
                action_name=action.name,
                parameters=request.data.get("parameters", {}),
                actor_user=request.user
            )
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AutonomousExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AutonomousExecutionLog.objects.all()
    serializer_class = AutonomousExecutionLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class AutonomyControlViewSet(viewsets.ModelViewSet):
    queryset = AutonomyControl.objects.all()
    serializer_class = AutonomyControlSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    @action(detail=False, methods=['post'])
    def global_kill_switch(self, request):
        """Activa/Desactiva el Kill Switch Global."""
        control, _ = AutonomyControl.objects.get_or_create(domain=None)
        control.is_enabled = request.data.get("enabled", False)
        control.reason = request.data.get("reason", "Acción manual vía Kill Switch.")
        control.updated_by = request.user
        control.save()

        status = "HABILITADA" if control.is_enabled else "BLOQUEADA"
        return Response({"message": f"Autonomía GLOBAL {status}"})

    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """Revierte la optimización."""
        optimizer = GovernanceOptimizer(user=request.user)
        try:
            optimizer.rollback_optimization(pk)
            return Response({"status": "REVERTED", "message": "Sistema restaurado al estado previo."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
