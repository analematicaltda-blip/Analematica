"""Real existing ledger contracts on isolated ORM tables; never posts real funds."""
import runpy
from pathlib import Path
import unittest
import uuid
from datetime import date
from decimal import Decimal

fixture=runpy.run_path(str(Path(__file__).with_name('company_identity_check.py')),run_name='accounting_fixture')
from apps.core_erp.accounting.models import ChartOfAccounts,Account,FiscalPeriod,JournalEntry,LedgerEntry
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError,TenantMismatchError
from apps.core_erp.accounting.validation import validate_lines
from apps.core_erp.tenancy.models import Tenant
for model in (ChartOfAccounts,Account,FiscalPeriod,JournalEntry,LedgerEntry):fixture['fixture']['create'](model)

class AccountingFoundation(unittest.TestCase):
 def setUp(self):
  self.tenant=Tenant.objects.create(name='Accounting fixture',tax_id='ledger-'+uuid.uuid4().hex,state='ACTIVE')
  self.foreign=Tenant.objects.create(name='Other fixture',tax_id='foreign-'+uuid.uuid4().hex,state='ACTIVE')
  self.chart=ChartOfAccounts.plain_objects.create(tenant=self.tenant,name='Fixture chart')
  self.a=Account.plain_objects.create(tenant=self.tenant,chart_of_accounts=self.chart,code='1105',name='Cash',type='ASSET')
  self.b=Account.plain_objects.create(tenant=self.tenant,chart_of_accounts=self.chart,code='4105',name='Income',type='REVENUE')
  self.period=FiscalPeriod.plain_objects.create(tenant=self.tenant,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open')
 def lines(self):return [{'account':self.a,'debit':'10.00'},{'account':self.b,'credit':'10.00'}]
 def create(self,lines=None):return JournalService.create_entry(str(self.tenant.pk),date(2026,11,8),'Fixture only',lines or self.lines())
 def test_new_uuid_entry_can_be_created(self):
  entry=self.create();self.assertFalse(entry.is_posted)
  self.assertEqual(LedgerEntry.plain_objects.filter(journal_entry=entry).count(),2)
 def test_invalid_money_and_imbalance_create_no_header_or_lines(self):
  for invalid in ['-1','NaN','Infinity','0.001',1.0,True,'10000000000000000']:
   before=JournalEntry.plain_objects.count()
   with self.subTest(value=repr(invalid)),self.assertRaises(AccountingError):
    self.create([{'account':self.a,'debit':invalid},{'account':self.b,'credit':'10.00'}])
   self.assertEqual(JournalEntry.plain_objects.count(),before)
 def test_both_sides_zero_and_unbalanced_are_rejected(self):
  for left,right in [('10','1'),('0','0')]:
   with self.assertRaises(AccountingError):validate_lines([{'debit':left,'credit':right},{'credit':'10'}])
  with self.assertRaises(AccountingError):validate_lines([{'debit':'10'},{'credit':'9.99'}])
 def test_cross_company_account_rejected_before_header(self):
  other_chart=ChartOfAccounts.plain_objects.create(tenant=self.foreign,name='Foreign chart')
  other=Account.plain_objects.create(tenant=self.foreign,chart_of_accounts=other_chart,code='1105',name='Foreign',type='ASSET')
  before=JournalEntry.plain_objects.count()
  with self.assertRaises(TenantMismatchError):self.create([{'account':other,'debit':'10'},{'account':self.b,'credit':'10'}])
  self.assertEqual(JournalEntry.plain_objects.count(),before)
 def test_stale_active_flag_is_rechecked(self):
  Account.plain_objects.filter(pk=self.a.pk).update(is_active=False)
  with self.assertRaises(AccountingError):self.create()
 def test_ambiguous_open_period_is_rejected(self):
  FiscalPeriod.plain_objects.create(tenant=self.tenant,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open')
  with self.assertRaises(AccountingError):self.create()
 def test_posted_entry_guard_is_preserved(self):
  entry=self.create();JournalEntry.plain_objects.filter(pk=entry.pk).update(is_posted=True)
  entry.description='Cannot overwrite'
  with self.assertRaises(PermissionError):entry.save()
 def test_stale_parent_does_not_allow_posted_line_mutation(self):
  entry=self.create();line=LedgerEntry.plain_objects.filter(journal_entry=entry).first()
  # Cache a pre-posting parent, then simulate another writer posting the entry.
  _=line.journal_entry
  JournalEntry.plain_objects.filter(pk=entry.pk).update(is_posted=True)
  line.description='No mutation'
  with self.assertRaises(PermissionError):line.save()
  with self.assertRaises(PermissionError):line.delete()
 def test_balance_validation_does_not_depend_on_request_tenant_manager(self):
  entry=self.create();self.assertTrue(LedgerEngine.validate_balance(entry))
  LedgerEntry.plain_objects.filter(journal_entry=entry,account=self.b).update(credit_amount=Decimal('9.99'))
  with self.assertRaises(AccountingError):LedgerEngine.validate_balance(entry)

if __name__=='__main__':unittest.main()
