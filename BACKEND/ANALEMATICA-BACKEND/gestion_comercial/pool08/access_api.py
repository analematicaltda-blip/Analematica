"""Own native administration; institutional roles never imply business access."""
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from .api import Pool08View
from .identity import resolve_access
from .access_admin import AccessAdmin
from .access_protocol import AccessFault
from .crm_api import CRMView
from .crm import CRMError

class AccessAdminView(Pool08View):
    def service(self,request):
        if set(request.query_params)!={'provider_id'} or len(request.query_params.getlist('provider_id'))!=1:
            raise ValidationError('Selecciona una sola empresa verificada.')
        return AccessAdmin(resolve_access(request.user,request.query_params['provider_id']),CRMView().service(request))
    def handle_exception(self,exc):
        if isinstance(exc,(AccessFault,CRMError)):return Response({'code':str(exc)},status=exc.status)
        return super().handle_exception(exc)
    def get(self,request,section,key=None):
        if section=='commands':raise MethodNotAllowed('GET')
        return Response(self.service(request).read(section,key))
    def post(self,request,section,key=None):
        if section!='commands' or key is not None:raise MethodNotAllowed('POST')
        return Response(self.service(request).command(request.data))
