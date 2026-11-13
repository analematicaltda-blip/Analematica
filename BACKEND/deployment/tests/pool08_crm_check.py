"""Strict CRM domain boundaries; real ORM/API integration has separate suites."""
import importlib.util,unittest,uuid,copy
from pathlib import Path
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[3]
PATHS=['BACKEND/SGA-CD-BACKEND/app/commercial/pool08/crm.py','BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/pool08/crm.py','BACKEND/ANALEMATICA-BACKEND/gestion_comercial/pool08/crm.py']
def cases(path):
 spec=importlib.util.spec_from_file_location('crm_rules',ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 class MemoryStore:
  scope='local-company'
  def __init__(self):self.items={};self.events={}
  @contextmanager
  def transaction(self):
   backup=copy.deepcopy((self.items,self.events))
   try:yield
   except Exception:self.items,self.events=backup;raise
  def lock(self):pass
  def event(self,rid):return self.events.get(rid)
  def get(self,cid):return copy.deepcopy(self.items.get(cid))
  def duplicates(self,*args):return []
  def save(self,item,revision):self.items[item['id']]=copy.deepcopy(item)
  def append(self,rid,actor,operation,contact,fingerprint,receipt,data):self.events[rid]={'scope':self.scope,'fingerprint':fingerprint,'receipt':receipt}
 class Checks(unittest.TestCase):
  def setUp(self):self.store=MemoryStore();self.crm=module.CRM(self.store,actor='1',authorize=lambda:True,member=lambda ref:ref=='1')
  def body(self,**extra):
   data=dict(name='Persona',origin='MANUAL',responsible_ref='1');data.update(extra)
   return dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=data)
  def test_malformed_contacts(self):
   for extra in [{'email':None},{'phone':12},{'email':'no-email'},{'phone':'bad'},{'name':'x'*151},{'origin':''},{'notes':'x'*2001}]:
    with self.assertRaises(module.CRMError):self.crm.command(self.body(**extra))
   self.assertFalse(self.store.items)
  def test_untrusted_scope_and_roles(self):
   for key in ['tenant_ref','role','authorized','wallet_access']:
    body=self.body();body[key]='forged'
    with self.assertRaises(module.CRMError):self.crm.command(body)
  def test_foreign_responsible(self):
   with self.assertRaisesRegex(module.CRMError,'RESPONSIBLE_NOT_IN_COMPANY'):self.crm.command(self.body(responsible_ref='2'))
  def test_request_and_revision_validation(self):
   for changes in [{'request_id':'bad'},{'expected_revision':True},{'expected_revision':-1},{'data':[]},{'operation':'transfer_money'}]:
    body=self.body();body.update(changes)
    with self.assertRaises(module.CRMError):self.crm.command(body)
  def test_replay_cannot_resurrect_baja(self):
   body=self.body();cid=self.crm.command(body)['contact_id']
   self.crm.command(dict(request_id=str(uuid.uuid4()),operation='withdraw',contact_id=cid,expected_revision=1,data={'reason':'Titular'}))
   self.assertTrue(self.crm.command(body)['previous_receipt_only']);self.assertEqual(self.store.get(cid)['status'],'WITHDRAWN')
  def test_missing_timezone_rejected(self):
   cid=self.crm.command(self.body())['contact_id']
   with self.assertRaisesRegex(module.CRMError,'TIMEZONE_REQUIRED'):self.crm.command(dict(request_id=str(uuid.uuid4()),operation='task',contact_id=cid,expected_revision=1,data=dict(title='Llamar',due_at='2026-12-01T12:00:00',responsible_ref='1')))
  def test_consent_channels_purposes_evidence_and_booleans(self):
   cid=self.crm.command(self.body())['contact_id']
   for extra in [{'channel':'ALL'},{'purpose':'ANY'},{'granted':'yes'},{'evidence_digest':'unverified'}]:
    data=dict(channel='EMAIL',purpose='MARKETING',granted=True,evidence_digest='a'*64,expires_at='2026-12-10T00:00:00+00:00');data.update(extra)
    with self.assertRaises(module.CRMError):self.crm.command(dict(request_id=str(uuid.uuid4()),operation='consent',contact_id=cid,expected_revision=1,data=data))
  def test_email_control_characters_never_enter_contact_or_audit(self):
   for char in ['\x00','\x01','\x1f','\x7f','\x85','\x9f']:
    with self.subTest(code=ord(char)):
     with self.assertRaisesRegex(module.CRMError,'INVALID_CONTACT'):self.crm.command(self.body(email='bad'+char+'@example.test'))
   self.assertFalse(self.store.items);self.assertFalse(self.store.events)
  def test_numeric_or_boolean_evidence_is_not_a_hash_string(self):
   cid=self.crm.command(self.body())['contact_id'];before=copy.deepcopy(self.store.items)
   for evidence in [int('1'*64),True,None,['a'*64],{'sha256':'a'*64}]:
    data=dict(channel='EMAIL',purpose='MARKETING',granted=False,evidence_digest=evidence,expires_at='2026-12-10T00:00:00+00:00')
    with self.assertRaisesRegex(module.CRMError,'INVALID_CONSENT'):self.crm.command(dict(request_id=str(uuid.uuid4()),operation='consent',contact_id=cid,expected_revision=1,data=data))
   self.assertEqual(self.store.items,before);self.assertEqual(len(self.store.events),1)
  def test_email_normalization_and_consent_remain_declarations(self):
   cid=self.crm.command(self.body(email='  PERSONA+ventas@Example.test  '))['contact_id'];self.assertEqual(self.store.get(cid)['email'],'persona+ventas@example.test')
   data=dict(channel='EMAIL',purpose='MARKETING',granted=True,evidence_digest='a'*64,expires_at=(module.datetime.now(module.timezone.utc)+module.timedelta(days=1)).isoformat())
   self.crm.command(dict(request_id=str(uuid.uuid4()),operation='consent',contact_id=cid,expected_revision=1,data=data));consent=self.store.get(cid)['consents']['EMAIL:MARKETING'];self.assertFalse(consent['evidence_authenticity_verified']);self.assertFalse(consent['delivery_authorized'])
  def test_invalid_unicode_is_a_domain_error_without_writing(self):
   with self.assertRaisesRegex(module.CRMError,'INVALID_TEXT_ENCODING'):self.crm.command(self.body(name='invalid'+chr(0xD800)))
   self.assertFalse(self.store.items);self.assertFalse(self.store.events)
  def test_authority_checked_again_inside_transaction(self):
   calls=[]
   def auth():
    calls.append(True)
    if len(calls)>1:raise module.CRMError('REVOKED',403)
   self.crm.authorize=auth
   with self.assertRaisesRegex(module.CRMError,'REVOKED'):self.crm.command(self.body())
   self.assertFalse(self.store.items)
 return Checks
suite=unittest.TestSuite()
for path in PATHS:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cases(path)))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
