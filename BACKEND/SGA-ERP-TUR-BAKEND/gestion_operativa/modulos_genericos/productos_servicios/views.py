from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsOwner
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los productos y servicios de un prestador.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Filtra el queryset para devolver solo los objetos que pertenecen
        al perfil del prestador del usuario autenticado.
        """
        try:
            perfil = self.request.user.perfil_prestador
            # CORRECCIÓN: El modelo Product usa 'provider', no 'perfil'.
            return super().get_queryset().filter(provider=perfil)
        except AttributeError:
            # Si el usuario no tiene un perfil de prestador, no puede ver ningún objeto.
            return self.queryset.model.objects.none()

    def perform_create(self, serializer):
        """
        Asocia automáticamente el perfil del prestador al nuevo objeto
        al momento de la creación.
        """
        # CORRECCIÓN: El modelo Product usa 'provider', no 'perfil'.
        serializer.save(provider=self.request.user.perfil_prestador)
