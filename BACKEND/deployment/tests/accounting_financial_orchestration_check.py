"""Persistent owner-scoped financial rehearsal; no payments or desktop jobs."""
import copy,runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='financial_orchestration_fixture')
from apps.core_erp.accounting import financial_orchestration as engine
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.exceptions import AccountingError
from apps.turismo.services.company_identity import VerifiedCompanyLink
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet

class FinancialRehearsalChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['RecognitionTests']();self.case.setUp();self.f=self.case.case
  self.company=self.f.tenant;self.actor=self.f.actor;self.provider=self.f.provider
  self.scope={'actor':self.actor,'provider_id':self.provider.pk}
  self.intent={'schema':'sgacd-financial-rehearsal-v1','company_id':str(self.company.pk),'request_id':str(uuid.uuid4()),'purpose':'SUPPLIER_PAYMENT','amount':'123.45','currency':'COP','beneficiary_ref':str(uuid.uuid4()),'source_evidence_digest':'a'*64}
 def prepare(self):return engine.prepare(self.company.pk,**self.scope,intent=self.intent,confirmed=True)
 def confirm(self,plan,step_number,**overrides):
  return engine.confirm(self.company.pk,**self.scope,**{'request_id':plan['request_id'],'plan_digest':plan['plan_digest'],'step':step_number,'confirmed':True,**overrides})
 def simulate(self,plan,**overrides):
  return engine.simulate(self.company.pk,**self.scope,**{'request_id':plan['request_id'],'plan_digest':plan['plan_digest'],'confirmed':True,'impact_confirmation':'SIMULAR '+self.intent['amount']+' COP A '+self.intent['beneficiary_ref'],**overrides})
 def approve(self):
  plan=self.prepare();self.confirm(plan,1);self.confirm(plan,2);return plan
 def test_persist_separate_approvals_and_one_replayed_result(self):
  n=JournalEntry.plain_objects.count();p=self.approve();a=self.simulate(p);b=self.simulate(p)
  self.assertFalse(a['replayed']);self.assertTrue(b['replayed']);self.assertEqual(a['status'],'SIMULATED_ONLY')
  for k in ['payment_executed','network_called','desktop_job_created','ledger_written','usable_as_payment_authorization','bank_destination_verified']:self.assertFalse(a[k])
  self.assertEqual(JournalEntry.plain_objects.count(),n)
  self.assertEqual(OutboxEvent.objects.filter(aggregate_root=self.intent['request_id']).count(),4)
 def test_repeated_first_step_never_creates_second_approval(self):
  p=self.prepare();self.confirm(p,1);self.assertTrue(self.confirm(p,1)['replayed'])
  with self.assertRaises(AccountingError):self.simulate(p)
  self.assertIsNone(engine.read(self.company.pk,p['request_id'],'confirmation2'))
 def test_second_step_without_first_denied(self):
  with self.assertRaises(AccountingError):self.confirm(self.prepare(),2)
 def test_missing_second_or_impact_confirmation_denied(self):
  p=self.prepare();self.confirm(p,1)
  with self.assertRaises(AccountingError):self.simulate(p)
  self.confirm(p,2)
  with self.assertRaises(AccountingError):self.simulate(p,impact_confirmation='SIMULAR')
 def test_false_boolean_or_combined_steps_denied(self):
  p=self.prepare()
  for kwargs in ({'confirmed':False},{'confirmed':1},{'step':True},{'step':[1,2]}):
   with self.assertRaises(AccountingError):self.confirm(p,1,**kwargs)
 def test_changed_amount_destination_or_evidence_cannot_reuse_request(self):
  p=self.approve()
  for key,value in [('amount','999.99'),('beneficiary_ref',str(uuid.uuid4())),('source_evidence_digest','b'*64)]:
   old=self.intent[key];self.intent[key]=value
   with self.assertRaises(AccountingError):self.prepare()
   self.intent[key]=old
  self.assertEqual(self.simulate(p)['status'],'SIMULATED_ONLY')
 def test_tampered_persisted_intent_or_confirmation_denied(self):
  p=self.approve();row=engine.read(self.company.pk,p['request_id'],'prepared');old=copy.deepcopy(row.payload);row.payload['intent']['amount']='999.00';row.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.simulate(p)
  row.payload=old;row.save(update_fields=['payload']);a=engine.read(self.company.pk,p['request_id'],'confirmation2');a.payload['plan_digest']='b'*64;a.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.simulate(p)
 def test_expiry_blocks_new_confirmation_and_simulation(self):
  p=self.approve()
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=6)):
   with self.assertRaises(AccountingError):self.confirm(p,2)
   with self.assertRaises(AccountingError):self.simulate(p)
   with self.assertRaises(AccountingError):self.prepare()
 def test_committed_result_recoverable_after_expiry_without_new_action(self):
  p=self.approve();self.simulate(p)
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=6)):
   self.assertTrue(self.simulate(p)['replayed'])
 def test_cancellation_retains_evidence_and_blocks_approvals(self):
  p=self.approve();engine.cancel(self.company.pk,**self.scope,request_id=p['request_id'],plan_digest=p['plan_digest'],confirmed=True)
  for op in [lambda:self.simulate(p),lambda:self.confirm(p,2),self.prepare]:
   with self.assertRaises(AccountingError):op()
  self.assertEqual(OutboxEvent.objects.filter(aggregate_root=p['request_id']).count(),4)
 def test_revoked_binding_blocks_even_result_recovery(self):
  p=self.approve();self.simulate(p);VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  from rest_framework.exceptions import APIException
  with self.assertRaises(APIException):self.simulate(p)
 def test_wrong_digest_missing_actor_and_inactive_company_denied(self):
  p=self.prepare()
  with self.assertRaises(AccountingError):self.confirm(p,1,plan_digest='b'*64)
  with self.assertRaises(AccountingError):engine.prepare(self.company.pk,actor=None,provider_id=self.provider.pk,intent=self.intent)
  self.company.is_active=False;self.company.save(update_fields=['is_active'])
  with self.assertRaises(AccountingError):self.prepare()
 def test_agent_and_another_reviewer_cannot_confirm(self):
  p=self.prepare()
  from django.contrib.auth import get_user_model
  get_user_model().objects.filter(pk=self.actor.pk).update(is_agent=True)
  with self.assertRaises(AccountingError):self.confirm(p,1)
  get_user_model().objects.filter(pk=self.actor.pk).update(is_agent=False)
  reviewer=VerifiedCompanyLink.objects.get(provider=self.provider).reviewed_by
  from rest_framework.exceptions import APIException
  with self.assertRaises(APIException):engine.confirm(self.company.pk,actor=reviewer,provider_id=self.provider.pk,request_id=p['request_id'],plan_digest=p['plan_digest'],step=1,confirmed=True)
 def test_false_preparation_and_impact_review_denied(self):
  with self.assertRaises(AccountingError):engine.prepare(self.company.pk,**self.scope,intent=self.intent,confirmed=False)
  p=self.approve()
  with self.assertRaises(AccountingError):self.simulate(p,confirmed=False)
 def test_strict_contract_and_exact_amounts(self):
  original=dict(self.intent)
  for update in [{'amount':1.1},{'amount':'0.00'},{'amount':'01.00'},{'amount':'1.001'},{'currency':'USD'},{'purpose':'BANK_EXECUTE'},{'private_key':'never-store'},{'company_id':str(uuid.uuid4())}]:
   self.intent={**original,**update}
   with self.assertRaises((AccountingError,ValueError)):self.prepare()
  self.intent=original
 def test_transaction_failure_does_not_leave_confirmation(self):
  p=self.prepare()
  with patch.object(OutboxEvent.objects,'create',side_effect=RuntimeError('Disk failure')):
   with self.assertRaises(RuntimeError):self.confirm(p,1)
  self.assertIsNone(engine.read(self.company.pk,p['request_id'],'confirmation1'))
 def api(self,method,body,actor=None):
  r=APIRequestFactory().post('/fixture/?provider_id='+str(self.provider.pk),body,format='json');force_authenticate(r,user=actor or self.actor)
  return PlanCuentaViewSet.as_view({'post':method})(r)
 def test_owner_http_roundtrip_private_no_execution(self):
  r=self.api('prepare_financial_rehearsal',{'intent':self.intent,'confirmed':True});self.assertEqual(r.status_code,200,r.data);p=r.data
  for step in (1,2):
   r=self.api('confirm_financial_rehearsal',{'request_id':p['request_id'],'plan_digest':p['plan_digest'],'step':step,'confirmed':True});self.assertEqual(r.status_code,200,r.data)
  r=self.api('simulate_financial_rehearsal',{'request_id':p['request_id'],'plan_digest':p['plan_digest'],'confirmed':True,'impact_confirmation':'SIMULAR '+self.intent['amount']+' COP A '+self.intent['beneficiary_ref']});self.assertEqual(r.status_code,200,r.data);self.assertIn('no-store',r['Cache-Control']);self.assertFalse(r.data['payment_executed'])
 def test_http_unknown_arguments_and_foreign_owner_denied(self):
  r=self.api('prepare_financial_rehearsal',{'intent':self.intent,'confirmed':True,'auto_approve':True});self.assertEqual(r.status_code,400)
  from django.contrib.auth import get_user_model
  other=get_user_model()(username='outsider-'+uuid.uuid4().hex,is_active=True);get_user_model().objects.bulk_create([other])
  r=self.api('prepare_financial_rehearsal',{'intent':self.intent,'confirmed':True},actor=other);self.assertIn(r.status_code,(403,404))
if __name__=='__main__':unittest.main()
