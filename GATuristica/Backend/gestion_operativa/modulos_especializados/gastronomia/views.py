from rest_framework import viewsets, permissions, serializers
from .models import Restaurante, Menu, CategoriaPlato, Plato, ZonaDelivery
from .serializers import (
    RestauranteSerializer,
    MenuSerializer,
    CategoriaPlatoSerializer,
    PlatoSerializer,
    ZonaDeliverySerializer
)
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner

class RestauranteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que un proveedor gestione su Restaurante.
    """
    serializer_class = RestauranteSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return Restaurante.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        if Restaurante.objects.filter(perfil=self.request.user.perfil_prestador).exists():
            raise serializers.ValidationError("El perfil ya tiene un restaurante asociado.")
        serializer.save(perfil=self.request.user.perfil_prestador)

class MenuViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los menús de un Restaurante.
    """
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            restaurante = self.request.user.perfil_prestador.restaurante
            return Menu.objects.filter(restaurante=restaurante)
        except Restaurante.DoesNotExist:
            return Menu.objects.none()

    def perform_create(self, serializer):
        try:
            restaurante = self.request.user.perfil_prestador.restaurante
            serializer.save(restaurante=restaurante)
        except Restaurante.DoesNotExist:
            raise serializers.ValidationError("Debe crear un restaurante antes de añadir menús.")

class CategoriaPlatoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las categorías de un Menú.
    """
    serializer_class = CategoriaPlatoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            restaurante = self.request.user.perfil_prestador.restaurante
            return CategoriaPlato.objects.filter(menu__restaurante=restaurante)
        except Restaurante.DoesNotExist:
            return CategoriaPlato.objects.none()

class PlatoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los platos de una Categoría.
    """
    serializer_class = PlatoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            restaurante = self.request.user.perfil_prestador.restaurante
            return Plato.objects.filter(categoria__menu__restaurante=restaurante)
        except Restaurante.DoesNotExist:
            return Plato.objects.none()

class ZonaDeliveryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las zonas de delivery de un Restaurante.
    """
    serializer_class = ZonaDeliverySerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        try:
            restaurante = self.request.user.perfil_prestador.restaurante
            return ZonaDelivery.objects.filter(restaurante=restaurante)
        except Restaurante.DoesNotExist:
            return ZonaDelivery.objects.none()

    def perform_create(self, serializer):
        try:
            restaurante = self.request.user.perfil_prestador.restaurante
            serializer.save(restaurante=restaurante)
        except Restaurante.DoesNotExist:
            raise serializers.ValidationError("Debe crear un restaurante antes de añadir zonas de delivery.")
