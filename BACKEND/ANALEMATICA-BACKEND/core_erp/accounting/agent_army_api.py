"""Native backend API primitives; service/policy is bound by each backend module."""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError,NotFound
import os
from .agent_army_runtime import identifier
from .agent_army_engines import EngineUnavailable,EngineOutcomeUnknown
from .exceptions import AccountingError
from .query_parser import AccountingQueryJSONParser

class ArmyView(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes=[AccountingQueryJSONParser]
    army=None
    def initial(self,request,*args,**kwargs):
        if os.environ.get('BACKEND_SERVICE')=='turismo':raise NotFound('Servicio no disponible en la plataforma institucional.')
        return super().initial(request,*args,**kwargs)
    def provider(self,request):
        if set(request.query_params)!={'provider_id'} or len(request.query_params.getlist('provider_id'))!=1:
            raise ValidationError('Selecciona un único prestador autorizado.')
        return identifier(request.query_params['provider_id'])
    def handle_exception(self,exception):
        if isinstance(exception,AccountingError):exception=ValidationError({'code':'ARMY_ACCOUNTING_REVIEW_REQUIRED','detail':'La misión requiere revisión de su fuente o contexto.'})
        if isinstance(exception,(EngineUnavailable,EngineOutcomeUnknown)):
            return Response({'code':'ARMY_ENGINE_UNAVAILABLE','detail':'Motor local no configurado o resultado no verificado; no se ejecutaron operaciones financieras.'},status=503)
        return super().handle_exception(exception)
    def finalize_response(self,request,response,*args,**kwargs):
        response=super().finalize_response(request,response,*args,**kwargs);response['Cache-Control']='no-store';return response

class CatalogView(ArmyView):
    def get(self,request):
        from .agent_army_engines import configured
        data=self.army.catalog(request.user,self.provider(request));data['engines']=configured(self.army.policy)
        return Response(data)

class MissionView(ArmyView):
    def post(self,request):return Response(self.army.run(request.user,self.provider(request),request.data))

class StateView(ArmyView):
    def get(self,request,request_id):return Response(self.army.state(request.user,self.provider(request),str(request_id)))

class EngineView(ArmyView):
    adapter=None
    def post(self,request,request_id,engine):
        return Response(self.army.engine_plan(request.user,self.provider(request),str(request_id),engine,request.data,self.adapter))
