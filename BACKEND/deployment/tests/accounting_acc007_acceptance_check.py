"""ACC007 canonical tamper detection and installed SQLite SQL protection."""
import copy,runpy,unittest,uuid
from pathlib import Path
from decimal import Decimal
f=runpy.run_path(str(Path(__file__).with_name('accounting_sql_check.py')),run_name='acc007_fixture')
from django.db import connection,transaction,DatabaseError
from apps.core_erp.accounting.models import Account,JournalEntry,LedgerEntry
from apps.core_erp.accounting.integrity import journal_hash
from apps.core_erp.accounting.ledger_engine import LedgerEngine,rows
from apps.core_erp.accounting.sql_guard_health import inspect_guards
from apps.core_erp.accounting import sql_identity_guards
class ACC007Acceptance(unittest.TestCase):
 def setUp(self):self.c=f['SqlGuardTests']();self.c.setUp();self.entry=self.c.entry
 def tearDown(self):self.c.tearDown()
 def test_header_financial_fields_are_committed_by_existing_v2_hash(self):
  changes={'tenant_id':uuid.uuid4(),'period_id':uuid.uuid4(),'date':self.entry.date.replace(year=self.entry.date.year-1),'reference':'changed','description':'changed','currency':'USD','base_currency':'EUR','exchange_rate':Decimal('1.010000'),'created_by_id':987654,'event_type':'CHANGED','financial_event_id':'changed','correlation_id':'changed','rule_version':'changed','is_reversal':True,'reversed_entry_id':uuid.uuid4(),'posted_at':None,'previous_hash':'f'*64}
  original=self.entry.system_hash
  for field,value in changes.items():
   with self.subTest(field=field):
    clone=copy.copy(self.entry);setattr(clone,field,value);self.assertNotEqual(journal_hash(clone,rows(self.entry),clone.previous_hash),original)
 def test_every_line_identity_account_amount_and_currency_is_hashed(self):
  original=self.entry.system_hash
  for field,value in {'id':uuid.uuid4(),'tenant_id':uuid.uuid4(),'account_id':uuid.uuid4(),'debit_amount':Decimal('12.34'),'credit_amount':Decimal('12.34'),'amount_transaction':Decimal('12.34'),'amount_base':Decimal('12.34'),'currency':'USD','description':'changed'}.items():
   with self.subTest(field=field):
    lines=rows(self.entry);line=lines[0]
    if field=='account_id':
     # Retain a valid related model while changing the FK identifier.
     account=copy.copy(line.account);account.pk=value;line.account=account
    else:setattr(line,field,value)
    self.assertNotEqual(journal_hash(self.entry,lines,self.entry.previous_hash),original)
  lines=rows(self.entry);self.assertNotEqual(journal_hash(self.entry,lines[:1],self.entry.previous_hash),original)
 def test_account_code_type_and_chart_are_hashed(self):
  for field,value in [('code','ALTERED'),('type','LIABILITY'),('chart_of_accounts_id',uuid.uuid4())]:
   lines=rows(self.entry);line=lines[0];account=copy.copy(line.account);setattr(account,field,value);line.account=account
   self.assertNotEqual(journal_hash(self.entry,lines,self.entry.previous_hash),self.entry.system_hash)
 def test_line_order_does_not_change_canonical_hash(self):
  self.assertEqual(journal_hash(self.entry,list(reversed(rows(self.entry))),self.entry.previous_hash),self.entry.system_hash)
 def raw_rejected(self,sql,params):
  with self.assertRaises(DatabaseError),transaction.atomic():
   with connection.cursor() as cursor:cursor.execute(sql,params)
 def test_sql_protects_posted_header_and_line_columns(self):
  for field,value in [('description','modified'),('currency','USD'),('exchange_rate','2'),('is_posted',False)]:self.raw_rejected('UPDATE core_erp_journalentry SET '+field+'=%s WHERE id=%s',[value,self.entry.pk.hex])
  line=rows(self.entry)[0]
  for field,value in [('account_id',line.account_id.hex),('amount_base','0.01'),('currency','USD'),('id',uuid.uuid4().hex)]:self.raw_rejected('UPDATE core_erp_ledgerentry SET '+field+'=%s WHERE id=%s',[value,line.pk.hex])
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.entry.tenant_id)['is_valid'])
 def test_sql_protects_used_account_identity_and_deletion(self):
  account=rows(self.entry)[0].account
  for field,value in [('code','altered'),('type','EQUITY'),('chart_of_accounts_id',uuid.uuid4().hex),('tenant_id',uuid.uuid4().hex),('id',uuid.uuid4().hex)]:self.raw_rejected('UPDATE core_erp_account SET '+field+'=%s WHERE id=%s',[value,account.pk.hex])
  self.raw_rejected('DELETE FROM core_erp_account WHERE id=%s',[account.pk.hex])
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.entry.tenant_id)['is_valid'])
 def test_display_label_and_activation_do_not_rewrite_history(self):
  account=rows(self.entry)[0].account
  with connection.cursor() as cursor:cursor.execute('UPDATE core_erp_account SET name=%s,is_active=%s WHERE id=%s',['New visible label',False,account.pk.hex])
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.entry.tenant_id)['is_valid'])
 def test_health_detects_replaced_body_and_does_not_repair(self):
  self.assertTrue(inspect_guards(connection)['ready'])
  with connection.cursor() as cursor:
   cursor.execute('DROP TRIGGER accounting_header_update_v1')
   cursor.execute('CREATE TRIGGER accounting_header_update_v1 BEFORE UPDATE ON core_erp_journalentry BEGIN SELECT 1; END')
  self.assertIn('accounting_sql_guard_body_changed',inspect_guards(connection)['checks'])
  self.assertFalse(inspect_guards(connection)['ready'])
 def test_health_requires_new_identity_guard_and_never_installs_it(self):
  with connection.cursor() as cursor:cursor.execute('DROP TRIGGER accounting_account_identity_v1')
  report=inspect_guards(connection);self.assertFalse(report['ready']);self.assertIn('accounting_sql_guards_missing',report['checks'])
  self.assertFalse(inspect_guards(connection)['ready'])
 def test_failed_guard_reinstallation_rolls_back_drops(self):
  from unittest.mock import patch
  with patch.object(sql_identity_guards,'statements',side_effect=RuntimeError('Synthetic migration failure')):
   with self.assertRaises(RuntimeError):sql_identity_guards.install(connection)
  self.assertTrue(inspect_guards(connection)['ready'])
 def test_guard_migration_reinstall_preserves_all_existing_hashes(self):
  before=list(JournalEntry.plain_objects.values_list('pk','system_hash','previous_hash','hash_version'))
  sql_identity_guards.uninstall(connection);sql_identity_guards.install(connection);sql_identity_guards.install(connection)
  self.assertEqual(list(JournalEntry.plain_objects.values_list('pk','system_hash','previous_hash','hash_version')),before)
  self.assertTrue(inspect_guards(connection)['ready']);self.assertEqual(self.c.case.post().pk,self.entry.pk)
if __name__=='__main__':unittest.main()
