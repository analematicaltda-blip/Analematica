from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .domain.models import OperacionComercial
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from .serializers import OperacionSerializer, ClienteSerializer
from rest_framework.views import APIView
from rest_framework.exceptions import APIException

class CommercialWorkflowUnavailable(APIException):
    status_code = 503
    default_detail = 'Operaciones comerciales pendientes de contrato empresarial, tarifas y validación fiscal.'
    default_code = 'commercial_workflow_not_enabled'

class OperacionComercialViewSet(viewsets.ModelViewSet):
    # Preserve router identity without evaluating an unverified tenant mapping.
    queryset = OperacionComercial.objects.none()
    serializer_class = OperacionSerializer
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        raise CommercialWorkflowUnavailable()

    @action(detail=False)
    def stats(self, request):
        raise CommercialWorkflowUnavailable()

from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.views import ClienteViewSet as OwnedClienteViewSet

class ClienteViewSet(OwnedClienteViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

class POSView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Never fabricate a completed sale or fiscal invoice from client totals.
        raise CommercialWorkflowUnavailable()

class QuotationPreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        from .quote_preview import preview
        from rest_framework.response import Response
        response=Response(preview(request.user,request.data))
        response['Cache-Control']='no-store'
        return response
