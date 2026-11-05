from rest_framework import viewsets, permissions
from .models import Reserva, PoliticaCancelacion
from .serializers import ReservaSerializer, PoliticaCancelacionSerializer
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner

class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        """
        El proveedor solo puede ver sus propias reservas.
        """
        return Reserva.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        """
        Asigna el perfil del proveedor automáticamente al crear una reserva.
        """
        serializer.save(perfil=self.request.user.perfil_prestador)

class PoliticaCancelacionViewSet(viewsets.ModelViewSet):
    serializer_class = PoliticaCancelacionSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        """
        El proveedor solo puede ver sus propias políticas de cancelación.
        """
        return PoliticaCancelacion.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        """
        Asigna el perfil del proveedor automáticamente al crear una política.
        """
        serializer.save(perfil=self.request.user.perfil_prestador)
