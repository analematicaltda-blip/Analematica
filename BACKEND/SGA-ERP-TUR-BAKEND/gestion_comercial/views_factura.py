from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..web_session import ErpSessionAuthentication
from ..company_scope import owned_provider
from apps.turismo.services.company_identity import resolve_company
from apps.core_erp.accounting.http_privacy import PrivateAccountingResponseMixin
from .serializers_factura import FacturaSerializer
from .models.FacturaElectronica import FacturaElectronica

class FacturaViewSet(PrivateAccountingResponseMixin,viewsets.ReadOnlyModelViewSet):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
    queryset = FacturaElectronica.objects.none()
    serializer_class = FacturaSerializer

    def company(self):
        user=get_user_model().objects.filter(pk=self.request.user.pk,is_active=True).first()
        if user is None:raise PermissionDenied('Se requiere un titular activo.')
        self.request.user=user
        return resolve_company(user,owned_provider(self.request).pk).tenant

    def get_queryset(self):
        company=self.company()
        # Legacy tenant strings are not guessed to be provider IDs. Both sides
        # of the invoice/operation relation must agree with the reviewed Tenant.
        return FacturaElectronica.objects.filter(tenant_id=str(company.pk),operacion_comercial__tenant_id=company.pk).order_by('-fecha_envio_dian','pk')

    @action(detail=True)
    def pdf(self, request, pk=None):
        self.get_object()
        return Response({'code':'FISCAL_DOCUMENT_NOT_GENERATED','detail':'No hay PDF fiscal verificado disponible.'},status=503)

    @action(detail=False, methods=['post'])
    def trigger_dian(self, request):
        self.company()
        return Response({'code':'DIAN_VERIFIED_TRANSPORT_UNAVAILABLE','detail':'Consulta el diagnóstico DIAN. No se creó ni envió una factura.','fiscal_accepted':False,'network_called':False},status=503)
