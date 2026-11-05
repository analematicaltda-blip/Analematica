from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsOwner
from .models import InventoryItem
from .serializers import InventoryItemSerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el inventario de un prestador.
    """
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Filtra el queryset para devolver solo los objetos que pertenecen
        al perfil del prestador del usuario autenticado.
        """
        try:
            perfil = self.request.user.perfil_prestador
            return super().get_queryset().filter(perfil=perfil)
        except AttributeError:
            return self.queryset.model.objects.none()

    def perform_create(self, serializer):
        """
        Asocia automáticamente el perfil del prestador al nuevo ítem de inventario.
        """
        serializer.save(perfil=self.request.user.perfil_prestador)
