# SaritaUnificado/backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_genericos/clientes/views.py
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Cliente
from .serializers import ClienteSerializer
from ....permissions import IsPrestadorOwner

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los clientes (CRM) de un prestador.
    """
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Este queryset asegura que el usuario solo vea los clientes
        asociados a su propio perfil de prestador.
        """
        user = self.request.user
        if hasattr(user, 'perfil_prestador'):
            return Cliente.objects.filter(perfil=user.perfil_prestador)
        return Cliente.objects.none() # No devolver clientes si no es un prestador

    def perform_create(self, serializer):
        """
        Asigna automáticamente el perfil del prestador autenticado
        al crear un nuevo cliente.
        """
        serializer.save(perfil=self.request.user.perfil_prestador)
