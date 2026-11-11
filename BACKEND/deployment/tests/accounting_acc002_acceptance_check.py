"""ACC002 original criteria with actual ORM instances, bulk SQL and new UUIDs."""
import runpy,unittest,uuid,copy
from pathlib import Path
from django.db import connection,transaction,DatabaseError
f=runpy.run_path(str(Path(__file__).with_name('accounting_posting_check.py')),run_name='acc002_fixture')
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.accounting import sql_guards
from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
if AccountingRatioPolicy._meta.db_table not in connection.introspection.table_names():
 with connection.schema_editor() as editor:editor.create_model(AccountingRatioPolicy)
from apps.core_erp.accounting.posting_write import permits,posting_save
class ACC002Acceptance(unittest.TestCase):
 def setUp(self):self.case=f['PostingTests']();self.case.setUp();self.c=self.case
 def test_fresh_uuid_header_and_lines_create_without_reading_missing_object(self):
  entry=self.c.draft();self.assertIsInstance(entry.pk,uuid.UUID);self.assertFalse(entry.is_posted);self.assertEqual(LedgerEntry.plain_objects.filter(journal_entry=entry).count(),2)
  first=LedgerEntry.plain_objects.filter(journal_entry=entry).first();first.description='Allowed draft change';first.save(update_fields=['description']);self.assertEqual(LedgerEntry.plain_objects.get(pk=first.pk).description,'Allowed draft change')
  deferred=JournalEntry.plain_objects.only('id','description').get(pk=entry.pk);deferred.description='Deferred draft update';deferred.save(update_fields=['description']);self.assertEqual(JournalEntry.plain_objects.get(pk=entry.pk).description,'Deferred draft update')
 def test_loaded_and_newly_saved_identities_cannot_move(self):
  for loaded in [False,True]:
   entry=self.c.draft();line=LedgerEntry.plain_objects.filter(journal_entry=entry).first()
   if loaded:entry=JournalEntry.plain_objects.get(pk=entry.pk)
   for instance in [entry,line]:
    original=instance.pk;instance.pk=uuid.uuid4()
    with self.assertRaises(PermissionError):instance.save()
    instance.pk=original
 def test_posted_header_all_instance_save_forms_and_delete_are_rejected(self):
  posted=self.c.post(self.c.draft());original=posted.system_hash
  for kwargs in [{},{'update_fields':['description']},{'force_update':True},{'force_insert':True}]:
   row=JournalEntry.plain_objects.get(pk=posted.pk);row.description='Blocked'
   with self.assertRaises(PermissionError):row.save(**kwargs)
  with self.assertRaises(PermissionError):posted.delete()
  self.assertEqual(JournalEntry.plain_objects.get(pk=posted.pk).system_hash,original)
 def test_stale_cached_header_cannot_save_or_unpost(self):
  entry=self.c.draft();stale=JournalEntry.plain_objects.get(pk=entry.pk);self.c.post(entry)
  for value in [False,True]:
   stale.is_posted=value;stale._validated_post=True
   with self.assertRaises(PermissionError):stale.save()
 def test_cached_draft_parent_cannot_mutate_delete_or_add_posted_lines(self):
  entry=self.c.draft();line=LedgerEntry.plain_objects.select_related('journal_entry').filter(journal_entry=entry).first();cached=line.journal_entry;self.assertFalse(cached.is_posted);self.c.post(entry)
  with self.assertRaises(PermissionError):line.save()
  with self.assertRaises(PermissionError):line.delete()
  with self.assertRaises(PermissionError):LedgerEntry(tenant=self.c.tenant,journal_entry=cached,account=self.c.a,debit_amount='1.00').save()
 def test_instance_flag_does_not_authorize_posted_uuid_creation(self):
  entry=JournalEntry(tenant=self.c.tenant,period=self.c.period,date=self.c.period.period_start,description='Forged internal flag',is_posted=True);entry._validated_post=True
  with self.assertRaises(PermissionError):entry.save()
  self.assertFalse(JournalEntry.plain_objects.filter(pk=entry.pk).exists())
 def test_temporary_capability_is_bound_to_identity_and_reset_after_failure(self):
  one=self.c.draft();two=self.c.draft();self.assertFalse(permits(one))
  with self.assertRaises(RuntimeError):
   with posting_save(one):
    self.assertTrue(permits(one));self.assertFalse(permits(two))
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1) as pool:self.assertFalse(pool.submit(permits,one).result())
    raise RuntimeError('Synthetic interruption')
  self.assertFalse(permits(one));one.is_posted=True
  with self.assertRaises(PermissionError):one.save()
 def test_sql_guards_block_bulk_mutations_and_creation_in_posted_parent(self):
  sql_guards.install(connection)
  try:
   entry=self.c.post(self.c.draft());line=LedgerEntry.plain_objects.filter(journal_entry=entry).first();clone=copy.copy(line);clone._state=copy.copy(line._state);clone._state.adding=True;clone.pk=uuid.uuid4()
   actions=[lambda:JournalEntry.plain_objects.filter(pk=entry.pk).update(description='Blocked'),lambda:JournalEntry.plain_objects.filter(pk=entry.pk).delete(),lambda:LedgerEntry.plain_objects.filter(pk=line.pk).update(description='Blocked'),lambda:LedgerEntry.plain_objects.filter(pk=line.pk).delete(),lambda:LedgerEntry.plain_objects.bulk_create([clone]),lambda:LedgerEntry.plain_objects.bulk_update([line],['description'])]
   for action in actions:
    with self.assertRaises(DatabaseError),transaction.atomic():action()
   self.assertEqual(LedgerEntry.plain_objects.filter(journal_entry=entry).count(),2)
  finally:sql_guards.uninstall(connection)
if __name__=='__main__':unittest.main()
