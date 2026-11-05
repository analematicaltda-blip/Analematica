from rest_framework import viewsets, permissions, serializers
from .models import OrganizadorEvento, Evento, Promocion
from .serializers import (
    OrganizadorEventoSerializer,
    EventoSerializer,
    PromocionSerializer,
)
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner
from ...modulos_genericos.productos_servicios.models import Product

class OrganizadorEventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que un proveedor gestione su perfil de Organizador de Eventos.
    """
    serializer_class = OrganizadorEventoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return OrganizadorEvento.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        if OrganizadorEvento.objects.filter(perfil=self.request.user.perfil_prestador).exists():
            raise serializers.ValidationError("El perfil ya tiene un organizador de eventos asociado.")
        serializer.save(perfil=self.request.user.perfil_prestador)

class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Eventos de un Organizador.
    """
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            organizador = self.request.user.perfil_prestador.organizador_eventos
            return Evento.objects.filter(organizador=organizador)
        except OrganizadorEvento.DoesNotExist:
            return Evento.objects.none()

    def perform_create(self, serializer):
        try:
            organizador = self.request.user.perfil_prestador.organizador_eventos
            serializer.save(organizador=organizador)
        except OrganizadorEvento.DoesNotExist:
            raise serializers.ValidationError("Debe crear un perfil de organizador de eventos antes de añadir eventos.")

class PromocionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las Promociones de un Proveedor.
    """
    serializer_class = PromocionSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return Promocion.objects.filter(perfil=self.request.user.perfil_prestador)

    def get_serializer_context(self):
        """
        Pasa el 'request' al serializador para poder validar los productos.
        """
        return {'request': self.request}

    def get_serializer(self, *args, **kwargs):
        """
        Filtra el queryset de 'productos_aplicables' para mostrar solo los
        productos del perfil del usuario actual.
        """
        serializer = super().get_serializer(*args, **kwargs)
        if hasattr(serializer.fields, 'get'):
            productos_field = serializer.fields.get('productos_aplicables')
            if productos_field:
                perfil = self.request.user.perfil_prestador
                productos_field.queryset = Product.objects.filter(perfil=perfil)
        return serializer

    def perform_create(self, serializer):
        serializer.save(perfil=self.request.user.perfil_prestador)
