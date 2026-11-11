"""Installed SQLite triggers, real isolated ORM and raw update/bulk operations."""
import copy,runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='sql_guard_fixture')
from django.db import connection,transaction,DatabaseError
from apps.core_erp.accounting import sql_guards,sql_guard_hardening,sql_identity_guards
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
from apps.core_erp.accounting.ledger_engine import LedgerEngine

class SqlGuardTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['AdapterTests']();self.case.setUp();sql_guards.install(connection);sql_guard_hardening.install(connection);sql_identity_guards.install(connection)
  self.entry=self.case.post();self.line=LedgerEntry.plain_objects.filter(journal_entry=self.entry).first()
 def tearDown(self):sql_identity_guards.uninstall(connection);sql_guards.uninstall(connection)
 def rejected(self,action):
  with self.assertRaisesRegex(DatabaseError,'ACCOUNTING_'),transaction.atomic():action()
 def test_posted_header_cannot_be_changed_deleted_or_unposted(self):
  query=JournalEntry.plain_objects.filter(pk=self.entry.pk)
  for action in [lambda:query.update(description='Changed'),lambda:query.update(is_posted=False),lambda:query._raw_delete('default')]:self.rejected(action)
 def test_posted_lines_cannot_be_changed_deleted_or_inserted(self):
  query=LedgerEntry.plain_objects.filter(pk=self.line.pk)
  self.rejected(lambda:query.update(debit_amount='99'))
  self.rejected(lambda:query._raw_delete('default'))
  clone=copy.copy(self.line);clone.pk=uuid.uuid4();clone._state=copy.copy(self.line._state);clone._state.adding=True
  self.rejected(lambda:LedgerEntry.plain_objects.bulk_create([clone]))
 def test_new_posted_header_must_not_bypass_draft_creation(self):
  clone=copy.copy(self.entry);clone.pk=uuid.uuid4();clone._state=copy.copy(self.entry._state);clone._state.adding=True
  self.rejected(lambda:JournalEntry.plain_objects.bulk_create([clone]))
 def test_policy_history_is_immutable_but_new_revisions_work(self):
  mapping=self.case.ratio_mapping();self.assertEqual(self.case.configure_ratio(mapping).status_code,201)
  policy=AccountingRatioPolicy.objects.get(tenant=self.case.tenant)
  self.rejected(lambda:AccountingRatioPolicy.objects.filter(pk=policy.pk).update(evidence_digest='f'*64))
  self.rejected(lambda:AccountingRatioPolicy.objects.filter(pk=policy.pk)._raw_delete('default'))
  self.assertEqual(self.case.configure_ratio(mapping,expected_revision=1).status_code,201)
 def test_posting_replay_and_reversal_still_work(self):
  self.assertEqual(self.case.post().pk,self.entry.pk)
  reversal=LedgerEngine.reverse_entry(self.entry.pk,'Reviewed correction',tenant_id=self.case.tenant.pk,actor=self.case.user)
  self.assertTrue(reversal.is_posted);self.assertTrue(LedgerEngine.validate_ledger_integrity(self.case.tenant.pk)['is_valid'])
 def test_install_is_idempotent_and_reverse_is_explicit(self):
  sql_guards.install(connection)
  self.rejected(lambda:JournalEntry.plain_objects.filter(pk=self.entry.pk).update(description=self.entry.description))
  sql_guards.uninstall(connection)
  self.assertEqual(JournalEntry.plain_objects.filter(pk=self.entry.pk).update(description=self.entry.description),1)
  sql_guards.install(connection)

 def test_health_detects_missing_guard_and_never_repairs_it(self):
  from apps.core_erp.accounting.sql_guard_health import inspect_guards
  self.assertTrue(inspect_guards(connection)['ready'])
  with connection.cursor() as cursor:cursor.execute('DROP TRIGGER accounting_line_update_v1')
  result=inspect_guards(connection)
  self.assertFalse(result['ready']);self.assertIn('accounting_sql_guards_missing',result['checks'])
  self.assertFalse(inspect_guards(connection)['ready'])
  sql_guards.install(connection);self.assertTrue(inspect_guards(connection)['ready'])

 def test_health_detects_trigger_attached_to_wrong_table(self):
  from apps.core_erp.accounting.sql_guard_health import inspect_guards
  with connection.cursor() as cursor:
   cursor.execute('DROP TRIGGER accounting_line_update_v1')
   cursor.execute('CREATE TRIGGER accounting_line_update_v1 BEFORE UPDATE ON core_erp_accountingratiopolicy BEGIN SELECT 1; END')
  self.assertIn('accounting_sql_guards_invalid',inspect_guards(connection)['checks'])

class PrivilegeAuditTests(unittest.TestCase):
 def test_sqlite_is_not_qualified_for_postgresql_role_separation(self):
  from apps.core_erp.accounting.db_privileges import inspect_privileges
  result=inspect_privileges(connection)
  self.assertFalse(result['ready']);self.assertTrue(result['read_only'])
  self.assertEqual(result['checks'],['accounting_db_privileges_unsupported'])
 def test_readonly_command_can_require_qualification(self):
  from django.core.management import call_command
  from django.core.management.base import CommandError
  import io
  output=io.StringIO();call_command('accounting_db_privileges',stdout=output)
  self.assertIn('accounting_db_privileges_unsupported',output.getvalue())
  with self.assertRaises(CommandError):call_command('accounting_db_privileges',require_ready=True,stdout=io.StringIO())

class RuntimeProfileTests(unittest.TestCase):
 def test_profile_has_no_ddl_delete_or_grant_side_effect(self):
  from apps.core_erp.accounting.runtime_profile import describe_profile
  profile=describe_profile();self.assertFalse(profile['grants_executed'])
  self.assertEqual(len({row['table'] for row in profile['tables']}),len(profile['tables']))
  self.assertTrue(all(set(row['privileges'])<={'SELECT','INSERT','UPDATE'} for row in profile['tables']))
  locking=next(row for row in profile['tables'] if row['table']=='core_erp_tenant')
  self.assertEqual(locking['privileges'],['SELECT']);self.assertEqual(locking['update_columns'],['id'])
  currency=next(row for row in profile['tables'] if row['table']=='core_erp_currency')
  self.assertEqual(currency['privileges'],['SELECT']);self.assertEqual(currency['update_columns'],['id'])
  chart=next(row for row in profile['tables'] if row['table']=='core_erp_chartofaccounts')
  self.assertEqual(chart['privileges'],['SELECT']);self.assertEqual(chart['update_columns'],['id'])

class ConstraintNormalizationTests(unittest.TestCase):
 def expression(self,casts):
  labels=['PENDING','LEASED','RETRY','DELIVERED','QUARANTINED']
  items=', '.join("'"+label+"'::character varying"+('::text' if casts else '') for label in labels)
  return 'CHECK (status::text = ANY (ARRAY['+items+']'+('' if casts else '::text[]')+'))'
 def row(self,sql):return ('core_erp_accountingdelivery','accounting_delivery_valid_status','c',True,False,False,sql)
 def test_only_known_postgresql_cast_rewrite_is_normalized(self):
  from accounting_restore_contract import normalize_constraints
  self.assertEqual(normalize_constraints([self.row(self.expression(False))]),normalize_constraints([self.row(self.expression(True))]))
 def test_changed_domain_is_not_ignored(self):
  from accounting_restore_contract import normalize_constraints
  with self.assertRaises(AssertionError):normalize_constraints([self.row(self.expression(True).replace('LEASED','INVALID'))])
 def test_unrelated_constraints_remain_exact(self):
  from accounting_restore_contract import normalize_constraints
  row=('different','other','c',True,False,False,'CHECK (x>0)')
  self.assertEqual(normalize_constraints([row]),[list(row)])

if __name__=='__main__':unittest.main()
