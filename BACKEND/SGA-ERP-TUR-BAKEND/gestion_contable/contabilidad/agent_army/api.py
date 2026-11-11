"""API nativa del ejército; no pasa por el backend de SGA-CD."""
from apps.core_erp.accounting import agent_army_api as base
from .services import ARMY,NEKO,SOUP
from .engines import dispatch

from ....web_session import ErpSessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class CatalogView(base.CatalogView):
    army=ARMY
    def get(self,request):
        response=super().get(request)
        response.data['staff']={'operational_general':'JARVI','mission_interpreter':'NEKO','agent_optimizer':'SOUP','general_roles':{'JARVI':'GENERAL_OPERATIVO','NEKO':'GENERAL_CONVERSACIONAL','SOUP':'GENERAL_OPTIMIZADOR_DE_PROCESOS'},
            'voice_agent':{'name':None,'status':'NOT_CONFIGURED','separate_from_command_chain':True,'voice_is_approval':False}}
        return response
class MissionView(base.MissionView):army=ARMY
class StateView(base.StateView):army=ARMY
class EngineView(base.EngineView):
    army=ARMY
    adapter=staticmethod(dispatch)

for view in (CatalogView,MissionView,StateView,EngineView):
    view.authentication_classes=[JWTAuthentication,ErpSessionAuthentication]

class IntakeView(base.ArmyView):
    army=ARMY
    def post(self,request):return base.Response(NEKO.preview(request.user,self.provider(request),request.data))
class OptimizationView(base.ArmyView):
    army=ARMY
    def get(self,request,request_id):return base.Response(SOUP.evaluate(request.user,self.provider(request),str(request_id)))

for view in (IntakeView,OptimizationView):view.authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
