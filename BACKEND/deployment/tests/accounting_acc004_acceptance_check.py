"""ACC004 supported state writes, current-period reversals and lock ordering."""
import runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from datetime import timedelta
f=runpy.run_path(str(Path(__file__).with_name('accounting_posting_check.py')),run_name='acc004_fixture')
from django.db import connection,transaction
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from apps.core_erp.accounting.models import Account,FiscalPeriod,JournalEntry,LedgerEntry
from apps.core_erp.accounting.exceptions import AccountingError,DuplicateReversalError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.delivery_models import AccountingDailyBalance
if AccountingDailyBalance._meta.db_table not in connection.introspection.table_names():
 with connection.schema_editor() as editor:editor.create_model(AccountingDailyBalance)
class ACC004Acceptance(unittest.TestCase):
 def setUp(self):self.c=f['PostingTests']();self.c.setUp()
 def test_period_and_account_writes_take_company_lock_before_row_write(self):
  for obj in [self.c.a,self.c.period]:
   with CaptureQueriesContext(connection) as queries:obj.save()
   sql=[q['sql'].lower() for q in queries];company=next(i for i,s in enumerate(sql) if 'core_erp_tenant' in s and s.startswith('select'));write=next(i for i,s in enumerate(sql) if s.startswith('update'));self.assertLess(company,write)
  for obj in [Account.plain_objects.create(tenant=self.c.tenant,chart_of_accounts=self.c.chart,code='1107',name='Unused account',type='ASSET'),FiscalPeriod.plain_objects.create(tenant=self.c.tenant,period_start=timezone.localdate()+timedelta(days=400),period_end=timezone.localdate()+timedelta(days=401),status='open')]:
   with CaptureQueriesContext(connection) as queries:obj.delete()
   sql=[q['sql'].lower() for q in queries];self.assertLess(next(i for i,s in enumerate(sql) if 'core_erp_tenant' in s and s.startswith('select')),next(i for i,s in enumerate(sql) if s.startswith('delete')))
 def test_bulk_state_writes_lock_company_before_update(self):
  for query in [Account.plain_objects.filter(pk=self.c.a.pk),FiscalPeriod.plain_objects.filter(pk=self.c.period.pk)]:
   with CaptureQueriesContext(connection) as queries:
    query.update(**({'is_active':True} if query.model is Account else {'status':'open'}))
   sql=[q['sql'].lower() for q in queries];self.assertLess(next(i for i,s in enumerate(sql) if 'core_erp_tenant' in s and s.startswith('select')),next(i for i,s in enumerate(sql) if s.startswith('update')))
 def test_bulk_writes_cannot_move_company(self):
  for query in [Account.plain_objects.filter(pk=self.c.a.pk),FiscalPeriod.plain_objects.filter(pk=self.c.period.pk)]:
   with self.assertRaises(AccountingError):query.update(tenant=self.c.foreign)
 def test_stale_period_cannot_reopen_a_concurrent_close(self):
  stale=FiscalPeriod.plain_objects.get(pk=self.c.period.pk);fresh=FiscalPeriod.plain_objects.get(pk=self.c.period.pk);fresh.status='closed';fresh.save()
  with self.assertRaises(AccountingError):stale.save()
  self.assertEqual(FiscalPeriod.plain_objects.get(pk=stale.pk).status,'closed')
  stale.refresh_from_db();stale.status='open';stale.save();self.assertEqual(FiscalPeriod.plain_objects.get(pk=stale.pk).status,'open')
 def test_stale_account_cannot_undo_deactivation(self):
  stale=Account.plain_objects.get(pk=self.c.a.pk);fresh=Account.plain_objects.get(pk=self.c.a.pk);fresh.is_active=False;fresh.save()
  with self.assertRaises(AccountingError):stale.save()
  self.assertFalse(Account.plain_objects.get(pk=stale.pk).is_active)
 def test_equivalent_company_uuid_text_is_not_reassignment(self):
  for obj in [self.c.a,self.c.period]:obj.tenant_id=str(obj.tenant_id);obj.save()
 def test_idempotent_same_state_write_is_allowed(self):
  stale=FiscalPeriod.plain_objects.get(pk=self.c.period.pk);self.c.period.status='closed';self.c.period.save();stale.status='closed';stale.save();self.assertEqual(FiscalPeriod.plain_objects.get(pk=stale.pk).status,'closed')
 def test_account_and_period_cannot_move_between_companies(self):
  for obj in [self.c.a,self.c.period]:
   obj.tenant=self.c.foreign
   with self.assertRaises(AccountingError):obj.save()
 def test_close_blocks_post_and_reversal_without_orphan_draft(self):
  original=self.c.post(self.c.draft());pending=self.c.draft();count=JournalEntry.plain_objects.count();self.c.period.status='closed';self.c.period.save()
  with self.assertRaises(AccountingError):self.c.post(pending)
  with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(original.pk,tenant_id=self.c.tenant.pk,actor=self.c.user)
  self.assertEqual(JournalEntry.plain_objects.count(),count);self.assertEqual(JournalEntry.plain_objects.get(pk=original.pk).system_hash,original.system_hash)
 def test_historical_original_reverses_in_current_period_preserving_original(self):
  today=timezone.localdate();self.c.period.period_start=today-timedelta(days=1);self.c.period.period_end=today-timedelta(days=1);self.c.period.save()
  from apps.core_erp.accounting.journal_service import JournalService
  original=JournalService.create_entry(str(self.c.tenant.pk),today-timedelta(days=1),'Historical fixture',self.c.lines(),created_by=self.c.user);original=self.c.post(original);self.c.period.status='closed';self.c.period.save();current=FiscalPeriod.plain_objects.create(tenant=self.c.tenant,period_start=today,period_end=today,status='open')
  reversal=LedgerEngine.reverse_entry(original.pk,tenant_id=self.c.tenant.pk,actor=self.c.user);self.assertEqual(reversal.period_id,current.pk);self.assertEqual(reversal.date,today);self.assertEqual(JournalEntry.plain_objects.get(pk=original.pk).system_hash,original.system_hash);self.assertTrue(LedgerEngine.validate_ledger_integrity(self.c.tenant.pk)['is_valid'])
  with self.assertRaises(DuplicateReversalError):LedgerEngine.reverse_entry(original.pk,tenant_id=self.c.tenant.pk,actor=self.c.user)
 def test_posted_account_identity_cannot_change_hash_through_model_save(self):
  entry=self.c.post(self.c.draft());account=Account.plain_objects.get(pk=self.c.a.pk)
  for field,value in [('code','NEW-CODE'),('type','LIABILITY'),('chart_of_accounts',self.c.chart)]:
   if field=='chart_of_accounts':
    from apps.core_erp.accounting.models import ChartOfAccounts
    value=ChartOfAccounts.plain_objects.create(tenant=self.c.tenant,name='Replacement chart')
   original=getattr(account,field);setattr(account,field,value)
   with self.subTest(field=field),self.assertRaises(AccountingError):account.save()
   setattr(account,field,original)
  self.assertEqual(self.c.post(entry).pk,entry.pk)
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.c.tenant.pk)['is_valid'])
 def test_posted_account_identity_cannot_change_through_bulk_writes(self):
  entry=self.c.post(self.c.draft());query=Account.plain_objects.filter(pk=self.c.a.pk)
  with self.assertRaises(AccountingError):query.update(code='Bulk mutation')
  account=query.get();account.type='LIABILITY'
  with self.assertRaises(AccountingError):Account.plain_objects.bulk_update([account],['type'])
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.c.tenant.pk)['is_valid'])
 def test_posted_account_nonstructural_update_preserves_hash(self):
  entry=self.c.post(self.c.draft());self.c.a.name='Renamed display label';self.c.a.save(update_fields=['name']);Account.plain_objects.filter(pk=self.c.a.pk).update(is_active=False)
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.c.tenant.pk)['is_valid'])
  self.assertEqual(self.c.post(entry).pk,entry.pk)
 def test_reversal_failure_rolls_back_before_retry(self):
  original=self.c.post(self.c.draft());count=JournalEntry.plain_objects.count()
  from apps.core_erp.accounting.models import AccountingAuditLog
  create=AccountingAuditLog.objects.create
  def fail(**kw):
   if kw.get('action')=='REVERSE':raise OSError('Synthetic reverse audit failure')
   return create(**kw)
  with patch.object(AccountingAuditLog.objects,'create',side_effect=fail):
   with self.assertRaises(OSError):LedgerEngine.reverse_entry(original.pk,tenant_id=self.c.tenant.pk,actor=self.c.user)
  self.assertEqual(JournalEntry.plain_objects.count(),count);self.assertTrue(LedgerEngine.reverse_entry(original.pk,tenant_id=self.c.tenant.pk,actor=self.c.user).is_posted)
if __name__=='__main__':unittest.main()
