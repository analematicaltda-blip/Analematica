from rest_framework import viewsets, permissions, serializers
from .models import CompaniaTransporte, TipoVehiculo, Vehiculo, Ruta, HorarioRuta
from .serializers import (
    CompaniaTransporteSerializer,
    TipoVehiculoSerializer,
    VehiculoSerializer,
    RutaSerializer,
    HorarioRutaSerializer,
)
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner

class TipoVehiculoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver los tipos de vehículo disponibles.
    """
    queryset = TipoVehiculo.objects.all()
    serializer_class = TipoVehiculoSerializer
    permission_classes = [permissions.IsAuthenticated]

class CompaniaTransporteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que un proveedor gestione su Compañía de Transporte.
    """
    serializer_class = CompaniaTransporteSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return CompaniaTransporte.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        if CompaniaTransporte.objects.filter(perfil=self.request.user.perfil_prestador).exists():
            raise serializers.ValidationError("El perfil ya tiene una compañía de transporte asociada.")
        serializer.save(perfil=self.request.user.perfil_prestador)

class VehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los vehículos de una Compañía de Transporte.
    """
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            compania = self.request.user.perfil_prestador.compania_transporte
            return Vehiculo.objects.filter(compania=compania)
        except CompaniaTransporte.DoesNotExist:
            return Vehiculo.objects.none()

    def perform_create(self, serializer):
        try:
            compania = self.request.user.perfil_prestador.compania_transporte
            serializer.save(compania=compania)
        except CompaniaTransporte.DoesNotExist:
            raise serializers.ValidationError("Debe crear una compañía de transporte antes de añadir vehículos.")

class RutaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las rutas de una Compañía de Transporte.
    """
    serializer_class = RutaSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            compania = self.request.user.perfil_prestador.compania_transporte
            return Ruta.objects.filter(compania=compania)
        except CompaniaTransporte.DoesNotExist:
            return Ruta.objects.none()

    def perform_create(self, serializer):
        try:
            compania = self.request.user.perfil_prestador.compania_transporte
            serializer.save(compania=compania)
        except CompaniaTransporte.DoesNotExist:
            raise serializers.ValidationError("Debe crear una compañía de transporte antes de añadir rutas.")

class HorarioRutaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los horarios de una Ruta.
    """
    serializer_class = HorarioRutaSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            compania = self.request.user.perfil_prestador.compania_transporte
            return HorarioRuta.objects.filter(ruta__compania=compania)
        except CompaniaTransporte.DoesNotExist:
            return HorarioRuta.objects.none()
