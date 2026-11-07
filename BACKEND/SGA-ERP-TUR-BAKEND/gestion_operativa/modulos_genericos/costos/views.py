from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsOwner
from .models import Costo
from .serializers import CostoSerializer

class CostoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los costos operativos de un prestador.
    """
    queryset = Costo.objects.all()
    serializer_class = CostoSerializer
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
        Asocia automáticamente el perfil del prestador al nuevo costo.
        """
        serializer.save(perfil=self.request.user.perfil_prestador)
