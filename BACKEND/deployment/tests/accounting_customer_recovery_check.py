"""Unknown-commit fault injection and scoped receipt API; SQL qualified separately."""
import runpy,unittest,copy,json,uuid,base64
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_customer_package_check.py')),run_name='recovery_fixture')
from core_erp.accounting.customer_package_store import CustomerPackageStore,StorageConflict,StorageOutcomeUnknown,package_receipt
from django.db import DatabaseError

class MemoryConnection:
    vendor='postgresql';in_atomic_block=False
    def __init__(self,company,mode='normal'):
        self.company=company;self.mode=mode;self.autocommit=True;self.rows={};self.pending={};self.closed=False;self.rollbacks=0
    def get_autocommit(self):return self.autocommit
    def set_autocommit(self,value):
        if value and self.mode=='cleanup_failure':raise DatabaseError('Synthetic cleanup failure')
        self.autocommit=value
    def close(self):self.closed=True;self.pending={}
    def rollback(self):
        self.rollbacks+=1;self.pending={}
        if self.mode=='rollback_failure':raise DatabaseError('Synthetic rollback failure')
    def commit(self):
        if self.mode=='before_commit':raise DatabaseError('Synthetic lost connection before commit')
        self.rows.update(self.pending);self.pending={}
        if self.mode=='after_commit':raise DatabaseError('Synthetic acknowledgement lost after commit')
    @contextmanager
    def cursor(self):
        owner=self
        class Cursor:
            result=None
            def execute(self,sql,args=None):
                if sql.startswith('SELECT pg_advisory'):self.result=None
                elif sql.startswith('SELECT company_id'):self.result=(owner.company,)
                elif sql.startswith('SELECT package_digest,package_bytes'):
                    self.result=owner.pending.get((args[1],args[2]),owner.rows.get((args[1],args[2])))
                elif sql.startswith('SELECT revision,package_digest'):
                    values=[(key[1],value[0]) for key,value in owner.rows.items() if key[0]==args[1]];self.result=max(values) if values else None
                elif sql.startswith('INSERT INTO'):
                    owner.pending[(args[1],args[2])]=(args[3],args[5]);self.result=None
                else:raise AssertionError('Unexpected synthetic SQL operation')
            def fetchone(self):return self.result
        yield Cursor()

class CommitRecoveryChecks(unittest.TestCase):
 def setUp(self):self.company=str(uuid.uuid4());self.value=fixture['package'](self.company)
 def store(self,connection):
  with patch.object(CustomerPackageStore,'check',return_value=None):return CustomerPackageStore(connection,self.company)
 def put(self,connection,value=None):
  with patch.object(CustomerPackageStore,'check',return_value=None):return self.store(connection).put(value or self.value)
 def test_lost_acknowledgement_keeps_committed_bytes_and_discards_connection(self):
  c=MemoryConnection(self.company,'after_commit')
  with self.assertRaises(StorageOutcomeUnknown):self.put(c)
  self.assertTrue(c.closed);self.assertEqual(len(c.rows),1);self.assertEqual(c.rollbacks,0)
  fresh=MemoryConnection(self.company);fresh.rows=c.rows;self.assertTrue(self.put(fresh)['replayed']);self.assertEqual(len(fresh.rows),1)
 def test_failure_before_commit_is_still_unknown_until_fresh_read(self):
  c=MemoryConnection(self.company,'before_commit')
  with self.assertRaises(StorageOutcomeUnknown):self.put(c)
  self.assertTrue(c.closed);self.assertFalse(c.rows);self.assertFalse(c.pending)
  fresh=MemoryConnection(self.company);self.assertFalse(self.put(fresh)['replayed']);self.assertEqual(len(fresh.rows),1)
 def test_conflict_is_not_masked_by_failed_rollback(self):
  c=MemoryConnection(self.company);self.put(c);c.mode='rollback_failure';other=fixture['package'](self.company,document=self.value['envelope']['context']['document_id']);other['auth_tag']=base64.urlsafe_b64encode(b'x'*32).decode().rstrip('=');other['package_digest']=__import__('hashlib').sha256(json.dumps({k:v for k,v in other.items() if k!='package_digest'},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
  with self.assertRaises(StorageConflict):self.put(c,other)
  self.assertTrue(c.closed);self.assertEqual(len(c.rows),1)
 def test_successful_commit_is_not_reported_failed_by_cleanup(self):
  c=MemoryConnection(self.company,'cleanup_failure');result=self.put(c);self.assertTrue(result['stored']);self.assertTrue(c.closed);self.assertEqual(len(c.rows),1)
 def test_dedicated_connection_is_still_required(self):
  c=MemoryConnection(self.company);c.in_atomic_block=True
  with self.assertRaises(ValueError):self.put(c)
  self.assertFalse(c.rows)

class ReceiptApiChecks(unittest.TestCase):
 setUp=fixture['CustomerPackageChecks'].setUp
 save_grant=fixture['CustomerPackageChecks'].save_grant
 post=fixture['CustomerPackageChecks'].post
 def receipt(self,**kw):
  params={'revision':'1','package_digest':self.value['package_digest'],**kw}
  return self.client.get('/v1/receipts/'+self.value['envelope']['context']['document_id'],params=params,headers=self.headers)
 def test_receipt_reads_exact_opaque_version_and_does_not_return_ciphertext(self):
  self.assertEqual(self.post().status_code,200);r=self.receipt();self.assertEqual(r.status_code,200,r.text);data=r.json();self.assertTrue(data['stored']);self.assertEqual(data['verified_by'],'EXACT_VERSION_READ');self.assertFalse(data['authenticated_ciphertext_verified']);self.assertFalse(data['fiscal_accepted']);self.assertNotIn('envelope',data);self.assertNotIn('key_descriptor',data);self.assertIn('no-store',r.headers['cache-control'])
 def test_unobserved_version_remains_not_found_without_false_ack(self):self.assertEqual(self.receipt().status_code,404)
 def test_conflicting_digest_does_not_acknowledge_another_package(self):self.post();self.assertEqual(self.receipt(package_digest='f'*64).status_code,409)
 def test_read_permission_is_required_after_append(self):
  self.post();self.grant['permissions']=['append'];self.save_grant();self.assertEqual(self.receipt().status_code,403)
 def test_revocation_is_checked_again_for_receipt(self):
  self.post();self.grant['token_sha256']='f'*64;self.save_grant();self.assertEqual(self.receipt().status_code,401)
 def test_noncanonical_duplicate_and_unexpected_queries_are_rejected(self):
  for query in [[('revision','1'),('revision','2'),('package_digest','f'*64)],{'revision':'01','package_digest':'f'*64},{'revision':'1','package_digest':'f'*64,'origin':'https://evil.test'}]:
   r=self.client.get('/v1/receipts/'+self.value['envelope']['context']['document_id'],params=query,headers=self.headers);self.assertEqual(r.status_code,422,r.text)
 def test_uncertain_write_is_machine_readable_without_sql_details(self):
  def fail(value):raise StorageOutcomeUnknown('PRIVATE-SQL-DETAIL')
  self.store.put=fail;r=self.post();self.assertEqual(r.status_code,503);self.assertEqual(r.json()['detail']['code'],'PACKAGE_WRITE_OUTCOME_UNKNOWN');self.assertNotIn('PRIVATE-SQL',r.text)
 def test_receipt_does_not_accept_newer_version_as_the_requested_one(self):
  self.post();v=fixture['package'](self.company,document=self.value['envelope']['context']['document_id'],revision=2,previous=self.value['package_digest']);self.store.items[v['envelope']['context']['document_id']]=v
  self.assertEqual(self.receipt().status_code,409)
if __name__=='__main__':unittest.main()
