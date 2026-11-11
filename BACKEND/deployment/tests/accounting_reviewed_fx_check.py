"""Reviewed foreign draft -> exact COP ledger; isolated ORM, declared rates only."""
import runpy,unittest,uuid,copy
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_posting_check.py')),run_name='reviewed_fx_fixture')
from apps.core_erp.accounting import reviewed_fx as fx
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry,AccountingAuditLog
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.fx.models import Currency
from apps.core_erp.outbox_models import OutboxEvent

class ReviewedFxTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['PostingTests']();self.case.setUp();self.company=self.case.tenant;self.actor=self.case.user
  for code in ['USD','EUR','COP']:Currency.objects.update_or_create(code=code,defaults={'name':'Synthetic '+code,'symbol':code,'is_active':True})
  self.entry=self.case.draft(currency='USD');LedgerEntry.plain_objects.filter(journal_entry=self.entry).update(currency='USD')
  self.day=self.entry.date.isoformat();self.terms={'base_currency':'USD','target_currency':'COP','rate':'4000.123456','source_reference':'synthetic-rate:declared','source_version':'1','observed_at':timezone.now().isoformat(),'valid_from':self.day,'valid_until':self.day,'evidence_digest':'a'*64}
  self.args={'actor':self.actor,'entry_id':str(self.entry.pk)}
 def review(self,**kw):return fx.review(self.company.pk,**{**self.args,'terms':self.terms,'expected_revision':0,'confirmed':True,**kw})
 def confirm(self,r,**kw):return fx.confirm(self.company.pk,**{**self.args,'review_id':r['review_id'],'confirmed':True,**kw})
 def test_exact_posting_uses_reviewed_rate_without_global_lookup(self):
  r=self.review();self.assertFalse(r['ledger_written']);self.assertEqual(r['preview']['valuation']['total_debit_cop'],'40001.23')
  with patch('apps.core_erp.fx.fx_engine.FXEngine.get_rate',side_effect=AssertionError('No global rate fallback')):a=self.confirm(r)
  self.assertEqual(a['exchange_rate'],'4000.123456');self.assertFalse(a['rate_independently_verified']);self.assertFalse(a['money_transferred']);self.assertEqual(a['total_debit_cop'],a['total_credit_cop'])
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
 def test_replay_is_single_post_and_restores_no_confirmation(self):
  r=self.review();a=self.confirm(r);b=self.confirm(r);self.assertEqual(a['journal_hash'],b['journal_hash']);self.assertTrue(b['replayed']);self.assertEqual(AccountingAuditLog.plain_objects.filter(reference_entry=self.entry,action='POST').count(),1)
  state=fx.state(self.company.pk,**self.args);self.assertFalse(state['confirmations_restored']);self.assertEqual(state['applied']['entry_id'],str(self.entry.pk))
 def test_second_confirmation_and_same_actor_required(self):
  r=self.review()
  with self.assertRaises(AccountingError):self.confirm(r,confirmed=False)
  with self.assertRaises(AccountingError):self.confirm(r,actor=fixture['fixture']['fixture']['F'].other)
 def test_generic_post_cannot_bypass_pending_review(self):
  self.review()
  with self.assertRaises(AccountingError):self.case.post(self.entry)
 def test_changed_draft_source_blocked(self):
  r=self.review();JournalEntry.plain_objects.filter(pk=self.entry.pk).update(description='Changed')
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_stale_revision_blocked(self):
  first=self.review();second=self.review(expected_revision=1)
  with self.assertRaises(AccountingError):self.confirm(first)
  self.assertTrue(self.confirm(second)['ledger_written'])
 def test_invalid_rate_direction_precision_and_float_rejected(self):
  for change in [{'rate':4000.0},{'rate':'0.000000'},{'rate':'4000.1234567'},{'target_currency':'USD'},{'source_reference':'https://example.invalid/?token=secret'},{'source_version':''},{'evidence_digest':'bad'}]:
   with self.assertRaises((AccountingError,ValueError,TypeError)):self.review(terms={**self.terms,**change})
 def test_future_observation_or_uncovered_economic_date_blocked(self):
  for change in [{'observed_at':'2099-01-01T00:00:00+00:00'},{'observed_at':'2026-01-01T00:00:00'},{'valid_from':'1900-01-01','valid_until':'1900-01-02'}]:
   with self.assertRaises((AccountingError,ValueError,TypeError)):self.review(terms={**self.terms,**change})
 def test_rounding_imbalance_is_not_plugged(self):
  entry=JournalService.create_entry(str(self.company.pk),self.entry.date,'Synthetic rounding',[{'account':self.case.a,'debit':'0.01'},{'account':self.case.a,'debit':'0.01'},{'account':self.case.b,'credit':'0.02'}],created_by=self.actor,currency='USD');LedgerEntry.plain_objects.filter(journal_entry=entry).update(currency='USD')
  with self.assertRaises(AccountingError):self.review(entry_id=str(entry.pk),terms={**self.terms,'rate':'1.500000'})
 def test_proof_failure_rolls_back_journal_rate_lines_and_audit(self):
  r=self.review();original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type')==fx.POSTED:raise RuntimeError('Synthetic proof write failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.confirm(r)
  entry=JournalEntry.plain_objects.get(pk=self.entry.pk);self.assertFalse(entry.is_posted);self.assertEqual(entry.financial_event_id,'reviewed-fx-pending:'+r['review_id']);self.assertEqual(entry.exchange_rate,Decimal('1'));self.assertFalse(AccountingAuditLog.plain_objects.filter(reference_entry=entry).exists())
 def test_tampered_review_or_missing_proof_cannot_replay(self):
  r=self.review();a=self.confirm(r);OutboxEvent.objects.filter(event_type=fx.POSTED,payload__entry_id=str(self.entry.pk))._raw_delete('default')
  with self.assertRaises(AccountingError):self.confirm(r)
  with self.assertRaises(AccountingError):self.case.post(self.entry)
 def test_inactive_currency_and_closed_period_blocked(self):
  r=self.review();Currency.objects.filter(code='USD').update(is_active=False)
  with self.assertRaises(AccountingError):self.confirm(r)
  Currency.objects.filter(code='USD').update(is_active=True);self.case.period.status='closed';self.case.period.save()
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_neutral_reversal_preserves_reviewed_rate_and_state_marks_history(self):
  r=self.review();self.confirm(r)
  with patch('apps.core_erp.fx.fx_engine.FXEngine.get_rate',side_effect=AssertionError('No new FX rate for reversal')):
   reverse=LedgerEngine.reverse_entry(self.entry.pk,tenant_id=self.company.pk,actor=self.actor)
  self.assertEqual(reverse.exchange_rate,Decimal(self.terms['rate']));self.assertTrue(fx.state(self.company.pk,**self.args)['applied']['original_reversed'])
 def test_missing_origin_proof_blocks_reversal(self):
  r=self.review();self.confirm(r);OutboxEvent.objects.filter(event_type=fx.POSTED,payload__entry_id=str(self.entry.pk))._raw_delete('default')
  with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(self.entry.pk,tenant_id=self.company.pk,actor=self.actor)
 def test_same_source_version_cannot_be_reused_with_changed_rate_or_evidence(self):
  self.review()
  for changes in [{'rate':'4100.000000'},{'evidence_digest':'b'*64}]:
   with self.assertRaises(AccountingError):self.review(expected_revision=1,terms={**self.terms,**changes})
  second=self.review(expected_revision=1,terms={**self.terms,'rate':'4100.000000','source_version':'2'});self.assertEqual(second['preview']['revision'],2)
 def test_missing_quote_version_blocks_posting(self):
  r=self.review();OutboxEvent.objects.filter(pk=fx.quote_record(self.company,self.terms).pk)._raw_delete('default')
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_currency_change_cannot_bypass_pending_fx_review(self):
  self.review();JournalEntry.plain_objects.filter(pk=self.entry.pk).update(currency='COP');LedgerEntry.plain_objects.filter(journal_entry=self.entry).update(currency='COP')
  with self.assertRaises(AccountingError):self.case.post(self.entry)
 def test_deleted_review_does_not_release_reserved_draft_for_generic_post(self):
  r=self.review();OutboxEvent.objects.filter(pk=r['review_id'])._raw_delete('default')
  with self.assertRaises(AccountingError):self.case.post(self.entry)
 def test_foreign_company_is_rejected(self):
  with self.assertRaises(AccountingError):fx.review(self.case.foreign.pk,**self.args,terms=self.terms,expected_revision=0,confirmed=True)
 def test_review_tampering_and_rate_conflict_rejected(self):
  r=self.review();JournalEntry.plain_objects.filter(pk=self.entry.pk).update(exchange_rate='4500.000000')
  with self.assertRaises(AccountingError):self.confirm(r)
  JournalEntry.plain_objects.filter(pk=self.entry.pk).update(exchange_rate='1.000000');row=OutboxEvent.objects.get(pk=r['review_id']);payload=copy.deepcopy(row.payload);payload['review']['quote']['rate']='4500.000000';OutboxEvent.objects.filter(pk=row.pk).update(payload=payload)
  with self.assertRaises(AccountingError):self.confirm(r)
if __name__=='__main__':unittest.main()
