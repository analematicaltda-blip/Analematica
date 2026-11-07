# SaritaUnificado/backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_genericos/clientes/views.py
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Cliente
from .serializers import ClienteSerializer
from ....permissions import IsPrestadorOwner
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction, IntegrityError
from ..permissions import get_current_tenant
from apps.turismo.models import TourismProvider
import uuid

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los clientes (CRM) de un prestador.
    """
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Este queryset asegura que el usuario solo vea los clientes
        asociados a su propio perfil de prestador.
        """
        return Cliente.objects.filter(perfil=self.get_provider())

    def get_provider(self):
        provider=get_current_tenant()
        if provider is not None:
            provider=TourismProvider.objects.filter(pk=provider.pk,owner=self.request.user).first()
        else:
            providers=TourismProvider.objects.filter(owner=self.request.user)
            if providers.count()!=1:
                raise PermissionDenied('Seleccione explícitamente una empresa propia para gestionar clientes.')
            provider=providers.first()
        if provider is None:
            raise PermissionDenied('No tiene acceso a esta empresa.')
        return provider

    def perform_create(self, serializer):
        """
        Asigna automáticamente el perfil del prestador autenticado
        al crear un nuevo cliente.
        """
        # Assign the concrete proxy target; never accept company identity from payload.
        from ..perfil.models import ProviderProfile
        try:
            with transaction.atomic():
                serializer.save(perfil=ProviderProfile.objects.get(pk=self.get_provider().pk),id_publico=uuid.uuid4())
        except IntegrityError:
            raise ValidationError({'email':'Ya existe un cliente con este correo en la empresa.'})

    def perform_update(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise ValidationError({'email':'Ya existe un cliente con este correo en la empresa.'})
