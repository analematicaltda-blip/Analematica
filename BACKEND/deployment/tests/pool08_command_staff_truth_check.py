"""Execute canonical legacy methods without model/network imports or constructor."""
import ast,asyncio,unittest,typing
from pathlib import Path
from types import SimpleNamespace
SOURCE=Path(__file__).resolve().parents[2]/'ANALEMATICA-BACKEND/agents/legacy_command_staff.py'
class Envelope:
 def __init__(self,**kwargs):self.__dict__.update(kwargs)
def method(name):
 node=next(n for n in ast.walk(ast.parse(SOURCE.read_text())) if isinstance(n,ast.AsyncFunctionDef) and n.name==name);ns={'Dict':dict,'Any':typing.Any,'Optional':typing.Optional,'List':list,'MissionDispatchEnvelope':Envelope,'InputModality':SimpleNamespace(TEXT='TEXT'),'InteractionPriority':SimpleNamespace(NORMAL='NORMAL')};exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(SOURCE),'exec'),ns);return ns[name]
class Checks(unittest.TestCase):
 def test_legacy_commercial_routes_never_invoke_textual_colonels(self):
  class Colonel:
   async def ainvoke(self,*args,**kwargs):raise AssertionError('Legacy textual colonel must not run')
  own=SimpleNamespace(colonel_redes=Colonel(),colonel_ventas=Colonel())
  for division,utterance in [('MARKETING','publicar ads'),('VENTAS','prospecto'),('UNKNOWN','consulta desconocida')]:
   result=asyncio.run(method('execute_mission')(own,Envelope(target_division=division,raw_utterance=utterance,origin_user_id='1',origin_tenant_id='1',user_roles=[],intent_action='TEST',extracted_parameters={})));self.assertEqual(result['status'],'BLOCKED');self.assertFalse(result['provider_action_executed'])
 def test_neko_propagates_block_and_does_not_invent_admin_role(self):
  class Jarvi:
   async def execute_mission(inner,envelope):
    self.assertEqual(envelope.user_roles,[]);return {'status':'BLOCKED','code':'VERIFIED_COMMERCIAL_MISSION_REQUIRED'}
  result=asyncio.run(method('handle_user_command')(SimpleNamespace(jarvi=Jarvi()),'publicar ads'));self.assertIn('BLOCKED',result);self.assertNotIn('COMPLETED_SUCCESS',result)
 def test_unverified_text_is_never_labelled_completed_success(self):
  class Jarvi:
   async def execute_mission(inner,envelope):return {'final_report':{'text':'Texto sin recibo de herramienta'}}
  result=asyncio.run(method('handle_user_command')(SimpleNamespace(jarvi=Jarvi()),'deporte',roles=['operador']));self.assertIn('NO_VERIFICADO',result);self.assertNotIn('COMPLETED_SUCCESS',result)
if __name__=='__main__':unittest.main()
