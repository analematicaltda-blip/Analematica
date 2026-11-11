"""Disposable real-ledger checks for zero-activity bank period evidence."""
import runpy,unittest,uuid,copy,sys
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_period_check.py')),run_name='empty_period_fixture')
from apps.core_erp.accounting import bank_empty_period as engine
from apps.core_erp.accounting.bank_period import assess
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.models import Account
from django.utils import timezone
class EmptyPeriodChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['BankPeriodChecks']();self.base.setUp();self.case=self.base.case;self.day=self.base.base.bank.entry.date-timedelta(days=1)
  self.case.period.period_start=self.day-timedelta(days=1);self.case.period.save()
  self.scope={'actor':self.case.user};self.period={'since':self.day.isoformat(),'until':self.day.isoformat(),'opening':'0.00','closing':'0.00','statement_complete':True,'evidence_digest':'c'*64}
  self.args={**self.scope,'request_id':str(uuid.uuid4()),'account_id':str(self.case.a.pk),'period':self.period,'no_bank_movements':True,'confirmed':True}
 def review(self,**kw):return engine.review(self.case.tenant.pk,**{**self.args,**kw})
 def confirm(self,r,**kw):return engine.confirm(self.case.tenant.pk,**{**self.scope,'review_id':r['review_id'],'confirmed':True,**kw})
 def state(self,r):return engine.state(self.case.tenant.pk,**self.scope,review_id=r['review_id'])
 def test_two_confirmations_no_synthetic_bank_rows_or_ledger_writes(self):
  before=self.base.base.counts();r=self.review();self.assertFalse(r['period_reconciled']);a=self.confirm(r);self.assertTrue(a['period_reconciled']);self.assertFalse(a['bank_verified']);self.assertEqual(a['assessment']['ledger_period_rows'],0);self.assertEqual(before,self.base.base.counts());self.assertEqual(a,self.confirm(r))
 def test_plain_assessment_still_requires_nonempty_rows(self):
  with self.assertRaises(AccountingError):assess(self.case.tenant,self.case.a.pk,self.period,[],[])
 def test_no_inferred_opening_balance(self):
  self.base.post_cash('5.00',self.day-timedelta(days=1))
  with self.assertRaises(AccountingError):self.review()
  a=self.confirm(self.review(period={**self.period,'opening':'5.00','closing':'5.00'}));self.assertEqual(a['assessment']['ledger_opening'],'5.00')
 def test_declared_opening_and_closing_must_match(self):
  with self.assertRaises(AccountingError):self.review(period={**self.period,'closing':'1.00'})
 def test_existing_offsetting_cash_movements_are_not_a_zero_activity_period(self):
  self.base.post_cash('3.00',self.day)
  with self.assertRaises(AccountingError):self.review()
 def test_backdated_posting_invalidates_confirmation_and_recovered_status(self):
  r=self.review();self.confirm(r);self.base.post_cash('3.00',self.day);a=self.state(r);self.assertTrue(a['historically_confirmed']);self.assertFalse(a['period_reconciled']);self.assertTrue(a['requires_review']);self.assertFalse(self.confirm(r)['period_reconciled'])
 def test_source_change_between_reviews_blocks_second_confirmation(self):
  r=self.review();self.base.post_cash('1.00',self.day)
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_expiry_prevents_first_application(self):
  r=self.review()
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=16)):
   with self.assertRaises(AccountingError):self.confirm(r)
 def test_mandatory_declarations_and_two_confirmations(self):
  for value in [False,1,None]:
   with self.assertRaises(AccountingError):self.review(no_bank_movements=value)
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  with self.assertRaises(AccountingError):self.confirm(self.review(),confirmed=False)
 def test_idempotent_review_cannot_be_rebound(self):
  r=self.review();self.assertEqual(r,self.review())
  with self.assertRaises(AccountingError):self.review(period={**self.period,'evidence_digest':'d'*64})
 def test_account_and_company_isolation(self):
  with self.assertRaises((AccountingError,Account.DoesNotExist)):self.review(account_id=str(uuid.uuid4()))
  r=self.review();row=OutboxEvent.objects.get(pk=r['review_id']);row.payload['body']['company_id']=str(uuid.uuid4());row.save()
  with self.assertRaises(AccountingError):self.state(r)
 def test_atomic_confirmation_proof_failure(self):
  r=self.review();original=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.CONFIRMED:raise RuntimeError('Synthetic evidence failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.confirm(r)
  self.assertFalse(self.state(r)['historically_confirmed'])
 def test_erp_api_scope_and_contract_and_corporate_validator(self):
  call=self.case.call;payload={k:v for k,v in self.args.items() if k!='actor'}
  r=call('review_empty_bank_period','post',payload);self.assertEqual(r.status_code,200,r.data)
  c=call('confirm_empty_bank_period','post',{'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(c.status_code,200,c.data);self.assertIn('no-store',c['Cache-Control'])
  contract=runpy.run_path(str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND/app/services/empty_bank_period_contract.py'))['validate']
  ctx={'tenant_id':str(self.case.tenant.pk)};contract('review_empty_bank_period',r.data,payload,ctx);contract('confirm_empty_bank_period',c.data,{'review_id':r.data['review_id']},ctx)
  for change in [{'bank_verified':True},{'company_id':str(uuid.uuid4())},{'period_reconciled':False}]:
   with self.assertRaises(ValueError):contract('confirm_empty_bank_period',{**c.data,**change},{'review_id':r.data['review_id']},ctx)
if __name__=='__main__':unittest.main()
