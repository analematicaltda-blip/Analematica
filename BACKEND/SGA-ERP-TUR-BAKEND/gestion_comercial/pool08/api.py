"""Owned, authenticated POOL-08 protocol; no commercial action is dispatched."""
import os
from rest_framework.parsers import BaseParser
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException, ValidationError, NotFound
from apps.core_erp.accounting.agent_army_runtime import authority, identifier
from .contract import (SYSTEM, CURRENT_VERSION, MAX_BYTES, ContractRejected, capabilities,
                       contract_document, decode, http_status, validate_intent)

class ContractFailure(APIException):
    def __init__(self, error):
        self.code = str(error)
        self.status_code = http_status(error)
        super().__init__('El contrato no fue aceptado; no se ejecutó ninguna operación.')

class IntentParser(BaseParser):
    media_type = 'application/json'
    def parse(self, stream, media_type=None, parser_context=None):
        try:
            return decode(stream.read(MAX_BYTES + 1))
        except ContractRejected as exc:
            raise ContractFailure(exc) from None

class Pool08View(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]
    parser_classes = [IntentParser]
    def initial(self, request, *args, **kwargs):
        if os.environ.get('BACKEND_SERVICE') != SYSTEM:
            raise NotFound('Contrato no disponible en este servicio.')
        return super().initial(request, *args, **kwargs)
    def context(self, request):
        if set(request.query_params) != {'provider_id'} or len(request.query_params.getlist('provider_id')) != 1:
            raise ValidationError('Selecciona una sola empresa propia verificada.')
        company, actor, provider = authority(request.user, identifier(request.query_params['provider_id']))
        return {'tenant_ref': str(company.pk), 'actor_ref': str(actor.pk)}
    def handle_exception(self, exception):
        if isinstance(exception, ContractFailure):
            return Response({'detail': {'code': exception.code,
                            'detail': 'Contrato no válido; no se ejecutó ninguna operación.'}},
                            status=exception.status_code, headers={'X-POOL08-Error-Code': exception.code})
        return super().handle_exception(exception)
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store'
        response['X-POOL08-Contract-Version'] = getattr(self, 'version', CURRENT_VERSION)
        return response
    def document(self, request, reader):
        context = self.context(request)
        try:
            result = reader(request.headers.get('X-POOL08-Contract-Version'))
        except ContractRejected as exc:
            raise ContractFailure(exc) from None
        self.version = result['schema_version']
        return Response({**result, 'context': context})

class CapabilitiesView(Pool08View):
    def get(self, request):
        return self.document(request, capabilities)

class ContractView(Pool08View):
    def get(self, request):
        return self.document(request, contract_document)

class IntentValidationView(Pool08View):
    def post(self, request):
        context = self.context(request)
        try:
            result = validate_intent(request.data, **context,
                                     requested_version=request.headers.get('X-POOL08-Contract-Version'))
        except ContractRejected as exc:
            raise ContractFailure(exc) from None
        self.version = result['schema_version']
        return Response(result)

from rest_framework_simplejwt.authentication import JWTAuthentication
from ...web_session import ErpSessionAuthentication
for view in (Pool08View, CapabilitiesView, ContractView, IntentValidationView):
    view.authentication_classes = [JWTAuthentication, ErpSessionAuthentication]
