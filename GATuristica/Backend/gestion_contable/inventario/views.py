from rest_framework import viewsets, permissions
from .models import Almacen, MovimientoInventario
from .serializers import (
    AlmacenSerializer,
    MovimientoInventarioSerializer
)

class IsPrestadorOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # El perfil está en el objeto directamente o a través de una relación
        if hasattr(obj, 'perfil'):
            return obj.perfil == request.user.perfil_prestador
        # La FK a producto ahora apunta a ProductoUnificado que tiene 'provider'
        if hasattr(obj, 'producto') and hasattr(obj.producto, 'provider'):
             return obj.producto.provider == request.user.perfil_prestador
        return False

class AlmacenViewSet(viewsets.ModelViewSet):
    serializer_class = AlmacenSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return Almacen.objects.filter(perfil=self.request.user.perfil_prestador)

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        # Filtra movimientos basados en los productos del perfil del usuario
        return MovimientoInventario.objects.filter(producto__provider=self.request.user.perfil_prestador)
