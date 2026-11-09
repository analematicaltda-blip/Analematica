"""Actual cryptographic receipt verification and durable local retry metadata.
Synthetic codes/certificates only; never asserts DIAN acceptance or transmission.
"""
import copy,hashlib,json,os,runpy,sqlite3,subprocess,sys,tempfile,unittest,uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import timedelta
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_local_signer_check.py')),run_name='dian_receipt_lab_fixture')
from receipt_validation import verify_receipt,checked_profile,APPLICATION,NS,STATES
from receipt_journal import ReceiptJournal
from local_signer import LaboratorySigningError
from lxml import etree
from signxml import XMLSigner,methods,SignatureMethod,DigestAlgorithm,CanonicalizationMethod

class ReceiptChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.f=fixture['LocalSignerChecks'];cls.f.setUpClass()
  cls.profile={'mode':'LABORATORY_ONLY','company_id':cls.f.company,'document_id':cls.f.doc,'invoice_number':'LAB-001','invoice_fingerprint':hashlib.sha384(cls.f.plain).hexdigest(),'sender_id':'100000002','recipient_id':'100000001','environment':'HABILITACION-LAB','leaf_sha256':cls.f.profile['leaf_sha256'],'root_sha256':cls.f.profile['root_sha256'],'certificate_subject_serial':cls.f.profile['certificate_subject_serial']}
  cls.cache={}
 @classmethod
 def response(cls,code='LAB_ACCEPTED',changes=None,mutate=None):
  if changes is None and mutate is None and code in cls.cache:return cls.cache[code]
  p={**cls.profile,**(changes or {})};root=etree.Element('{'+APPLICATION+'}ApplicationResponse',nsmap={None:APPLICATION,**{k:NS[k] for k in ['cbc','cac','ext','ds']}})
  def add(parent,space,name,text=None):
   n=etree.SubElement(parent,'{'+NS[space]+'}'+name);n.text=text;return n
  ext=add(add(add(root,'ext','UBLExtensions'),'ext','UBLExtension'),'ext','ExtensionContent');placeholder=add(ext,'ds','Signature');placeholder.set('Id','placeholder')
  for key,value in [('CustomizationID','SGACD-LAB-RECEIPT'),('ProfileID','LABORATORY-ONLY'),('ProfileExecutionID',p['environment']),('UUID',str(uuid.uuid4()))]:add(root,'cbc',key,value)
  for kind,key in [('SenderParty','sender_id'),('ReceiverParty','recipient_id')]:add(add(add(root,'cac',kind),'cac','PartyTaxScheme'),'cbc','CompanyID',p[key])
  document=add(root,'cac','DocumentResponse');add(add(document,'cac','Response'),'cbc','ResponseCode',code);ref=add(document,'cac','DocumentReference');add(ref,'cbc','ID',p['invoice_number']);add(ref,'cbc','UUID',p['invoice_fingerprint'])
  if mutate is not None:mutate(root)
  signer=XMLSigner(method=methods.enveloped,signature_algorithm=SignatureMethod.RSA_SHA256,digest_algorithm=DigestAlgorithm.SHA256,c14n_algorithm=CanonicalizationMethod.CANONICAL_XML_1_0)
  signed=etree.tostring(signer.sign(root,key=cls.f.leaf_key,cert=[cls.f.leaf_cert]),encoding='UTF-8',xml_declaration=True)
  if changes is None and mutate is None:cls.cache[code]=signed
  return signed
 def verify(self,raw=None,**changes):return verify_receipt(raw or self.response(),**{'profile':copy.deepcopy(self.profile),'leaf_pem':self.f.leaf_pem,'root_pem':self.f.root_pem,**changes})
 def test_real_signature_and_three_distinct_laboratory_states(self):
  for code,state in STATES.items():
   r=self.verify(self.response(code));self.assertEqual(r['laboratory_response_state'],state);self.assertTrue(r['xml_signature_verified']);self.assertTrue(r['document_identity_matched'])
   for k in ['fiscal_accepted','dian_origin_verified','dian_profile_validated','certificate_revocation_checked','ledger_written','network_called','number_allocated','usable_as_fiscal_acceptance']:self.assertFalse(r[k])
 def test_tampered_document_or_response_code_denied(self):
  from signxml.exceptions import InvalidDigest
  for old,new in [(b'LAB-001',b'LAB-002'),(b'LAB_ACCEPTED',b'LAB_REJECTED')]:
   with self.assertRaises(InvalidDigest):self.verify(self.response().replace(old,new))
 def test_signed_foreign_document_sender_receiver_and_environment_denied(self):
  for changes in [{'invoice_number':'LAB-002'},{'invoice_fingerprint':'f'*96},{'sender_id':'100000003'},{'recipient_id':'100000004'},{'environment':'PRODUCTION'}]:
   with self.assertRaises(LaboratorySigningError):self.verify(self.response(changes=changes))
 def test_unknown_or_real_codes_cannot_become_laboratory_acceptance(self):
  for code in ['00','ACCEPTED','VALIDADO','']:
   with self.assertRaises(LaboratorySigningError):self.verify(self.response(code))
 def test_root_unsigned_duplicate_and_relocated_signatures_denied(self):
  for mode in ['unsigned','duplicate','relocated']:
   root=etree.fromstring(self.response());signature=root.xpath('.//ds:Signature',namespaces=NS)[0]
   if mode=='unsigned':signature.getparent().remove(signature)
   elif mode=='duplicate':root.append(copy.deepcopy(signature))
   else:signature.getparent().remove(signature);root.append(signature)
   with self.assertRaises(LaboratorySigningError):self.verify(etree.tostring(root))
 def test_signed_duplicate_parties_or_document_references_denied(self):
  def duplicate(root,path):root.append(copy.deepcopy(root.find(path,NS)))
  def duplicate_reference(root):
   node=root.find('cac:DocumentResponse',NS);node.append(copy.deepcopy(node.find('cac:DocumentReference',NS)))
  for mutate in [lambda root:duplicate(root,'cac:SenderParty'),duplicate_reference]:
   with self.assertRaises(LaboratorySigningError):self.verify(self.response(mutate=mutate))
 def test_external_reference_and_entities_not_fetched(self):
  with patch('socket.socket',side_effect=AssertionError('No network')):
   root=etree.fromstring(self.response());root.xpath('.//ds:Reference',namespaces=NS)[0].set('URI','https://not-a-real-server.invalid/receipt')
   with self.assertRaises(LaboratorySigningError):self.verify(etree.tostring(root))
   with self.assertRaises(LaboratorySigningError):self.verify(b'<!DOCTYPE x [<!ENTITY a SYSTEM "file:///etc/passwd">]><x>&a;</x>')
   self.assertTrue(self.verify()['xml_signature_verified'])
 def test_pinned_certificate_expiry_identity_and_root_enforced(self):
  for changes in [{'profile':{**self.profile,'leaf_sha256':'0'*64}},{'profile':{**self.profile,'root_sha256':'0'*64}},{'profile':{**self.profile,'certificate_subject_serial':'not-the-leaf'}},{'now':self.f.now+timedelta(days=5)}]:
   with self.assertRaises(LaboratorySigningError):self.verify(**changes)
 def test_profile_never_enables_production_or_accepts_secrets(self):
  for changes in [{'mode':'PRODUCTION'},{'environment':'HABILITACION'},{'pin':'never-store-secret'},{'company_id':'not-uuid'},{'invoice_fingerprint':'f'*64}]:
   with self.assertRaises(ValueError):checked_profile({**self.profile,**changes})
 def test_cli_refuses_noninteractive_receipt_verification(self):
  root=Path(__file__).resolve().parents[3]
  args=[sys.executable,str(root/'DESKTOP/fiscal-signer/verify_receipt_local.py')]
  for field in ['input','profile','leaf','root']:args+=['--'+field,'nonexistent-test-file']
  r=subprocess.run(args,input='',capture_output=True,text=True,timeout=10)
  self.assertEqual(r.returncode,1);self.assertNotIn('Traceback',r.stderr)
 def test_receipt_size_and_non_utf8_denied(self):
  for value in [b'x'*(1024*1024+1),b'\xff',b'']:
   with self.assertRaises((ValueError,etree.XMLSyntaxError)):verify_receipt(value,profile=self.profile,leaf_pem=self.f.leaf_pem,root_pem=self.f.root_pem)

class JournalChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  ReceiptChecks.setUpClass();cls.f=ReceiptChecks.f;cls.profile=ReceiptChecks.profile
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='receipt-journal-lab-');self.addCleanup(self.temp.cleanup)
  self.path=Path(self.temp.name)/'local.sqlite3';self.journal=ReceiptJournal.initialize(self.path);self.scope={'profile':copy.deepcopy(self.profile),'signed_document_sha256':hashlib.sha256(self.f.plain).hexdigest()}
 def prepare(self):return self.journal.prepare(**self.scope)
 def begin(self):return self.journal.begin_attempt(**self.scope)
 def apply(self,token,code='LAB_ACCEPTED',**changes):
  return self.journal.apply_receipt(**self.scope,**{'attempt_token':token,'raw':ReceiptChecks.response(code),'leaf_pem':self.f.leaf_pem,'root_pem':self.f.root_pem,**changes})
 def test_prepare_retry_reopen_preserves_key_and_never_allocates_number(self):
  a=self.prepare();b=ReceiptJournal(self.path).prepare(**self.scope);self.assertEqual(a['submission_key'],b['submission_key']);self.assertTrue(b['replayed']);self.assertEqual(b['revision'],1);self.assertFalse(b['number_allocated'])
 def test_uncertain_retry_retains_document_and_rejects_stale_attempt(self):
  p=self.prepare();a=self.begin();u=self.journal.mark_uncertain(**self.scope,attempt_token=a['attempt_token']);self.assertEqual(u['state'],'UNCERTAIN_LAB');self.assertTrue(self.journal.mark_uncertain(**self.scope,attempt_token=a['attempt_token'])['replayed'])
  b=self.begin();self.assertEqual(p['submission_key'],b['submission_key']);self.assertNotEqual(a['attempt_token'],b['attempt_token'])
  with self.assertRaises(LaboratorySigningError):self.apply(a['attempt_token'])
  self.assertFalse(self.apply(b['attempt_token'])['fiscal_accepted'])
 def test_inflight_and_final_states_cannot_restart(self):
  self.prepare();a=self.begin()
  with self.assertRaises(LaboratorySigningError):self.begin()
  self.apply(a['attempt_token'])
  with self.assertRaises(LaboratorySigningError):self.begin()
 def test_pending_then_final_and_replayed_response(self):
  self.prepare();a=self.begin();p=self.apply(a['attempt_token'],'LAB_PENDING');self.assertEqual(p['state'],'PENDING_LAB_ONLY');self.assertTrue(self.apply(a['attempt_token'],'LAB_PENDING')['replayed'])
  r=self.apply(a['attempt_token']);self.assertEqual(r['state'],'ACCEPTED_LAB_ONLY');self.assertTrue(self.apply(a['attempt_token'])['replayed'])
  with self.assertRaises(LaboratorySigningError):self.apply(a['attempt_token'],'LAB_REJECTED')
 def test_rejected_is_distinct_and_never_fiscal_acceptance(self):
  self.prepare();a=self.begin();r=self.apply(a['attempt_token'],'LAB_REJECTED');self.assertEqual(r['state'],'REJECTED_LAB_ONLY');self.assertFalse(r['usable_as_fiscal_acceptance'])
 def test_changed_signed_digest_or_profile_never_reuses_document_identity(self):
  self.prepare()
  for changes in [{'signed_document_sha256':'f'*64},{'profile':{**self.profile,'invoice_number':'LAB-999'}},{'profile':{**self.profile,'root_sha256':'f'*64}}]:
   with self.assertRaises(LaboratorySigningError):self.journal.prepare(**{**self.scope,**changes})
 def test_bad_receipt_leaves_journal_unchanged(self):
  self.prepare();a=self.begin();before=self.journal.inspect(**self.scope)
  from signxml.exceptions import InvalidDigest
  with self.assertRaises(InvalidDigest):self.apply(a['attempt_token'],raw=ReceiptChecks.response().replace(b'LAB-001',b'LAB-002'))
  self.assertEqual(before,self.journal.inspect(**self.scope))
 def test_failed_prepare_rolls_back_intent_and_event(self):
  original=self.journal.append
  def fail(*args,**kwargs):original(*args,**kwargs);raise RuntimeError('Synthetic storage fault')
  with patch.object(self.journal,'append',side_effect=fail):
   with self.assertRaises(RuntimeError):self.prepare()
  self.assertFalse(self.prepare()['replayed'])
 def test_local_append_only_guards_block_update_delete_and_missing_guard(self):
  self.prepare()
  with sqlite3.connect(self.path) as con:
   for sql in ['DELETE FROM event','UPDATE intent SET signed_digest=\'changed\'']:
    with self.assertRaises(sqlite3.IntegrityError):con.execute(sql)
   con.execute('DROP TRIGGER no_event_delete')
  with self.assertRaises(LaboratorySigningError):self.journal.inspect(**self.scope)
 def test_same_named_but_weakened_guard_is_rejected(self):
  self.prepare()
  with sqlite3.connect(self.path) as con:
   con.executescript('DROP TRIGGER no_event_update; CREATE TRIGGER no_event_update BEFORE UPDATE ON event BEGIN SELECT 1; END;')
  with self.assertRaises(LaboratorySigningError):self.journal.inspect(**self.scope)
 def test_private_path_permissions_no_overwrite_no_auto_initialization(self):
  with self.assertRaises(FileExistsError):ReceiptJournal.initialize(self.path)
  self.path.chmod(0o644)
  with self.assertRaises(LaboratorySigningError):self.prepare()
  self.path.chmod(0o600);alias=Path(self.temp.name)/'alias';alias.symlink_to(self.path)
  with self.assertRaises(LaboratorySigningError):ReceiptJournal(alias)
  missing=ReceiptJournal(Path(self.temp.name)/'missing.sqlite3')
  with self.assertRaises(LaboratorySigningError):missing.prepare(**self.scope)
 def test_concurrent_prepare_and_begin_have_single_result(self):
  barrier=Barrier(2)
  def prepare():barrier.wait();return self.prepare()
  with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(lambda _:prepare(),range(2)))
  self.assertEqual(sum(not r['replayed'] for r in rows),1);self.assertEqual(rows[0]['submission_key'],rows[1]['submission_key'])
  barrier=Barrier(2)
  def begin():
   barrier.wait()
   try:return self.begin()['attempt_token']
   except LaboratorySigningError:return None
  with ThreadPoolExecutor(max_workers=2) as pool:attempts=list(pool.map(lambda _:begin(),range(2)))
  self.assertEqual(sum(v is not None for v in attempts),1)
 def test_only_metadata_persisted_no_xml_private_keys_or_party_identifiers(self):
  self.prepare();a=self.begin();self.apply(a['attempt_token']);raw=self.path.read_bytes()
  for value in [b'ApplicationResponse',b'BEGIN PRIVATE KEY',b'100000001',b'LAB-001',self.profile['invoice_fingerprint'].encode()]:self.assertNotIn(value,raw)
  state=ReceiptJournal(self.path).inspect(**self.scope);self.assertFalse(state['network_called']);self.assertFalse(state['ledger_written']);self.assertFalse(state['signed_document_bytes_verified'])
if __name__=='__main__':unittest.main()
