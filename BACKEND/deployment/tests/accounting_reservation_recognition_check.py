"""Delivered-service attestation -> reviewed ledger accrual -> exact reversal."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta,date
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_fiscal_check.py')),run_name='recognition_fixture')
from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingAuditLog,AccountingEventReceipt
from apps.core_erp.accounting.delivery_models import AccountingDelivery,AccountingProjectionReceipt
from apps.core_erp.accounting.reports_engine import ReportsEngine
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from apps.domain_business.operativa.models import Reservation
from apps.turismo.models import VerifiedCompanyLink
from apps.domain_business.comercial.services import reservation_recognition as engine
from rest_framework.exceptions import APIException
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
create=fixture['fixture']['fixture']['fixture']['create']
for model in (Account,FiscalPeriod,LedgerEntry,AccountingEventReceipt,AccountingAuditLog,AccountingDelivery,AccountingProjectionReceipt):create(model)
class RecognitionTests(unittest.TestCase):
 def setUp(self):
  self.fiscal=fixture['FiscalReservationTests']();self.fiscal.setUp();self.case=self.fiscal.case
  self.day=timezone.localdate();Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(start_date=timezone.now()-timedelta(days=2),end_date=timezone.now()-timedelta(days=1))
  self.fiscal_review=self.fiscal.review()
  self.chart=ChartOfAccounts.plain_objects.create(tenant=self.case.tenant,name='Reviewed accrual chart')
  self.asset=Account.plain_objects.create(tenant=self.case.tenant,chart_of_accounts=self.chart,code='130505',name='Reviewed receivable',type='ASSET')
  self.revenue=Account.plain_objects.create(tenant=self.case.tenant,chart_of_accounts=self.chart,code='410505',name='Service revenue',type='REVENUE')
  self.tax=Account.plain_objects.create(tenant=self.case.tenant,chart_of_accounts=self.chart,code='240805',name='Reviewed tax liability',type='LIABILITY')
  self.period=FiscalPeriod.plain_objects.create(tenant=self.case.tenant,period_start=date(self.day.year,1,1),period_end=date(self.day.year,12,31),status='open')
  self.args={**self.fiscal.args,'fiscal_review_id':self.fiscal_review['review_id'],'entry_date':self.day.isoformat(),'account_mapping':{'receivable':str(self.asset.pk),'revenue':str(self.revenue.pk),'tax_liability':None},'service_evidence_digest':'c'*64,'policy_evidence_digest':'d'*64,'economic_fact':'SERVICE_DELIVERED','confirmed':True,'expected_revision':0}
 def review(self,**overrides):return engine.review_recognition(**{**self.args,**overrides})
 def post(self,review,**overrides):return engine.post_recognition(**{**self.fiscal.args,'review_id':review['review_id'],'confirmed':True,**overrides})
 def reversal_review(self):return engine.review_reversal(**self.fiscal.args,reason='Servicio anulado por revisión del titular',evidence_digest='e'*64,confirmed=True)
 def reverse(self,review):return engine.reverse_recognition(**self.fiscal.args,review_id=review['review_id'],confirmed=True)
 def test_review_does_not_post_money(self):
  review=self.review();self.assertFalse(review['ledger_written']);self.assertEqual(review['preview']['totals']['gross'],'100.00')
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.case.tenant).exists())
 def test_review_post_replay_real_balanced_journal_and_report(self):
  review=self.review();a=self.post(review);b=self.post(review)
  self.assertFalse(a['replayed']);self.assertTrue(b['replayed']);self.assertEqual(a['journal_id'],b['journal_id'])
  journal=JournalEntry.plain_objects.get(pk=a['journal_id']);self.assertTrue(journal.is_posted);self.assertEqual(journal.system_hash,journal.compute_hash())
  balance=ReportsEngine.get_trial_balance(self.case.tenant.pk,self.day);self.assertEqual(str(balance['total_debit']),'100.00');self.assertEqual(balance['total_credit'],balance['total_debit'])
  self.assertEqual(ReportsEngine.get_profitability(self.case.tenant.pk,self.day,self.day)['net_profit'],'100.00')
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.case.tenant).count(),1)
 def test_second_confirmation_required(self):
  with self.assertRaises(APIException):self.post(self.review(),confirmed=False)
 def test_future_service_is_not_recognized(self):
  Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(end_date=timezone.now()+timedelta(days=1))
  with self.assertRaises(APIException):self.review()
 def test_foreign_or_wrong_role_accounts_rejected(self):
  for mapping in [{'receivable':str(self.revenue.pk),'revenue':str(self.revenue.pk),'tax_liability':None},{'receivable':str(uuid.uuid4()),'revenue':str(self.revenue.pk),'tax_liability':None}]:
   with self.assertRaises(APIException):self.review(account_mapping=mapping)
 def test_changed_source_after_review_blocks_post(self):
  review=self.review();Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(total_price='101.00')
  with self.assertRaises(APIException):self.post(review)
 def test_closed_period_after_review_blocks_post(self):
  review=self.review();FiscalPeriod.plain_objects.filter(pk=self.period.pk).update(status='closed')
  with self.assertRaises(AccountingError):self.post(review)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.case.tenant).exists())
 def test_revoked_identity_blocks_post(self):
  review=self.review();VerifiedCompanyLink.objects.filter(provider=self.case.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.post(review)
 def test_review_digest_tampering_blocks_post(self):
  review=self.review();payload=OutboxEvent.objects.get(pk=review['review_id']).payload;payload['review']['entry_date']='2026-01-01'
  OutboxEvent.objects.filter(pk=review['review_id']).update(payload=payload)
  with self.assertRaises(APIException):self.post(review)
 def test_posted_origin_proof_failure_rolls_back_ledger(self):
  review=self.review();original=OutboxEvent.objects.create
  def create_event(**kwargs):
   if kwargs.get('event_type')==engine.POSTED:raise RuntimeError('Proof unavailable')
   return original(**kwargs)
  with patch.object(OutboxEvent.objects,'create',side_effect=create_event):
   with self.assertRaises(RuntimeError):self.post(review)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.case.tenant).exists());self.assertFalse(AccountingEventReceipt.objects.filter(tenant=self.case.tenant).exists())
 def test_exact_reversal_keeps_original_and_neutralizes_reports(self):
  posted=self.post(self.review());original=JournalEntry.plain_objects.get(pk=posted['journal_id']);old_hash=original.system_hash
  review=self.reversal_review();a=self.reverse(review);b=self.reverse(review)
  self.assertNotEqual(a['journal_id'],posted['journal_id']);self.assertTrue(b['replayed']);original.refresh_from_db();self.assertEqual(original.system_hash,old_hash)
  self.assertEqual(ReportsEngine.get_profitability(self.case.tenant.pk,self.day,self.day)['net_profit'],'0.00')
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.case.tenant.pk)['is_valid']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.case.tenant).count(),2)
 def test_cancelled_source_can_reverse_existing_accrual(self):
  self.post(self.review());Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(status='CANCELLED')
  self.assertTrue(self.reverse(self.reversal_review())['ledger_written'])
 def test_no_new_recognition_review_after_posting(self):
  self.post(self.review())
  with self.assertRaises(APIException):self.review(expected_revision=1)
 def test_tax_component_credits_liability_without_inventing_rate(self):
  self.fiscal.items[0].update(net='84.03',tax='15.97',tax_category='TAXABLE')
  fiscal=self.fiscal.review(expected_revision=1)
  review=self.review(fiscal_review_id=fiscal['review_id'],account_mapping={'receivable':str(self.asset.pk),'revenue':str(self.revenue.pk),'tax_liability':str(self.tax.pk)})
  posted=self.post(review);lines=LedgerEntry.plain_objects.filter(journal_entry_id=posted['journal_id'])
  self.assertEqual(lines.count(),3);self.assertEqual(str(lines.get(account=self.tax).credit_amount),'15.97')
  self.assertEqual(ReportsEngine.get_profitability(self.case.tenant.pk,self.day,self.day)['net_profit'],'84.03')
 def test_post_retry_after_reversal_does_not_rebook(self):
  review=self.review();self.post(review);self.reverse(self.reversal_review());result=self.post(review)
  self.assertTrue(result['reversed']);self.assertTrue(result['replayed']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.case.tenant).count(),2)
 def test_missing_origin_proof_is_not_reconstructed_on_replay(self):
  review=self.review();self.post(review);OutboxEvent.objects.filter(event_type=engine.POSTED,aggregate_root=str(self.case.reservation.pk)).delete()
  with self.assertRaises(APIException):self.post(review)
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.POSTED,aggregate_root=str(self.case.reservation.pk)).exists())
 def test_reversal_proof_failure_rolls_back_contrapartida(self):
  self.post(self.review());review=self.reversal_review();original=OutboxEvent.objects.create
  def create_event(**kwargs):
   if kwargs.get('event_type')==engine.REVERSED:raise RuntimeError('Proof failed')
   return original(**kwargs)
  with patch.object(OutboxEvent.objects,'create',side_effect=create_event):
   with self.assertRaises(RuntimeError):self.reverse(review)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.case.tenant).count(),1)
  self.assertTrue(self.reverse(review)['ledger_written'])
 def test_existing_advance_blocks_receivable_recognition(self):
  Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(deposit_paid='50.00')
  with self.assertRaises(APIException):self.review()
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.case.tenant).exists())
 def test_advance_registered_after_review_blocks_posting(self):
  review=self.review();Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(deposit_paid='1.00')
  with self.assertRaises(APIException):self.post(review)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.case.tenant).exists())
 def advance(self,amount='40.00'):
  Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(deposit_paid=amount)
  cash=Account.plain_objects.create(tenant=self.case.tenant,chart_of_accounts=self.chart,code='110505',name='Cash receipt',type='ASSET')
  liability=Account.plain_objects.create(tenant=self.case.tenant,chart_of_accounts=self.chart,code='280505',name='Customer advance',type='LIABILITY')
  journal=LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=self.day,description='Previously posted customer receipt',lines_data=[{'account':cash,'debit':amount},{'account':liability,'credit':amount}],actor=self.case.actor,idempotency_key='advance:'+str(uuid.uuid4()),period_id=self.period.pk)
  return journal,liability,{'journal_id':str(journal.pk),'liability_account_id':str(liability.pk),'evidence_digest':'f'*64}
 def test_partial_advance_reduces_receivable_without_second_cash_receipt(self):
  original,liability,allocation=self.advance();review=self.review(advance_allocation=allocation)
  self.assertEqual(review['preview']['receivable_amount'],'60.00')
  posted=self.post(review);self.assertTrue(self.post(review)['replayed'])
  lines=LedgerEntry.plain_objects.filter(journal_entry_id=posted['journal_id'])
  self.assertEqual(str(lines.get(account=self.asset).debit_amount),'60.00')
  self.assertEqual(str(lines.get(account=liability).debit_amount),'40.00')
  self.assertEqual(lines.count(),3);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.case.tenant).count(),2)
  self.assertEqual(ReportsEngine.get_profitability(self.case.tenant.pk,self.day,self.day)['net_profit'],'100.00')
  self.reverse(self.reversal_review());original.refresh_from_db();self.assertTrue(original.is_posted)
  self.assertEqual(ReportsEngine.get_profitability(self.case.tenant.pk,self.day,self.day)['net_profit'],'0.00')
 def test_full_advance_creates_no_zero_receivable_line(self):
  _,liability,allocation=self.advance('100.00');posted=self.post(self.review(advance_allocation=allocation))
  lines=LedgerEntry.plain_objects.filter(journal_entry_id=posted['journal_id'])
  self.assertFalse(lines.filter(account=self.asset).exists());self.assertEqual(lines.count(),2)
 def test_changed_deposit_after_review_rejects_application(self):
  _,_,allocation=self.advance();review=self.review(advance_allocation=allocation)
  Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(deposit_paid='41.00')
  with self.assertRaises(APIException):self.post(review)
 def test_reversed_receipt_cannot_be_applied(self):
  journal,_,allocation=self.advance();review=self.review(advance_allocation=allocation)
  LedgerEngine.reverse_entry(journal.pk,'Receipt reversed after review',tenant_id=self.case.tenant.pk,actor=self.case.actor)
  with self.assertRaises(APIException):self.post(review)
 def test_unrelated_or_wrong_liability_receipt_rejected(self):
  _,_,allocation=self.advance();allocation['liability_account_id']=str(self.tax.pk)
  with self.assertRaises(APIException):self.review(advance_allocation=allocation)
 def test_allocation_claim_failure_rolls_back_only_recognition(self):
  _,_,allocation=self.advance();review=self.review(advance_allocation=allocation);original=OutboxEvent.objects.create
  def create_event(**kwargs):
   if kwargs.get('event_type')==engine.ADVANCE_APPLIED:raise RuntimeError('Claim unavailable')
   return original(**kwargs)
  with patch.object(OutboxEvent.objects,'create',side_effect=create_event):
   with self.assertRaises(RuntimeError):self.post(review)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.case.tenant).count(),1)
  self.assertFalse(AccountingEventReceipt.objects.filter(tenant=self.case.tenant,event_id=engine.key(self.case.reservation)).exists())
  self.assertTrue(self.post(review)['ledger_written'])
 def test_receipt_cannot_be_reused_for_another_reservation(self):
  _,_,allocation=self.advance();self.post(self.review(advance_allocation=allocation))
  original=Reservation.plain_objects.get(pk=self.case.reservation.pk)
  other=Reservation.plain_objects.create(tenant=self.case.tenant,customer_id=original.customer_id,content_type_id=original.content_type_id,object_id=original.object_id,start_date=original.start_date,end_date=original.end_date,status='CONFIRMED',total_price='100.00',deposit_paid='40.00')
  fiscal=self.fiscal.review(reservation_id=other.pk)
  with self.assertRaises(APIException):self.review(reservation_id=other.pk,fiscal_review_id=fiscal['review_id'],advance_allocation=allocation)
 def test_missing_advance_claim_on_replay_is_not_reconstructed(self):
  journal,_,allocation=self.advance();review=self.review(advance_allocation=allocation);self.post(review)
  OutboxEvent.objects.filter(pk=engine.advance_claim_id(journal.pk)).delete()
  with self.assertRaises(APIException):self.post(review)
 def test_advance_and_tax_are_applied_as_separate_liabilities(self):
  _,liability,allocation=self.advance();self.fiscal.items[0].update(net='84.03',tax='15.97',tax_category='TAXABLE')
  fiscal=self.fiscal.review(expected_revision=1)
  review=self.review(fiscal_review_id=fiscal['review_id'],advance_allocation=allocation,account_mapping={'receivable':str(self.asset.pk),'revenue':str(self.revenue.pk),'tax_liability':str(self.tax.pk)})
  posted=self.post(review);lines=LedgerEntry.plain_objects.filter(journal_entry_id=posted['journal_id'])
  self.assertEqual(lines.count(),4);self.assertEqual(str(lines.get(account=self.tax).credit_amount),'15.97')
  self.assertEqual(str(lines.get(account=liability).debit_amount),'40.00')
  self.assertEqual(str(lines.get(account=self.asset).debit_amount),'60.00')
 def test_all_shared_ledger_reversals_block_an_actively_applied_receipt(self):
  receipt,_,allocation=self.advance();self.post(self.review(advance_allocation=allocation))
  with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(receipt.pk,'Reject reversal of applied receipt',tenant_id=str(self.case.tenant.pk).upper(),actor=self.case.actor)
  self.reverse(self.reversal_review())
  reversed_receipt=LedgerEngine.reverse_entry(receipt.pk,'Receipt released after recognition reversal',tenant_id=self.case.tenant.pk,actor=self.case.actor)
  self.assertEqual(reversed_receipt.reversed_entry_id,receipt.pk)
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.case.tenant.pk)['is_valid'])
 def test_recover_review_and_post_without_restoring_confirmations(self):
  review=self.review();state=engine.recognition_status(**self.fiscal.args)
  self.assertEqual(state['review']['review_id'],review['review_id']);self.assertIsNone(state['posting']);self.assertFalse(state['confirmations_restored'])
  posted=self.post(review);state=engine.recognition_status(**self.fiscal.args);self.assertEqual(state['posting']['journal_id'],posted['journal_id']);self.assertEqual(len(state['history']),1)
  self.reverse(self.reversal_review());self.assertTrue(engine.recognition_status(**self.fiscal.args)['posting']['reversed'])
 def test_status_does_not_reconstruct_missing_origin_evidence(self):
  self.post(self.review());OutboxEvent.objects.filter(event_type=engine.POSTED,aggregate_root=str(self.case.reservation.pk)).delete()
  with self.assertRaises(APIException):engine.recognition_status(**self.fiscal.args)
 def test_history_paging_retains_all_review_versions(self):
  for revision in range(25):self.review(expected_revision=revision)
  first=engine.recognition_status(**self.fiscal.args);second=engine.recognition_status(**self.fiscal.args,before_revision=first['next_before_revision'])
  self.assertEqual([r['revision'] for r in first['history']+second['history']],list(range(25,0,-1)))
 def test_real_view_review_and_post(self):
  def call(action,body):
   request=APIRequestFactory().post('/fixture/?provider_id='+str(self.case.provider.pk),body,format='json');force_authenticate(request,user=self.case.actor)
   return PlanCuentaViewSet.as_view({'post':action})(request)
  body={k:v for k,v in self.args.items() if k not in {'actor','provider_id'}};body['reservation_id']=str(body['reservation_id'])
  result=call('review_reservation_recognition',body);self.assertEqual(result.status_code,200,result.data)
  posted=call('post_reservation_recognition',{'reservation_id':body['reservation_id'],'review_id':result.data['review_id'],'confirmed':True});self.assertEqual(posted.status_code,200,posted.data);self.assertTrue(posted.data['ledger_written'])
if __name__=='__main__':unittest.main()
