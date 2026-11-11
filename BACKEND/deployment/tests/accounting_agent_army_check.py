"""Independent native backend armies on real disposable ORM and DRF data."""
import copy,runpy,unittest,uuid,os,json,tempfile,hashlib
from pathlib import Path
from unittest.mock import patch
from decimal import localcontext,Inexact,Rounded
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='army_fixture')
from apps.admin_plataforma.gestion_contable.contabilidad.agent_army.services import ARMY as ANA
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.agent_army.services import ARMY as ERP
from apps.core_erp.accounting import agent_army_runtime as runtime
from apps.core_erp.accounting import agent_army_engines as engines
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.exceptions import AccountingError
from apps.turismo.models import VerifiedCompanyLink
from django.utils import timezone
from django.db import connection
from rest_framework.exceptions import APIException
from rest_framework.test import APIRequestFactory,force_authenticate,APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.test import override_settings
from django.urls import path,include
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.agent_army import api as erp_api
from apps.admin_plataforma.gestion_contable.contabilidad.agent_army import api as ana_api
class TestURLs:
 urlpatterns=[path('erp/',include('apps.prestadores.mi_negocio.gestion_contable.contabilidad.agent_army.urls')),path('ana/',include('apps.admin_plataforma.gestion_contable.contabilidad.agent_army.urls'))]
class ArmyChecks(unittest.TestCase):
 def setUp(self):
  environment=patch.dict(os.environ,{'BACKEND_SERVICE':'erp-tur'});environment.start();self.addCleanup(environment.stop)
  self.base=fixture['AdapterTests']();self.base.setUp();self.addCleanup(self.base.doCleanups);self.day=timezone.localdate().isoformat()
 def payload(self,tasks=None):return {'request_id':str(uuid.uuid4()),'tasks':tasks or ['trial_balance','profitability'],'since':self.day,'until':self.day,'confirmed':True}
 def run_mission(self,army=ERP,body=None):return army.run(self.base.user,str(self.base.provider.pk),body or self.payload())
 def config(self,army=ERP):
  p=army.policy.prefix+'_DUET';return {p+'_ENABLED':'1',p+'_OWNER_ID':str(self.base.user.pk),p+'_COMPANY_ID':str(self.base.tenant.pk),p+'_ORIGIN':'http://127.0.0.1:9998',p+'_TOKEN':'synthetic-token-not-used-remotely',p+'_PROVIDER':'codex'}
 def call(self,view,body=None,user=None,query=None,**kwargs):
  req=APIRequestFactory().post('/army/?provider_id='+str(query or self.base.provider.pk),body or self.payload(),format='json');force_authenticate(req,user=user or self.base.user);return view.as_view()(req,**kwargs)
 def test_two_owned_structures_have_full_six_ranks_no_shared_agent_ids(self):
  a=ANA.catalog(self.base.user,str(self.base.provider.pk));b=ERP.catalog(self.base.user,str(self.base.provider.pk))
  self.assertEqual(a['logical_agents'],29);self.assertEqual(b['logical_agents'],29)
  self.assertEqual({n['rank'] for n in a['nodes']},{'GENERAL','CORONEL','CAPITAN','TENIENTE','SARGENTO','SOLDADO'})
  self.assertTrue({n['id'] for n in a['nodes']}.isdisjoint(n['id'] for n in b['nodes']))
  a['nodes'].clear();self.assertEqual(len(ANA.catalog(self.base.user,str(self.base.provider.pk))['nodes']),29)
 def test_actual_reports_and_full_rank_trace_without_ledger_writes(self):
  self.base.post();before=(JournalEntry.plain_objects.count(),LedgerEntry.plain_objects.count());result=self.run_mission()
  self.assertEqual(result['status'],'COMPLETED_READ');self.assertFalse(result['ledger_written']);self.assertFalse(result['network_called'])
  for row in result['results']:
   self.assertEqual(len(row['trace']),7);self.assertEqual(row['status'],'VERIFIED_READ');self.assertIsNotNone(row['data_digest'])
  self.assertEqual(before,(JournalEntry.plain_objects.count(),LedgerEntry.plain_objects.count()))
 def test_all_tasks_propagate_review_without_fiscal_or_chain_certification(self):
  mapping=self.base.ratio_mapping();self.base.configure_ratio(mapping);self.base.post()
  result=self.run_mission(body=self.payload(list(runtime.TASKS)));self.assertEqual(len(result['results']),5)
  self.assertEqual(result['status'],'REQUIRES_REVIEW');rows={r['task']:r for r in result['results']}
  self.assertFalse(rows['commercial_outbox']['data']['fiscal_receipt_verified']);self.assertFalse(rows['integrity']['data']['full_ledger_certified'])
 def test_missing_policy_is_blocked_not_fabricated(self):
  r=self.run_mission(body=self.payload(['quick_ratio']));self.assertEqual(r['results'][0]['status'],'REQUIRES_REVIEW');self.assertIsNone(r['results'][0]['data']['value'])
 def test_replay_uses_stored_snapshot_without_running_tools(self):
  body=self.payload();r=self.run_mission(body=body)
  with patch.object(runtime,'read_task',side_effect=AssertionError('Tool must not rerun')):
   again=self.run_mission(body=body)
  self.assertTrue(again['replayed']);self.assertEqual(again['results'],r['results'])
 def test_same_request_conflict_is_rejected(self):
  body=self.payload();self.run_mission(body=body);body['tasks']=['commercial_outbox']
  with self.assertRaises(AccountingError):self.run_mission(body=body)
 def test_namespace_isolation_even_same_company_and_request_uuid(self):
  body=self.payload();self.run_mission(ANA,body)
  with self.assertRaises(APIException):ERP.state(self.base.user,str(self.base.provider.pk),body['request_id'])
  self.run_mission(ERP,body);self.assertNotEqual(ANA.event_id(self.base.tenant.pk,body['request_id']),ERP.event_id(self.base.tenant.pk,body['request_id']))
 def test_wrong_owner_foreign_provider_and_revocation_denied(self):
  for army in (ANA,ERP):
   with self.assertRaises(APIException):army.run(self.base.other,str(self.base.provider.pk),self.payload())
  VerifiedCompanyLink.objects.filter(pk=self.base.link.pk).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.run_mission()
 def test_delegated_agent_cannot_impersonate_owner(self):
  self.base.user.is_agent=True;self.addCleanup(lambda:delattr(self.base.user,'is_agent'))
  with self.assertRaises(APIException):self.run_mission()
 def test_untrusted_write_tools_dates_scope_or_shell_fields_rejected(self):
  for extra in [{'tasks':['post_entry']},{'tasks':['trial_balance']*2},{'company_id':str(self.base.foreign.pk)},{'command':'rm -rf /'},{'confirmed':1},{'since':'20261111'},{'until':'2000-01-01'}]:
   with self.subTest(extra=extra),self.assertRaises(APIException):self.run_mission(body={**self.payload(),**extra})
 def test_caller_decimal_context_does_not_change_report(self):
  self.base.post();expected=self.run_mission()['results']
  with localcontext() as c:
   c.prec=2;c.traps[Inexact]=True;c.traps[Rounded]=True
   actual=self.run_mission()['results']
  clean=lambda rows:[{k:v for k,v in r.items() if k!='duration_ns'} for r in rows]
  self.assertEqual(clean(expected),clean(actual))
 def test_unexpected_failure_rolls_back_mission_and_audit(self):
  before=OutboxEvent.objects.count()
  with patch.object(runtime,'read_task',side_effect=RuntimeError('private diagnostic')):
   with self.assertRaises(RuntimeError):self.run_mission()
  self.assertEqual(OutboxEvent.objects.count(),before)
 def test_foreign_or_false_arithmetic_source_does_not_leak_data(self):
  for source in [{'tenant_id':str(self.base.foreign.pk),'private':'DO_NOT_DISCLOSE'}, {'tenant_id':str(self.base.tenant.pk),'posted_only':True,'valuation':'base_currency','cutoff_date':self.day,'total_debit':'10.00','total_credit':'11.00','lines':[]}]:
   with patch.object(runtime,'read_task',return_value=source):result=self.run_mission(body=self.payload(['trial_balance']))
   self.assertEqual(result['results'][0]['status'],'BLOCKED');self.assertNotIn('DO_NOT_DISCLOSE',str(result))
 def test_persisted_report_tampering_rejected(self):
  r=self.run_mission();row=OutboxEvent.objects.get(pk=ERP.event_id(self.base.tenant.pk,r['request_id']));row.payload['report']['financial_action_authorized']=True;row.save()
  with self.assertRaises(AccountingError):ERP.state(self.base.user,str(self.base.provider.pk),r['request_id'])
 def test_persisted_malformed_request_rejected_cleanly(self):
  r=self.run_mission();row=OutboxEvent.objects.get(pk=ERP.event_id(self.base.tenant.pk,r['request_id']));row.payload['request']=[];row.save()
  with self.assertRaises(AccountingError):ERP.state(self.base.user,str(self.base.provider.pk),r['request_id'])
 def test_recomputed_hash_cannot_enable_financial_actions(self):
  r=self.run_mission();row=OutboxEvent.objects.get(pk=ERP.event_id(self.base.tenant.pk,r['request_id']));body=row.payload;body['report']['financial_action_authorized']=True;body['digest']=runtime.fingerprint({k:body[k] for k in ('scope','request','report')});row.save()
  with self.assertRaises(AccountingError):ERP.state(self.base.user,str(self.base.provider.pk),r['request_id'])
 def test_native_apis_are_separate_and_permission_bound(self):
  for view in (ana_api.MissionView,erp_api.MissionView):
   self.assertEqual(self.call(view).status_code,200)
   self.assertEqual(self.call(view,user=self.base.other).status_code,403)
 def test_real_jwt_routes_for_both_owned_api_modules(self):
  client=APIClient(HTTP_HOST='localhost');token=str(AccessToken.for_user(self.base.user))
  with override_settings(ROOT_URLCONF=TestURLs):
   self.assertEqual(client.get('/erp/?provider_id='+str(self.base.provider.pk)).status_code,401)
   client.credentials(HTTP_AUTHORIZATION='Bearer '+token)
   for base in ('/erp/','/ana/'):
    body=self.payload();response=client.post(base+'missions/?provider_id='+str(self.base.provider.pk),body,format='json');self.assertEqual(response.status_code,200,response.content)
    data=response.json();data=data['data'] if data.get('success') is True else data
    response=client.get(base+'missions/'+body['request_id']+'/?provider_id='+str(self.base.provider.pk));self.assertEqual(response.status_code,200)
 def test_engine_configuration_is_separate_and_requires_owner_company(self):
  with patch.dict(os.environ,self.config(),clear=False):
   engines.configuration(ERP.policy,self.base.user,self.base.tenant,'open-duet')
   with self.assertRaises(engines.EngineUnavailable):engines.configuration(ANA.policy,self.base.user,self.base.tenant,'open-duet')
   with self.assertRaises(APIException):engines.configuration(ERP.policy,self.base.other,self.base.tenant,'open-duet')
 def test_engine_metadata_has_no_financial_values_or_company_identity(self):
  r=self.run_mission();plan=ERP.plan(self.base.user,str(self.base.provider.pk),r['request_id']);raw=json.dumps(plan)
  self.assertNotIn(str(self.base.tenant.pk),raw);self.assertNotIn(str(self.base.provider.pk),raw);self.assertNotIn('total_debit',raw);self.assertEqual(plan['tools_allowed'],[])
 def test_engine_calls_are_outside_transaction_and_not_automatically_repeated(self):
  r=self.run_mission();calls=[]
  def adapter(*args):
   self.assertFalse(connection.in_atomic_block);calls.append(1)
   return {'engine':'open-duet','state':'QUEUED','financial_action_authorized':False}
  with patch.dict(os.environ,self.config(),clear=False):
   first=ERP.engine_plan(self.base.user,str(self.base.provider.pk),r['request_id'],'open-duet',{'confirmed':True,'share_plan':True},adapter)
   again=ERP.engine_plan(self.base.user,str(self.base.provider.pk),r['request_id'],'open-duet',{'confirmed':True,'share_plan':True},adapter)
  self.assertEqual(len(calls),1);self.assertTrue(again['replayed']);self.assertFalse(first['financial_action_authorized'])
 def test_uncertain_engine_outcome_is_durable_and_not_retried(self):
  r=self.run_mission()
  with patch.dict(os.environ,self.config(),clear=False),patch.object(engines,'duet_plan',side_effect=engines.EngineOutcomeUnknown('private')) as worker:
   adapter=lambda actor,company,engine,plan:engines.execute(ERP.policy,actor,company,engine,plan)
   for _ in range(2):result=ERP.engine_plan(self.base.user,str(self.base.provider.pk),r['request_id'],'open-duet',{'confirmed':True,'share_plan':True},adapter)
  self.assertEqual(worker.call_count,1);self.assertEqual(result['state'],'OUTCOME_UNKNOWN')
 def test_engine_share_consent_cannot_be_boolean_alias(self):
  r=self.run_mission()
  for body in [{'confirmed':1,'share_plan':1},{'confirmed':True},{'confirmed':True,'share_plan':True,'company_id':'x'}]:
   with self.assertRaises(APIException):ERP.engine_plan(self.base.user,str(self.base.provider.pk),r['request_id'],'open-duet',body,lambda *a:None)
 def test_independence_from_sga_cd_source_packages(self):
  root=Path(__file__).resolve().parents[3]
  for folder in [root/'BACKEND/ANALEMATICA-BACKEND/gestion_contable/contabilidad/agent_army',root/'BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/agent_army']:
   for path in folder.glob('*.py'):
    text=path.read_text();self.assertNotIn('from app.',text);self.assertNotIn('import app.services',text)
 def test_replay_and_recovery_verify_with_independent_decimal_context(self):
  self.base.post();body=self.payload();expected=self.run_mission(body=body)
  with localcontext() as c:
   c.prec=2;c.traps[Inexact]=True;c.traps[Rounded]=True
   self.assertEqual(ERP.state(self.base.user,str(self.base.provider.pk),body['request_id']),expected)
   self.assertTrue(self.run_mission(body=body)['replayed'])
 def test_recomputed_hash_cannot_rewrite_chain_of_command(self):
  result=self.run_mission();row=OutboxEvent.objects.get(pk=ERP.event_id(self.base.tenant.pk,result['request_id']))
  body=row.payload;body['report']['results'][0]['trace'][0]='foreign:general'
  body['digest']=runtime.fingerprint({k:body[k] for k in ('scope','request','report')});row.save()
  with self.assertRaises(AccountingError):ERP.state(self.base.user,str(self.base.provider.pk),result['request_id'])
 def test_withdrawn_authority_rolls_back_mission_audit(self):
  original=runtime.read_task;before=OutboxEvent.objects.count()
  def revoke(*args):
   value=original(*args);VerifiedCompanyLink.objects.filter(pk=self.base.link.pk).update(revoked_at=timezone.now());return value
  with patch.object(runtime,'read_task',side_effect=revoke),self.assertRaises(APIException):self.run_mission()
  self.assertEqual(OutboxEvent.objects.count(),before);self.base.link.refresh_from_db();self.assertIsNone(self.base.link.revoked_at)
 def test_combined_report_bound_does_not_persist_partial_success(self):
  before=OutboxEvent.objects.count()
  with patch.object(runtime,'MAX_REPORT',50),self.assertRaises(AccountingError):self.run_mission()
  self.assertEqual(OutboxEvent.objects.count(),before)
 def test_each_mission_really_delegates_through_all_internal_ranks(self):
  calls=[];original=runtime.CommandNode.dispatch
  def record(node,*args,**kwargs):calls.append(node.node['rank']);return original(node,*args,**kwargs)
  with patch.object(runtime.CommandNode,'dispatch',new=record):result=self.run_mission(body=self.payload(['trial_balance']))
  self.assertEqual(calls,['GENERAL','CORONEL','CAPITAN','TENIENTE','SARGENTO'])
  self.assertEqual(len(result['results'][0]['trace']),7)
 def test_failed_reader_does_not_claim_checker_executed(self):
  with patch.object(runtime,'read_task',side_effect=AccountingError('source unavailable')):
   result=self.run_mission(body=self.payload(['trial_balance']))
  row=result['results'][0];self.assertEqual(row['status'],'BLOCKED');self.assertEqual(len(row['trace']),6)
  self.assertNotIn('verify',row['trace'][-1]);self.assertEqual(ERP.state(self.base.user,str(self.base.provider.pk),result['request_id'])['results'][0]['trace'],row['trace'])
if __name__=='__main__':unittest.main(verbosity=2)
