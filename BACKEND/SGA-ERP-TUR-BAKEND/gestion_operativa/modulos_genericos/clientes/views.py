from rest_framework_simplejwt.authentication import JWTAuthentication
from ....web_session import ErpSessionAuthentication
# SaritaUnificado/backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_genericos/clientes/views.py
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Cliente
from .serializers import ClienteSerializer
from ....permissions import IsPrestadorOwner
from rest_framework.exceptions import PermissionDenied, ValidationError, APIException
from django.db.models.deletion import ProtectedError
from django.db import transaction, IntegrityError
from apps.turismo.models import TourismProvider
import uuid

class ClientHistoryConflict(APIException):
    status_code=409
    default_detail='El cliente tiene documentos comerciales vinculados; debe conservarse su historial.'
    default_code='customer_history_protected'

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ClienteViewSet(viewsets.ModelViewSet):
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
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
        from ....company_scope import owned_provider
        return owned_provider(self.request)

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

    def require_unmanaged_customer(self, instance):
        import os
        from django.db import connection
        system=os.environ.get('BACKEND_SERVICE')
        if system not in ('analematica','erp-tur'):return
        if system=='analematica':
            from apps.admin_plataforma.gestion_comercial.pool08.crm_models import CRMContact
        else:
            from apps.prestadores.mi_negocio.gestion_comercial.pool08.crm_models import CRMContact
        if CRMContact._meta.db_table in connection.introspection.table_names() and CRMContact.objects.filter(provider_ref=str(instance.perfil_id),customer_ref=instance.pk).exists():
            raise ClientHistoryConflict('El contacto tiene seguimiento CRM protegido. Actualícelo o registre su baja desde CRM.')

    def perform_update(self, serializer):
        self.require_unmanaged_customer(serializer.instance)
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise ValidationError({'email':'Ya existe un cliente con este correo en la empresa.'})

    def perform_destroy(self, instance):
        self.require_unmanaged_customer(instance)
        from apps.turismo.models import QuotationDraft
        if QuotationDraft.objects.filter(customer_id=instance.pk).exists():
            raise ClientHistoryConflict()
        try:
            with transaction.atomic():
                instance.delete()
        except ProtectedError:
            raise ClientHistoryConflict()
