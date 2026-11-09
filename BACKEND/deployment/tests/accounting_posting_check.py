"""Posting on isolated real ledger tables. No banks, tax authorities or external bus."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_foundation_check.py')),run_name='posting_fixture')
from apps.core_erp.accounting.models import AccountingEventReceipt,AccountingAuditLog,JournalEntry,LedgerEntry
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.fx.models import Currency,FXRateTable
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.exceptions import AccountingError,DuplicateReversalError
from apps.core_erp.accounting.reports_engine import ReportsEngine
from apps.core_erp.tenancy.utils import set_current_tenant_id,clear_current_tenant_id
for model in (AccountingEventReceipt,AccountingAuditLog,OutboxEvent,Currency,FXRateTable):fixture['fixture']['fixture']['create'](model)

class PostingTests(fixture['AccountingFoundation']):
 def setUp(self):
  super().setUp();self.user=fixture['fixture']['F'].owner
 def draft(self,**extra):
  return JournalService.create_entry(str(self.tenant.pk),timezone.localdate(),'Synthetic reviewed journal',self.lines(),created_by=self.user,**extra)
 def post(self,entry):return LedgerEngine.post_entry(entry.pk,tenant_id=self.tenant.pk,actor=self.user)
 def test_post_and_replay_have_one_audit_outbox_no_bus(self):
  entry=self.draft()
  with patch('apps.core_erp.event_bus.EventBus.emit',side_effect=AssertionError('External bus must not run')):
   posted=self.post(entry);again=self.post(entry)
  self.assertEqual(posted.compute_hash(),posted.system_hash);self.assertEqual(posted.pk,again.pk);self.assertEqual(posted.hash_version,'v2');self.assertIsNone(posted.immutable_signature)
  self.assertEqual(AccountingAuditLog.plain_objects.filter(reference_entry=posted,action='POST').count(),1)
  self.assertEqual(OutboxEvent.objects.filter(pk=posted.pk).count(),1)
  self.assertEqual(OutboxEvent.objects.get(pk=posted.pk).payload['total_debit'],'10.00')
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.tenant.pk)['is_valid'])
 def test_hash_detects_equal_total_account_or_currency_tampering(self):
  posted=self.post(self.draft());line=LedgerEntry.plain_objects.filter(journal_entry=posted).first()
  LedgerEntry.plain_objects.filter(pk=line.pk).update(description='Tampered unchanged balance')
  self.assertFalse(LedgerEngine.validate_ledger_integrity(self.tenant.pk)['is_valid'])
  with self.assertRaises(AccountingError):self.post(posted)
 def test_audit_and_outbox_failure_roll_back_post_and_lines(self):
  for manager in (AccountingAuditLog.objects,OutboxEvent.objects):
   entry=self.draft()
   with patch.object(manager,'create',side_effect=RuntimeError('Synthetic write failure')):
    with self.assertRaises(RuntimeError):self.post(entry)
   self.assertFalse(JournalEntry.plain_objects.get(pk=entry.pk).is_posted)
   self.assertFalse(OutboxEvent.objects.filter(pk=entry.pk).exists())
 def test_inactive_actor_wrong_scope_and_closed_period_rejected(self):
  entry=self.draft()
  with self.assertRaises(JournalEntry.DoesNotExist):LedgerEngine.post_entry(entry.pk,tenant_id=self.foreign.pk,actor=self.user)
  with self.assertRaises(AccountingError):LedgerEngine.post_entry(entry.pk,tenant_id=self.tenant.pk)
  self.period.status='closed';self.period.save()
  with self.assertRaises(AccountingError):self.post(entry)
 def test_missing_or_future_fx_rejected_without_unit_fallback(self):
  entry=self.draft(currency='USD')
  LedgerEntry.plain_objects.filter(journal_entry=entry).update(currency='USD')
  with self.assertRaises(AccountingError):self.post(entry)
  usd,_=Currency.objects.get_or_create(code='USD',defaults={'name':'US dollar','symbol':'$'})
  cop,_=Currency.objects.get_or_create(code='COP',defaults={'name':'Colombian peso','symbol':'$'})
  rate=FXRateTable.objects.create(base_currency=usd,target_currency=cop,rate=Decimal('4000'),effective_from=timezone.now()+timedelta(days=1),version=uuid.uuid4().int%1000000)
  with self.assertRaises(AccountingError):self.post(entry)
  rate.effective_from=timezone.now()-timedelta(days=1);rate.save()
  posted=self.post(entry);self.assertEqual(posted.exchange_rate,Decimal('4000'))
  self.assertEqual(LedgerEntry.plain_objects.filter(journal_entry=posted).first().amount_base,Decimal('40000'))
 def test_manual_idempotency_and_changed_contract(self):
  args=dict(tenant_id=self.tenant.pk,entry_date=timezone.localdate(),description='Manual fixture',lines_data=self.lines(),actor=self.user,period_id=self.period.pk,idempotency_key='manual-fixture')
  a=LedgerEngine.post_lines(**args);b=LedgerEngine.post_lines(**args);self.assertEqual(a.pk,b.pk)
  with self.assertRaises(AccountingError):LedgerEngine.post_lines(**{**args,'description':'Changed'})
  self.assertEqual(AccountingEventReceipt.objects.filter(tenant=self.tenant).count(),1)
 def test_event_unknown_rule_rejects_and_retry_is_payload_bound(self):
  payload={'tenant_id':str(self.tenant.pk),'financial_event_id':'fixture-payment','amount':'10.00','reference':'fixture'}
  self.a.code='111005';self.a.save();self.b.code='130505';self.b.save()
  before=JournalEntry.plain_objects.count()
  with self.assertRaises(AccountingError):LedgerEngine.post_event('UNKNOWN',payload,actor=self.user)
  self.assertEqual(JournalEntry.plain_objects.count(),before)
  a=LedgerEngine.post_event('PAYMENT_RECEIVED',payload,actor=self.user)
  b=LedgerEngine.post_event('PAYMENT_RECEIVED',payload,actor=self.user);self.assertEqual(a.pk,b.pk)
  with self.assertRaises(AccountingError):LedgerEngine.post_event('PAYMENT_RECEIVED',{**payload,'amount':'11.00'},actor=self.user)
 def test_reversal_is_new_entry_in_current_period_and_not_repeatable(self):
  original=self.post(self.draft());hashed=original.system_hash
  reversal=LedgerEngine.reverse_entry(original.pk,'Reviewed reason',tenant_id=self.tenant.pk,actor=self.user)
  self.assertNotEqual(reversal.pk,original.pk);self.assertTrue(reversal.is_posted)
  self.assertEqual(JournalEntry.plain_objects.get(pk=original.pk).system_hash,hashed)
  with self.assertRaises(DuplicateReversalError):LedgerEngine.reverse_entry(original.pk,tenant_id=self.tenant.pk,actor=self.user)
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.tenant.pk)['is_valid'])
 def test_legacy_hashes_remain_unchanged_when_v2_is_appended(self):
  entry=self.draft();entry.previous_hash='GENESIS_SARITA_2026'
  old=LedgerEngine.calculate_hash(entry,entry.previous_hash)
  JournalEntry.plain_objects.filter(pk=entry.pk).update(is_posted=True,posted_at=timezone.now(),previous_hash=entry.previous_hash,system_hash=old)
  new=self.post(self.draft())
  self.assertEqual(new.previous_hash,old)
  historical=JournalEntry.plain_objects.get(pk=entry.pk)
  self.assertEqual(historical.system_hash,old);self.assertEqual(historical.hash_version,'legacy')
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.tenant.pk)['is_valid'])

 def test_reports_use_explicit_scope_posted_base_values_and_constant_queries(self):
  from django.db import connection
  from django.test.utils import CaptureQueriesContext
  self.post(self.draft());self.draft() # draft excluded
  with CaptureQueriesContext(connection) as queries:
   report=ReportsEngine.get_trial_balance(self.tenant.pk,timezone.localdate())
  self.assertLessEqual(len(queries),9);self.assertEqual(report['total_debit'],Decimal('10'));self.assertEqual(report['snapshot']['consistency'],'company_lock_shared_with_posting')
  self.assertEqual(report['total_credit'],Decimal('10'))
  self.assertEqual(ReportsEngine.get_trial_balance(self.foreign.pk,timezone.localdate())['lines'],[])
  self.assertEqual(ReportsEngine.get_balance_sheet(self.tenant.pk,timezone.localdate())['check'],Decimal('0'))
  with self.assertRaises(AccountingError):ReportsEngine.get_cash_flow(self.tenant.pk,timezone.localdate(),timezone.localdate())

 def test_integrity_validator_uses_v2_and_explicit_tenant_context(self):
  from apps.core_erp.integrity.accounting_validator import AccountingValidator
  posted=self.post(self.draft())
  with self.assertRaises(AccountingError):AccountingValidator()._verify_hash_chain()
  token=set_current_tenant_id(self.tenant.pk)
  try:
   result=AccountingValidator()._verify_hash_chain();self.assertTrue(result['success']);self.assertEqual(result['blocks_verified'],1)
  finally:clear_current_tenant_id(token)
 def test_future_economic_date_remains_draft(self):
  entry=JournalService.create_entry(str(self.tenant.pk),timezone.localdate()+timedelta(days=1),'Future draft',self.lines(),created_by=self.user)
  with self.assertRaises(AccountingError):self.post(entry)
  self.assertFalse(JournalEntry.plain_objects.get(pk=entry.pk).is_posted)

 def test_unreconciled_initial_balances_do_not_produce_false_complete_reports(self):
  self.post(self.draft());Account=type(self.a)
  Account.plain_objects.filter(pk=self.a.pk).update(initial_balance=Decimal('1000.00'))
  with self.assertRaises(AccountingError):ReportsEngine.get_trial_balance(self.tenant.pk,timezone.localdate())
  with self.assertRaises(AccountingError):LedgerEngine.validate_ledger_integrity(None)

 def test_cannot_reassign_posted_line_or_directly_post_model(self):
  entry=self.post(self.draft());line=LedgerEntry.plain_objects.filter(journal_entry=entry).first();other=self.draft()
  line.journal_entry=other
  with self.assertRaises(PermissionError):line.save()
  other.is_posted=True
  with self.assertRaises(PermissionError):other.save()

 def foreign_original(self):
  usd,_=Currency.objects.get_or_create(code='USD',defaults={'name':'US dollar','symbol':'$'})
  cop,_=Currency.objects.get_or_create(code='COP',defaults={'name':'Colombian peso','symbol':'$'})
  rate=FXRateTable.objects.create(base_currency=usd,target_currency=cop,rate=Decimal('4000'),effective_from=timezone.now()-timedelta(microseconds=1),version=uuid.uuid4().int%1000000)
  entry=self.draft(currency='USD');LedgerEntry.plain_objects.filter(journal_entry=entry).update(currency='USD')
  return self.post(entry),rate
 def test_z_foreign_reversal_keeps_original_rate_and_base_values(self):
  from apps.core_erp.accounting.reports_engine import ReportsEngine
  original,rate=self.foreign_original();before=original.system_hash
  FXRateTable.objects.create(base_currency=rate.base_currency,target_currency=rate.target_currency,rate=Decimal('4500'),effective_from=timezone.now(),version=uuid.uuid4().int%1000000)
  with patch('apps.core_erp.fx.fx_engine.FXEngine.get_rate',side_effect=AssertionError('Neutral reversal must not request a new quote')):
   reversal=LedgerEngine.reverse_entry(original.pk,'Neutral correction',tenant_id=self.tenant.pk,actor=self.user)
  self.assertEqual(reversal.exchange_rate,Decimal('4000'));self.assertEqual(reversal.currency,'USD')
  self.assertEqual(JournalEntry.plain_objects.get(pk=original.pk).system_hash,before)
  self.assertEqual(set(LedgerEntry.plain_objects.filter(journal_entry=reversal).values_list('amount_base',flat=True)),{Decimal('40000')})
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.tenant.pk)['is_valid'])
  self.assertTrue(all(row['balance']==0 for row in ReportsEngine.get_trial_balance(self.tenant.pk,timezone.localdate())['lines']))
  with self.assertRaises(DuplicateReversalError):LedgerEngine.reverse_entry(original.pk,'Duplicate',tenant_id=self.tenant.pk,actor=self.user)
 def test_z_foreign_reversal_rejects_altered_lines(self):
  original,_=self.foreign_original()
  draft=JournalService.create_entry(str(self.tenant.pk),timezone.localdate(),'Wrong reversal',
   [{'account':self.b,'debit':'9.00'},{'account':self.a,'credit':'9.00'}],created_by=self.user,currency='USD',base_currency='COP',exchange_rate=Decimal('4000'))
  draft.is_reversal=True;draft.reversed_entry_id=original.pk;draft.event_type='REVERSAL';draft.save()
  with self.assertRaises(AccountingError):self.post(draft)
  # An invalid abandoned draft is not silently deleted by the engine.
  self.assertFalse(JournalEntry.plain_objects.get(pk=draft.pk).is_posted)
 def test_z_foreign_reversal_closed_current_period_rolls_back(self):
  original,_=self.foreign_original();before=JournalEntry.plain_objects.count()
  self.period.status='closed';self.period.save()
  with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(original.pk,'Closed',tenant_id=self.tenant.pk,actor=self.user)
  self.assertEqual(JournalEntry.plain_objects.count(),before)

if __name__=='__main__':unittest.main()
