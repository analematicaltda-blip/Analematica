from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProcesoOperativo, TareaOperativa, OrdenOperativa, IncidenteOperativo
from .serializers import ProcesoOperativoSerializer, TareaOperativaSerializer, OrdenOperativaSerializer, IncidenteOperativoSerializer

class OrdenOperativaViewSet(viewsets.ModelViewSet):
    serializer_class = OrdenOperativaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil_prestador'):
            return OrdenOperativa.objects.filter(provider=self.request.user.perfil_prestador)
        return OrdenOperativa.objects.none()

    @action(detail=True, methods=['post'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        orden = self.get_object()
        from apps.sarita_agents.orchestrator import sarita_orchestrator
        directive = {
            "domain": "operativo_general",
            "mission": {"type": "TRANSITION_OPERATIONAL_STATE"},
            "parameters": {
                "orden_id": str(orden.id),
                "nuevo_estado": request.data.get("nuevo_estado"),
                "motivo": request.data.get("motivo", ""),
                "agente_id": str(request.user.id)
            }
        }
        sarita_orchestrator.handle_directive(directive)
        return Response({"status": "Misión de transición enviada al Coronel Operativo."})

class IncidenteOperativoViewSet(viewsets.ModelViewSet):
    serializer_class = IncidenteOperativoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil_prestador'):
            return IncidenteOperativo.objects.filter(provider=self.request.user.perfil_prestador)
        return IncidenteOperativo.objects.none()

class ProcesoOperativoViewSet(viewsets.ModelViewSet):
    serializer_class = ProcesoOperativoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil_prestador'):
            return ProcesoOperativo.objects.filter(provider=self.request.user.perfil_prestador)
        return ProcesoOperativo.objects.none()

    @action(detail=True, methods=['post'])
    def avanzar_estado(self, request, pk=None):
        proceso = self.get_object()
        # Lógica de transición gobernada por agente
        from apps.sarita_agents.orchestrator import sarita_orchestrator
        directive = {
            "domain": "prestadores",
            "mission": {"type": "UPDATE_OPERATIONAL_STATE"},
            "parameters": {
                "entidad_tipo": "ProcesoOperativo",
                "entidad_id": str(proceso.id),
                "nuevo_estado": request.data.get("nuevo_estado")
            }
        }
        sarita_orchestrator.handle_directive(directive)
        return Response({"status": "Misión de transición enviada."})

class TareaOperativaViewSet(viewsets.ModelViewSet):
    serializer_class = TareaOperativaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil_prestador'):
            return TareaOperativa.objects.filter(provider=self.request.user.perfil_prestador)
        return TareaOperativa.objects.none()
