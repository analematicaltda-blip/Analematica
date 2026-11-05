from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PeriodoContable
from .serializers import PeriodoContableSerializer
from .services import CierreContableService

class PeriodoContableViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodoContableSerializer
    permission_classes = [permissions.IsAdminUser] # Solo admins pueden gestionar períodos

    def get_queryset(self):
        # Asumiendo que un admin puede ver todos los períodos de su(s) perfil(es)
        # En un sistema multi-tenant más complejo, esto necesitaría más lógica.
        return PeriodoContable.objects.filter(perfil=self.request.user.perfil_prestador)

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        periodo = self.get_object()
        service = CierreContableService(periodo)
        try:
            service.cerrar_periodo()
            return Response({"status": "Período cerrado exitosamente."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reabrir(self, request, pk=None):
        periodo = self.get_object()
        service = CierreContableService(periodo)
        try:
            service.reabrir_periodo()
            return Response({"status": "Período reabierto exitosamente."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
