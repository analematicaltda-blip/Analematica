"""Reviewed first-book opening, preserved source and real ledger/report outcome."""
import runpy,unittest
from pathlib import Path
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='opening_fixture')
from apps.core_erp.accounting import opening_balances as engine
from apps.core_erp.accounting.models import Account,FiscalPeriod,JournalEntry,AccountingEventReceipt
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.reports_engine import ReportsEngine
from apps.core_erp.accounting.reconciliation import inspect_company
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class OpeningTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['RecognitionTests']();self.case.setUp();self.company=self.case.case.tenant;self.actor=self.case.case.actor
  self.equity=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='310505',name='Reviewed initial equity',type='EQUITY',initial_balance='100.00')
  Account.plain_objects.filter(pk=self.case.asset.pk).update(initial_balance='100.00')
 def review(self,**extra):return engine.review_opening(self.company.pk,**{'actor':self.actor,'entry_date':timezone.localdate().isoformat(),'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True,**extra})
 def apply(self,review,**extra):return engine.apply_opening(self.company.pk,**{'actor':self.actor,'review_id':review['review_id'],'confirmed':True,**extra})
 def test_preview_preserves_sources_and_does_not_post(self):
  preview=self.review();self.assertFalse(preview['ledger_written']);self.assertEqual(preview['preview']['total_debit'],'100.00');self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_opening_unblocks_reports_without_zeroing_original_balances(self):
  with self.assertRaises(AccountingError):ReportsEngine.get_trial_balance(self.company.pk,self.case.day)
  review=self.review();posted=self.apply(review);self.assertTrue(self.apply(review)['replayed'])
  r=ReportsEngine.get_trial_balance(self.company.pk,self.case.day);self.assertEqual(str(r['total_debit']),'100.00');self.assertEqual(r['total_credit'],r['total_debit'])
  self.case.asset.refresh_from_db();self.equity.refresh_from_db();self.assertEqual(str(self.case.asset.initial_balance),'100.00');self.assertEqual(str(self.equity.initial_balance),'100.00');self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1)
  self.assertEqual(ReportsEngine.get_profitability(self.company.pk,self.case.day,self.case.day)['net_profit'],'0.00');self.assertEqual(inspect_company(self.company.pk)['opening_reconciliation']['status'],'RECONCILED_PRESERVED_REFERENCE')
 def test_second_confirmation_and_unbalanced_sources_rejected(self):
  with self.assertRaises(AccountingError):self.apply(self.review(),confirmed=False)
  Account.plain_objects.filter(pk=self.equity.pk).update(initial_balance='99.00')
  with self.assertRaises(AccountingError):self.review(expected_revision=1)
 def test_changed_source_rejected_before_post_and_after_post(self):
  review=self.review();Account.plain_objects.filter(pk=self.equity.pk).update(initial_balance='101.00')
  with self.assertRaises(AccountingError):self.apply(review)
  Account.plain_objects.filter(pk=self.equity.pk).update(initial_balance='100.00');self.apply(review)
  Account.plain_objects.filter(tenant=self.company).update(initial_balance='0.00')
  with self.assertRaises(AccountingError):ReportsEngine.get_trial_balance(self.company.pk,self.case.day)
 def test_no_implicit_fx_or_opening_over_existing_books(self):
  self.company.currency='USD';self.company.save(update_fields=['currency'])
  with self.assertRaises(AccountingError):self.review()
  self.company.currency='COP';self.company.save(update_fields=['currency'])
  self.case.post(self.case.review())
  with self.assertRaises(AccountingError):self.review()
 def test_origin_proof_failure_rolls_back_all_posting(self):
  review=self.review();original=OutboxEvent.objects.create
  def create(**kwargs):
   if kwargs.get('event_type')==engine.APPLIED:raise RuntimeError('Proof unavailable')
   return original(**kwargs)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.apply(review)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists());self.assertFalse(AccountingEventReceipt.objects.filter(tenant=self.company).exists())
 def test_reversal_preserves_sources_and_neutralizes_opening(self):
  posted=self.apply(self.review());LedgerEngine.reverse_entry(posted['journal_id'],'Reviewed opening correction',tenant_id=self.company.pk,actor=self.actor)
  r=ReportsEngine.get_trial_balance(self.company.pk,self.case.day);self.assertEqual(r['total_debit'],r['total_credit']);self.assertEqual(ReportsEngine.get_balance_sheet(self.company.pk,self.case.day)['assets'],0)
  self.assertTrue(engine.inspect_opening(self.company.pk)['reversed']);self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
 def test_retired_source_account_preserves_historical_report_and_replay(self):
  review=self.review();posted=self.apply(review);Account.plain_objects.filter(pk=self.case.asset.pk).update(is_active=False)
  self.assertEqual(str(ReportsEngine.get_trial_balance(str(self.company.pk).upper(),self.case.day)['total_debit']),'100.00');self.assertTrue(self.apply(review)['replayed'])
 def old_opening(self):
  return LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.case.day,description='Previously recorded reviewed opening',lines_data=[{'account':self.case.asset,'debit':'100.00'},{'account':self.equity,'credit':'100.00'}],actor=self.actor,idempotency_key='previous-opening:'+str(self.company.pk),period_id=self.case.period.pk)
 def test_link_existing_opening_in_closed_period_without_duplicate_or_rehash(self):
  original=self.old_opening();old_hash=original.system_hash;FiscalPeriod.plain_objects.filter(pk=self.case.period.pk).update(status='closed')
  review=self.review(existing_journal_id=str(original.pk));result=self.apply(review);self.assertTrue(result['linked_existing']);self.assertFalse(result['ledger_written']);self.assertTrue(self.apply(review)['replayed'])
  original.refresh_from_db();self.assertEqual(original.system_hash,old_hash);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1);self.assertEqual(AccountingEventReceipt.objects.filter(tenant=self.company).count(),1);self.assertEqual(str(ReportsEngine.get_trial_balance(self.company.pk,self.case.day)['total_debit']),'100.00')
 def test_wrong_existing_journal_cannot_reconcile_source(self):
  existing=self.case.post(self.case.review())
  with self.assertRaises(AccountingError):self.review(existing_journal_id=str(existing['journal_id']))
 def test_existing_opening_reversed_after_review_cannot_be_linked(self):
  original=self.old_opening();review=self.review(existing_journal_id=str(original.pk));LedgerEngine.reverse_entry(original.pk,'Correction before link confirmation',tenant_id=self.company.pk,actor=self.actor)
  with self.assertRaises(AccountingError):self.apply(review)
 def test_real_api_review_and_post(self):
  def call(action,data):
   request=APIRequestFactory().post('/fixture/?provider_id='+str(self.case.case.provider.pk),data,format='json');force_authenticate(request,user=self.actor)
   return PlanCuentaViewSet.as_view({'post':action})(request)
  r=call('review_opening',{'entry_date':self.case.day.isoformat(),'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True});self.assertEqual(r.status_code,200,r.data)
  posted=call('apply_opening',{'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(posted.status_code,200,posted.data)
if __name__=='__main__':unittest.main()
