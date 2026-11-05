from rest_framework import viewsets, permissions, serializers
from .models import OperadorTuristico, PaqueteTuristico, ItinerarioDia
from .serializers import (
    OperadorTuristicoSerializer,
    PaqueteTuristicoSerializer,
    ItinerarioDiaSerializer,
)
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner

class OperadorTuristicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que un proveedor gestione su Operador Turístico.
    """
    serializer_class = OperadorTuristicoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return OperadorTuristico.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        if OperadorTuristico.objects.filter(perfil=self.request.user.perfil_prestador).exists():
            raise serializers.ValidationError("El perfil ya tiene un operador turístico asociado.")
        serializer.save(perfil=self.request.user.perfil_prestador)

class PaqueteTuristicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Paquetes Turísticos de un Operador.
    """
    serializer_class = PaqueteTuristicoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            operador = self.request.user.perfil_prestador.operador_turistico
            return PaqueteTuristico.objects.filter(operador=operador)
        except OperadorTuristico.DoesNotExist:
            return PaqueteTuristico.objects.none()

    def perform_create(self, serializer):
        try:
            operador = self.request.user.perfil_prestador.operador_turistico
            serializer.save(operador=operador)
        except OperadorTuristico.DoesNotExist:
            raise serializers.ValidationError("Debe crear un operador turístico antes de añadir paquetes.")

class ItinerarioDiaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el itinerario de un Paquete Turístico.
    """
    serializer_class = ItinerarioDiaSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            operador = self.request.user.perfil_prestador.operador_turistico
            return ItinerarioDia.objects.filter(paquete__operador=operador)
        except OperadorTuristico.DoesNotExist:
            return ItinerarioDia.objects.none()
