"""ACC010 portable client envelope/recovery contract; no hardware qualification."""
import sys,unittest,uuid,json,copy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'DESKTOP/fiscal-signer'),str(ROOT/'BACKEND/ANALEMATICA-BACKEND')]
from package_crypto import seal_package,open_package,derive,decode
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from core_erp.accounting.fiscal_envelope import inspect_envelope
from core_erp.accounting.customer_package_store import inspect_package
class ACC010Acceptance(unittest.TestCase):
 def setUp(self):self.scope={'company_id':str(uuid.uuid4()),'document_id':str(uuid.uuid4())};self.password='synthetic client password 123456';self.plain=b'<Invoice>synthetic private document</Invoice>'
 def package(self):return seal_package(self.plain,self.password,self.scope)
 def test_fresh_dek_iv_salt_for_each_encryption(self):
  a=self.package();b=self.package()
  def dek(p):
   kw,_=derive(self.password,decode(p['key_descriptor']['salt'],16));return aes_key_unwrap(kw,decode(p['envelope']['wrapped_key'],40))
  self.assertNotEqual(dek(a),dek(b));self.assertNotEqual(a['envelope']['iv'],b['envelope']['iv']);self.assertNotEqual(a['key_descriptor']['salt'],b['key_descriptor']['salt'])
 def test_authenticated_serialized_recovery_without_plaintext_or_key_in_package(self):
  p=self.package();raw=json.dumps(p);self.assertNotIn(self.password,raw);self.assertNotIn(self.plain.decode(),raw);self.assertNotIn('kek',p);self.assertNotIn('dek',p)
  plain,restored=open_package(json.loads(raw),self.password,self.scope);self.assertEqual(plain,self.plain);self.assertEqual(restored,p)
 def test_aad_is_cryptographically_bound_to_company_document_and_domain(self):
  p=self.package();env=p['envelope'];kw,_=derive(self.password,decode(p['key_descriptor']['salt'],16));dek=aes_key_unwrap(kw,decode(env['wrapped_key'],40))
  correct=[env['schema'],env['algorithm'],self.scope['company_id'],self.scope['document_id'],'fiscal-document']
  for index,value in [(2,str(uuid.uuid4())),(3,str(uuid.uuid4())),(4,'other-domain')]:
   wrong=correct[:];wrong[index]=value
   with self.assertRaises(InvalidTag):AESGCM(dek).decrypt(decode(env['iv'],12),decode(env['ciphertext'],maximum=1024*1024+16),json.dumps(wrong,separators=(',',':')).encode())
 def test_wrong_key_or_company_does_not_recover(self):
  p=self.package()
  with self.assertRaises(ValueError):open_package(p,'wrong password of adequate length',self.scope)
  with self.assertRaises(ValueError):open_package(p,self.password,{**self.scope,'company_id':str(uuid.uuid4())})
 def test_exact_reference_is_checked_when_supplied(self):
  p=self.package();pin={'revision':p['revision'],'package_digest':p['package_digest']};self.assertEqual(open_package(p,self.password,self.scope,expected_reference=pin)[0],self.plain)
  for bad in [{'revision':1,'package_digest':'a'*64},{'revision':2,'package_digest':p['package_digest']},{'revision':True,'package_digest':p['package_digest']},None,{'revision':1}]:
   with self.subTest(pin=bad),self.assertRaises(ValueError):open_package(p,self.password,self.scope,expected_reference=bad)
 def test_metadata_and_ciphertext_tamper_does_not_mutate_original(self):
  p=self.package();before=copy.deepcopy(p)
  for key in ['iv','wrapped_key','ciphertext']:
   modified=copy.deepcopy(p);v=modified['envelope'][key];modified['envelope'][key]=('B' if v[0]=='A' else 'A')+v[1:]
   with self.assertRaises(ValueError):open_package(modified,self.password,self.scope)
  self.assertEqual(p,before)
 def test_erp_preview_never_receives_client_keys_or_plaintext_fields(self):
  p=self.package();result=inspect_envelope(p['envelope'],self.scope['company_id']);self.assertFalse(result['stored']);self.assertFalse(result['authenticated_ciphertext_verified']);self.assertNotIn('ciphertext',result)
  for key in ['plaintext','xml','password','kek','dek','private_key']:
   with self.assertRaises(ValueError):inspect_envelope({**p['envelope'],key:'SENSITIVE'},self.scope['company_id'])
   with self.assertRaises(ValueError):inspect_package({**p,key:'SENSITIVE'},self.scope['company_id'])
 def test_customer_store_only_checks_ciphertext_shape_without_claiming_authenticity(self):
  p=self.package();metadata,_=inspect_package(p,self.scope['company_id']);self.assertEqual(set(metadata),{'company_id','document_id','revision','previous_digest','package_digest'});self.assertNotIn('plaintext',metadata)
 def test_unicode_password_and_bounds_are_explicit(self):
  password='🔐'*16;p=seal_package(self.plain,password,self.scope);self.assertEqual(open_package(p,password,self.scope)[0],self.plain)
  for password in ['short','prefix that is long '+chr(0xD800),'x'*1025]:
   with self.assertRaises(ValueError):seal_package(self.plain,password,self.scope)
if __name__=='__main__':unittest.main()
