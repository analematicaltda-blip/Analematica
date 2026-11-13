"""Legacy read adapter. Authoritative writes use the reviewed opportunity commands."""
import os
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound,PermissionDenied,ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from ...web_session import ErpSessionAuthentication
from ..pool08.identity import resolve_access
from ..pool08.access_protocol import AccessFault
from .models import Opportunity
from .serializers import OpportunitySerializer

class OpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Opportunity.objects.none()
    serializer_class=OpportunitySerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
    def get_queryset(self):
        if os.environ.get('BACKEND_SERVICE')!='erp-tur':raise NotFound()
        values=self.request.query_params.getlist('provider_id')
        if len(values)!=1:raise ValidationError('Selecciona una sola empresa verificada.')
        try:access=resolve_access(self.request.user,values[0])
        except AccessFault:raise PermissionDenied('No tienes acceso comercial a esta empresa.') from None
        if not access.session()['capability_permissions'].get('crm.prospect.manage'):raise PermissionDenied('Permiso CRM requerido.')
        return Opportunity.objects.filter(provider_id=values[0],is_active=True)
    @action(detail=True,methods=['put'],url_path='move')
    def move_opportunity(self,request,pk=None):
        self.get_object()
        return Response({'code':'REVIEWED_OPPORTUNITY_COMMAND_REQUIRED','detail':'Actualiza la etapa desde Oportunidades y embudo, con revisión e historial.'},status=409)
    def finalize_response(self,request,response,*args,**kwargs):
        response=super().finalize_response(request,response,*args,**kwargs);response['Cache-Control']='no-store';return response
