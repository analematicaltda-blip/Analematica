"""Native Jarvi/Neko/SOUP contracts and bounded local-engine protocol tests."""
import runpy,unittest,uuid,os,json,tempfile,hashlib,httpx,subprocess,sys
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_agent_army_check.py')),run_name='staff_fixture')
from apps.core_erp.accounting import agent_army_engines as engines
from apps.core_erp.accounting import agent_army_runtime as runtime
from apps.admin_plataforma.gestion_contable.contabilidad.agent_army.services import JARVI as AJ,NEKO as AN,SOUP as AS
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.agent_army.services import JARVI as EJ,NEKO as EN,SOUP as ES
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.exceptions import APIException
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.agent_army.api import CatalogView,MissionView
class StaffChecks(unittest.TestCase):
 setUp=fixture['ArmyChecks'].setUp
 payload=fixture['ArmyChecks'].payload
 config=fixture['ArmyChecks'].config
 run_mission=fixture['ArmyChecks'].run_mission
 call=fixture['ArmyChecks'].call
 def intake(self,question='rentabilidad',modality='TEXT'):
  return {'request_id':str(uuid.uuid4()),'question':question,'since':self.day,'until':self.day,'modality':modality}
 def test_jarvi_is_operational_general_of_each_local_chain(self):
  for j in (AJ,EJ):self.assertIn('Jarvi',j.catalog(self.base.user,str(self.base.provider.pk))['nodes'][0]['name'])
  self.assertNotEqual(type(AJ).__module__,type(EJ).__module__)
 def test_neko_prepares_without_dispatch_or_credentials_from_payload(self):
  before=OutboxEvent.objects.count()
  with patch.object(runtime,'read_task',side_effect=AssertionError('Neko must not execute tools')):
   for n in (AN,EN):
    draft=n.preview(self.base.user,str(self.base.provider.pk),self.intake())
    self.assertFalse(draft['mission_executed']);self.assertFalse(draft['draft']['confirmed']);self.assertEqual(draft['commander'],'JARVI')
  self.assertEqual(before,OutboxEvent.objects.count())
 def test_jarvi_requires_separate_confirmation_after_neko(self):
  draft=EN.preview(self.base.user,str(self.base.provider.pk),self.intake())['draft']
  with self.assertRaises(APIException):EJ.execute_mission(self.base.user,str(self.base.provider.pk),draft)
  self.assertEqual(EJ.execute_mission(self.base.user,str(self.base.provider.pk),{**draft,'confirmed':True})['commander'],'JARVI')
 def test_voice_transcript_is_not_financial_or_execution_approval(self):
  for name in ('balance de comprobación','diagnóstico de integridad','liquidez ácida','estado de la cola comercial'):
   d=EN.preview(self.base.user,str(self.base.provider.pk),self.intake(name,'VOICE_TRANSCRIPT'))
   self.assertFalse(d['voice_is_approval']);self.assertTrue(d['confirmation_required'])
 def test_unknown_injection_or_forged_roles_not_routed_by_default(self):
  for payload in [self.intake('DROP TABLE x'),self.intake('paga al proveedor'),{**self.intake(),'origin_user_id':'1'},self.intake('balance de prueba','VOICE_STREAM')]:
   with self.assertRaises(APIException):EN.preview(self.base.user,str(self.base.provider.pk),payload)
 def test_soup_uses_real_tool_samples_and_never_activates_candidates(self):
  r=self.run_mission();d=ES.evaluate(self.base.user,str(self.base.provider.pk),r['request_id'])
  self.assertEqual(d['optimizer'],'SOUP');self.assertEqual(d['total_tool_duration_ns'],sum(row['duration_ns'] for row in r['results']))
  self.assertFalse(d['training_executed']);self.assertFalse(d['activation_allowed']);self.assertIsNone(d['backend_72_tests_passed'])
 def test_soup_recommends_from_measured_latency_without_claiming_sla(self):
  r=self.run_mission()
  with patch.object(EJ,'state',return_value={**r,'results':[{**row,'duration_ns':300000000} for row in r['results']]}):
   d=ES.evaluate(self.base.user,str(self.base.provider.pk),r['request_id'])
  self.assertTrue(any(rec['code']=='PROFILE_READ_LATENCY' for rec in d['recommendations']));self.assertFalse(d['candidate_activated'])
 def test_soup_and_neko_do_not_cross_backend_missions_or_owner(self):
  r=self.run_mission()
  with self.assertRaises(APIException):AS.evaluate(self.base.user,str(self.base.provider.pk),r['request_id'])
  with self.assertRaises(APIException):ES.evaluate(self.base.other,str(self.base.provider.pk),r['request_id'])
 def test_voice_remains_separate_and_no_unidentified_agent_is_invented(self):
  req=fixture['APIRequestFactory']().get('/army/?provider_id='+str(self.base.provider.pk));fixture['force_authenticate'](req,user=self.base.user)
  d=CatalogView.as_view()(req).data;self.assertEqual(d['staff']['operational_general'],'JARVI');self.assertEqual(d['staff']['agent_optimizer'],'SOUP')
  self.assertIsNone(d['staff']['voice_agent']['name']);self.assertEqual(d['staff']['voice_agent']['status'],'NOT_CONFIGURED')
 def test_institutional_tourism_does_not_expose_erp_army(self):
  with patch.dict(os.environ,{'BACKEND_SERVICE':'turismo'}):self.assertEqual(self.call(MissionView).status_code,404)
 def test_open_duet_sends_only_plan_and_requires_plan_mode_ack(self):
  calls=[];plan={'system':'erp-tur','instruction':'Planifica revisión humana.','tasks':[{'id':'trial_balance','status':'VERIFIED_READ'}]}
  def handler(request):
   body=json.loads(request.content);calls.append((request.url.path,body));number=len(calls)
   self.assertEqual(request.url.host,'127.0.0.1');self.assertNotIn(str(self.base.tenant.pk),request.content.decode())
   return httpx.Response(201,json={'id':number,**({'approval_mode':'plan','memory_enabled':False} if number==1 else {})})
  cfg={'origin':'http://127.0.0.1:9998','token':'synthetic-local-token','provider':'codex'}
  r=engines.duet_plan(cfg,plan,httpx.MockTransport(handler));self.assertEqual(r['state'],'QUEUED');self.assertEqual(len(calls),3)
  self.assertEqual(calls[0][1]['approval_mode'],'plan');self.assertFalse(calls[0][1]['memory_enabled'])
 def test_open_duet_unsafe_mode_or_redirect_stops_before_turn(self):
  cfg={'origin':'http://127.0.0.1:9998','token':'synthetic-local-token','provider':'codex'};plan={'system':'erp-tur','instruction':'Read only','tasks':[]}
  for response in [httpx.Response(201,json={'id':1,'approval_mode':'auto','memory_enabled':False}),httpx.Response(302,headers={'Location':'https://external.example/'})]:
   calls=[]
   def handler(req):calls.append(1);return response
   with self.assertRaises(engines.EngineOutcomeUnknown):engines.duet_plan(cfg,plan,httpx.MockTransport(handler))
   self.assertEqual(len(calls),1)
 def test_open_duet_duplicate_or_oversized_json_rejected(self):
  cfg={'origin':'http://127.0.0.1:9998','token':'synthetic-local-token','provider':'codex'};plan={'system':'erp-tur','instruction':'Read only'}
  for content in [b'{"id":1,"id":2}',b'x'*40000]:
   with self.assertRaises(engines.EngineOutcomeUnknown):engines.duet_plan(cfg,plan,httpx.MockTransport(lambda r:httpx.Response(201,content=content)))
 def test_configuration_rejects_external_origin_and_token_in_url(self):
  p=EJ.policy.prefix+'_DUET'
  for origin in ['https://example.com','http://127.0.0.1:9998/api','http://a:b@127.0.0.1:9998','http://127.0.0.1:9998?token=x']:
   with patch.dict(os.environ,{**self.config(),p+'_ORIGIN':origin}),self.assertRaises(engines.EngineUnavailable):engines.configuration(EJ.policy,self.base.user,self.base.tenant,'open-duet')
 def binary(self,directory,output):
  path=Path(directory)/'native-fixture';path.write_text('#!/usr/bin/env python3\nimport sys\nassert sys.argv[1:]==["status"]\nprint('+repr(output)+')\n');path.chmod(0o700)
  return {'binary':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 def test_desktop_native_protocol_only_invokes_status(self):
  with tempfile.TemporaryDirectory() as private:
   result=engines.desktop_probe(self.binary(private,'{"platform":"linux","supported_surfaces":[]}'))
  self.assertEqual(result['state'],'PROBED');self.assertFalse(result['hardware_qualified']);self.assertFalse(result['desktop_action_executed'])
 def test_desktop_output_bound_and_integrity_change_rejected(self):
  with tempfile.TemporaryDirectory() as private:
   cfg=self.binary(private,'x'*40000)
   with self.assertRaises(engines.EngineOutcomeUnknown):engines.desktop_probe(cfg)
   Path(cfg['binary']).write_text('changed')
   with self.assertRaises(engines.EngineUnavailable):engines.desktop_probe(cfg)
 def test_native_analematica_bootstrap_has_no_sga_cd_api_dependency(self):
  root=Path(__file__).resolve().parents[3]
  script="""import os,sys,tempfile,json
from pathlib import Path
root=Path(sys.argv[1]);sys.path[:0]=[str(root/'BACKEND/deployment')]
from init_local import initialize
with tempfile.TemporaryDirectory() as private:
 initialize(private)
 config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
 os.environ.update(config,BACKEND_SERVICE='analematica',DATABASE_URL='sqlite:///:memory:',DJANGO_SETTINGS_MODULE='deployment.army_settings',SGACD_API_URL='http://127.0.0.1:1')
 sys.path.insert(0,str(root/'BACKEND/ANALEMATICA-BACKEND'))
 from deployment.army_wsgi import application
 from django.conf import settings
 from django.core.management import call_command
 call_command('check',fail_level='ERROR')
 assert settings.ROOT_URLCONF=='deployment.army_urls'
 assert not any(n.startswith('app.services') or n.startswith('app.agents') for n in sys.modules)
 print(json.dumps({'native':True,'sgacd_required':False,'root_urlconf':settings.ROOT_URLCONF}))
"""
  process=subprocess.run([sys.executable,'-c',script,str(root)],cwd=root,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=45)
  self.assertEqual(process.returncode,0,process.stderr[-4000:]);self.assertTrue(json.loads(process.stdout.splitlines()[-1])['native'])
if __name__=='__main__':unittest.main(verbosity=2)
