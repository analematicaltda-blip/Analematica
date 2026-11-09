"""Server shape contract deliberately cannot assert ciphertext authenticity."""
import base64,copy,importlib.util,unittest
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'ANALEMATICA-BACKEND/core_erp/accounting/fiscal_envelope.py'
spec=importlib.util.spec_from_file_location('fiscal_envelope_contract',path);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
def encoded(data):return base64.urlsafe_b64encode(data).rstrip(b'=').decode()
class EnvelopeTests(unittest.TestCase):
 def setUp(self):
  self.company='00000000-0000-4000-8000-000000000001'
  self.value={'schema':engine.SCHEMA,'algorithm':engine.ALGORITHM,'context':{'company_id':self.company,'document_id':'00000000-0000-4000-8000-000000000002'},'iv':encoded(bytes(12)),'wrapped_key':encoded(bytes(40)),'ciphertext':encoded(bytes(17))}
 def test_structural_acceptance_is_not_crypto_authentication_or_storage(self):
  before=copy.deepcopy(self.value);result=engine.inspect_envelope(self.value,self.company)
  self.assertFalse(result['authenticated_ciphertext_verified']);self.assertFalse(result['stored']);self.assertFalse(result['ledger_written'])
  self.assertEqual(self.value,before);self.assertNotIn('ciphertext',result)
 def test_digest_is_stable_across_object_key_order(self):
  self.assertEqual(engine.inspect_envelope(self.value,self.company)['envelope_digest'],engine.inspect_envelope(dict(reversed(list(self.value.items()))),self.company)['envelope_digest'])
 def test_unknown_fields_and_plaintext_or_key_fields_rejected(self):
  for field in ['plaintext','xml','pdf','kek','private_key']:
   with self.subTest(field=field),self.assertRaises(ValueError):engine.inspect_envelope({**self.value,field:'SENSITIVE'},self.company)
 def test_company_document_and_schema_scope(self):
  for changed in [{**self.value,'schema':'unknown'},{**self.value,'context':{**self.value['context'],'document_id':'invalid'}}]:
   with self.assertRaises(ValueError):engine.inspect_envelope(changed,self.company)
  with self.assertRaises(ValueError):engine.inspect_envelope(self.value,'00000000-0000-4000-8000-000000000003')
 def test_encoding_sizes_and_noncanonical_padding_rejected(self):
  for field,value in [('iv',encoded(bytes(11))),('wrapped_key',encoded(bytes(39))),('ciphertext',encoded(bytes(16))),('iv',self.value['iv']+'='),('ciphertext',self.value['ciphertext'][:-1]+'B')]:
   with self.subTest(field=field),self.assertRaises(ValueError):engine.inspect_envelope({**self.value,field:value},self.company)
 def test_intake_cap_is_explicit(self):
  with self.assertRaises(ValueError):engine.inspect_envelope({**self.value,'ciphertext':encoded(bytes(engine.MAX_DOCUMENT_BYTES+17))},self.company)

if __name__=='__main__':unittest.main()
