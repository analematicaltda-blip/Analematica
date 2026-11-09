"""Real local XAdES laboratory signatures, pinned synthetic chain, no fiscal claims."""
import copy,hashlib,json,os,subprocess,sys,tempfile,unittest,uuid
from pathlib import Path
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'DESKTOP/fiscal-signer'))
from local_signer import sign_package,verify_lab_xml,NS,LaboratorySigningError
from package_crypto import seal_package,open_package
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID,ExtendedKeyUsageOID,ObjectIdentifier
from lxml import etree

class LocalSignerChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.now=datetime.now(timezone.utc);cls.root_key=rsa.generate_private_key(public_exponent=65537,key_size=2048);cls.leaf_key=rsa.generate_private_key(public_exponent=65537,key_size=2048);cls.password='synthetic package password 123';cls.key_password=b'synthetic encrypted key password 456';cls.company=str(uuid.uuid4());cls.doc=str(uuid.uuid4());cls.expected={'company_id':cls.company,'document_id':cls.doc};cls.policy=b'SGACD LABORATORY ONLY policy, not DIAN or production.'
  name=lambda cn,serial:x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,cn),x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME,'SGACD LABORATORY ONLY'),x509.NameAttribute(NameOID.SERIAL_NUMBER,serial)])
  cls.root_name=name('SGACD LAB ROOT','LABROOT');cls.leaf_name=name('SGACD LAB LEAF','NIT 100000001-0')
  def build(subject,issuer,key,ca):
   return x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(cls.now-timedelta(hours=1)).not_valid_after(cls.now+timedelta(days=2)).add_extension(x509.BasicConstraints(ca=ca,path_length=0 if ca else None),True).add_extension(x509.KeyUsage(digital_signature=not ca,content_commitment=False,key_encipherment=False,data_encipherment=False,key_agreement=False,key_cert_sign=ca,crl_sign=ca,encipher_only=False,decipher_only=False),True)
  cls.builder=staticmethod(build);cls.root_cert=build(cls.root_name,cls.root_name,cls.root_key,True).sign(cls.root_key,hashes.SHA256());cls.leaf_cert=build(cls.leaf_name,cls.root_name,cls.leaf_key,False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CODE_SIGNING]),False).sign(cls.root_key,hashes.SHA256());cls.root_pem=cls.root_cert.public_bytes(serialization.Encoding.PEM);cls.leaf_pem=cls.leaf_cert.public_bytes(serialization.Encoding.PEM);cls.key_pem=cls.leaf_key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.BestAvailableEncryption(cls.key_password))
  cls.plain=('''<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"><cbc:UBLVersionID>2.1</cbc:UBLVersionID><cbc:CustomizationID>SGACD-STRUCTURAL-DRAFT</cbc:CustomizationID><cbc:ProfileID>LOCAL-UNSIGNED-DRAFT</cbc:ProfileID><cbc:ID>DRAFT-LAB-001</cbc:ID><cbc:UUID>'''+cls.doc+'''</cbc:UUID><cbc:IssueDate>2026-11-09</cbc:IssueDate><cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode><cbc:Note>BORRADOR LOCAL SIN VALIDEZ FISCAL</cbc:Note><cbc:DocumentCurrencyCode>COP</cbc:DocumentCurrencyCode><cac:AccountingSupplierParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>Synthetic lab supplier</cbc:RegistrationName><cbc:CompanyID>100000001</cbc:CompanyID></cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty><cac:AccountingCustomerParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>Synthetic lab customer</cbc:RegistrationName><cbc:CompanyID>100000002</cbc:CompanyID></cac:PartyLegalEntity></cac:Party></cac:AccountingCustomerParty><cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="COP">10.00</cbc:PayableAmount></cac:LegalMonetaryTotal><cac:InvoiceLine><cbc:ID>1</cbc:ID><cbc:LineExtensionAmount currencyID="COP">10.00</cbc:LineExtensionAmount><cac:Item><cbc:Description>Synthetic lab service</cbc:Description></cac:Item></cac:InvoiceLine></Invoice>''').encode()
  cls.profile={'mode':'LABORATORY_ONLY','company_id':cls.company,'document_id':cls.doc,'supplier_nit':'100000001','source_sha256':hashlib.sha256(cls.plain).hexdigest(),'leaf_sha256':cls.leaf_cert.fingerprint(hashes.SHA256()).hex(),'root_sha256':cls.root_cert.fingerprint(hashes.SHA256()).hex(),'certificate_subject_serial':'NIT 100000001-0','policy_id':'urn:sgacd:lab-policy:test','policy_sha256':hashlib.sha256(cls.policy).hexdigest()};cls.value=seal_package(cls.plain,cls.password,cls.expected);cls.cached=None
 def args(self):return {'value':copy.deepcopy(self.value),'package_password':self.password,'key_pem':self.key_pem,'key_password':self.key_password,'leaf_pem':self.leaf_pem,'root_pem':self.root_pem,'policy':self.policy,'profile':copy.deepcopy(self.profile),'source_confirmation':'REVISADO '+self.value['package_digest'][:12],'sign_confirmation':'FIRMAR LAB '+self.doc}
 def sign(self,**extra):return sign_package(**{**self.args(),**extra})
 def signed(self):
  if type(self).cached is None:type(self).cached=self.sign()
  return copy.deepcopy(type(self).cached)
 def raw(self):return open_package(self.signed()['package'],self.password,self.expected)[0]
 def verify(self,raw,**extra):return verify_lab_xml(raw,**{'profile':copy.deepcopy(self.profile),'leaf_pem':self.leaf_pem,'root_pem':self.root_pem,'policy':self.policy,'reviewed_source':self.plain,**extra})
 def test_actual_xades_signature_and_no_fiscal_acceptance(self):
  result=self.signed();report=self.verify(self.raw());self.assertTrue(report['xml_signature_verified']);self.assertTrue(report['reviewed_source_verified']);self.assertFalse(report['fiscal_accepted']);self.assertFalse(report['dian_profile_validated']);self.assertFalse(report['certificate_revocation_checked']);self.assertFalse(report['network_called']);self.assertEqual(result['package']['revision'],2);self.assertEqual(result['package']['previous_digest'],self.value['package_digest'])
 def test_signed_xml_is_encrypted_and_original_preserved(self):
  original=copy.deepcopy(self.value);result=self.signed();self.assertNotIn('Synthetic lab supplier',json.dumps(result['package']));self.assertNotIn('BEGIN',json.dumps(result));self.assertEqual(self.value,original);self.assertNotEqual(result['package']['envelope']['ciphertext'],self.value['envelope']['ciphertext'])
 def test_two_explicit_confirmations_before_key_loading(self):
  for change in [{'source_confirmation':''},{'sign_confirmation':''}]:
   with patch('local_signer.serialization.load_pem_private_key') as load:
    with self.assertRaises(ValueError):self.sign(**change)
    load.assert_not_called()
 def test_production_profile_refused_before_private_key(self):
  with patch('local_signer.serialization.load_pem_private_key') as load:
   with self.assertRaises(ValueError):self.sign(profile={**self.profile,'mode':'PRODUCTION'})
   load.assert_not_called()
 def test_wrong_package_password_scope_and_source_digest(self):
  for change in [{'package_password':'wrong password of enough length'},{'profile':{**self.profile,'company_id':str(uuid.uuid4())}},{'profile':{**self.profile,'source_sha256':'a'*64}},{'profile':{**self.profile,'supplier_nit':'100000003'}}]:
   with self.assertRaises(ValueError):self.sign(**change)
 def test_unencrypted_key_and_wrong_key_password_denied(self):
  clear=self.leaf_key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  with self.assertRaises(ValueError):self.sign(key_pem=clear)
  with self.assertRaises(ValueError):self.sign(key_password=b'wrong key password of adequate length')
 def test_private_key_must_match_pinned_leaf(self):
  other=self.root_key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.BestAvailableEncryption(self.key_password))
  with self.assertRaises(ValueError):self.sign(key_pem=other)
 def test_wrong_trust_anchor_expired_and_naive_time_denied(self):
  for change in [{'profile':{**self.profile,'root_sha256':'a'*64}},{'now':self.now+timedelta(days=4)},{'now':self.now.replace(tzinfo=None)}]:
   with self.assertRaises(ValueError):self.sign(**change)
 def test_policy_bytes_and_nonlaboratory_policy_denied(self):
  with self.assertRaises(ValueError):self.sign(policy=b'changed policy')
  with self.assertRaises(ValueError):self.sign(profile={**self.profile,'policy_id':'https://example.test/real-policy'})
 def test_unsupported_critical_certificate_extension_denied(self):
  cert=self.builder(self.leaf_name,self.root_name,self.leaf_key,False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CODE_SIGNING]),False).add_extension(x509.UnrecognizedExtension(ObjectIdentifier('1.2.3.4.5.6'),b'unknown'),True).sign(self.root_key,hashes.SHA256())
  with self.assertRaises(ValueError):self.sign(leaf_pem=cert.public_bytes(serialization.Encoding.PEM),profile={**self.profile,'leaf_sha256':cert.fingerprint(hashes.SHA256()).hex()})
 def test_nonlaboratory_certificate_denied_even_if_pinned(self):
  real_name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Not laboratory'),x509.NameAttribute(NameOID.SERIAL_NUMBER,'NIT 100000001-0')]);cert=self.builder(real_name,self.root_name,self.leaf_key,False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CODE_SIGNING]),False).sign(self.root_key,hashes.SHA256())
  with self.assertRaises(ValueError):self.sign(leaf_pem=cert.public_bytes(serialization.Encoding.PEM),profile={**self.profile,'leaf_sha256':cert.fingerprint(hashes.SHA256()).hex()})
 def test_document_tampering_fails_cryptographic_verification(self):
  from signxml.exceptions import InvalidDigest
  root=etree.fromstring(self.raw());root.find('cac:LegalMonetaryTotal/cbc:PayableAmount',NS).text='11.00'
  with self.assertRaises(InvalidDigest):self.verify(etree.tostring(root))
 def test_reviewed_source_content_must_match_signed_invoice(self):
  changed=self.plain.replace(b'>10.00<',b'>11.00<')
  with self.assertRaises(ValueError):self.verify(self.raw(),profile={**self.profile,'source_sha256':hashlib.sha256(changed).hexdigest()},reviewed_source=changed)
 def test_duplicate_or_relocated_signature_denied(self):
  root=etree.fromstring(self.raw());signature=root.find('.//ds:Signature',NS);root.append(copy.deepcopy(signature))
  with self.assertRaises(ValueError):self.verify(etree.tostring(root))
  root=etree.fromstring(self.raw());signature=root.find('.//ds:Signature',NS);signature.getparent().remove(signature);root.append(signature)
  with self.assertRaises(ValueError):self.verify(etree.tostring(root))
 def test_external_reference_never_fetched(self):
  root=etree.fromstring(self.raw());root.find('.//ds:Reference',NS).set('URI','https://external.invalid/invoice')
  with patch('socket.create_connection',side_effect=AssertionError('Network forbidden')) as network:
   with self.assertRaises(ValueError):self.verify(etree.tostring(root))
   network.assert_not_called()
 def test_external_entities_denied_before_signing(self):
  bad=b'<!DOCTYPE Invoice [<!ENTITY x SYSTEM "file:///etc/passwd">]>'+self.plain;package=seal_package(bad,self.password,self.expected);args=self.args();args.update(value=package,profile={**self.profile,'source_sha256':hashlib.sha256(bad).hexdigest()},source_confirmation='REVISADO '+package['package_digest'][:12])
  with self.assertRaises(ValueError):sign_package(**args)
 def test_existing_signature_not_signed_again(self):
  raw=self.raw();p=seal_package(raw,self.password,self.expected)
  with self.assertRaises(ValueError):self.sign(value=p,source_confirmation='REVISADO '+p['package_digest'][:12],profile={**self.profile,'source_sha256':hashlib.sha256(raw).hexdigest()})
 def test_unsigned_document_is_not_a_verified_signature(self):
  with self.assertRaises(ValueError):self.verify(self.plain)
 def test_signing_path_does_not_use_network(self):
  with patch('socket.create_connection',side_effect=AssertionError('Network forbidden')) as network:self.verify(self.raw());network.assert_not_called()
 def test_cli_refuses_automated_terminal(self):
  run=subprocess.run([sys.executable,str(ROOT/'DESKTOP/fiscal-signer/sign_local.py'),*sum(([f'--{name}','unused'] for name in ['input','profile','key','leaf','root','policy','output']),[])],input='',text=True,capture_output=True);self.assertEqual(run.returncode,1);self.assertNotIn('BEGIN',run.stdout+run.stderr)
 def test_signed_document_matches_reference_xsd(self):
  run=subprocess.run([sys.executable,str(ROOT/'FRONTEND/deployment/tests/validate_ubl_reference.py')],input=json.dumps([self.raw().decode()]),text=True,capture_output=True);self.assertEqual(run.returncode,0,run.stderr)
 def test_signature_value_independent_public_key_verification(self):
  import base64
  from cryptography.hazmat.primitives.asymmetric import padding
  root=etree.fromstring(self.raw());info=root.find('.//ds:SignedInfo',NS);signature=base64.b64decode(root.find('.//ds:SignatureValue',NS).text)
  self.leaf_cert.public_key().verify(signature,etree.tostring(info,method='c14n',exclusive=False,with_comments=False),padding.PKCS1v15(),hashes.SHA256())
 def test_browser_recovers_signed_encrypted_package(self):
  with tempfile.TemporaryDirectory(prefix='local-signer-interop-') as folder:
   case=Path(folder)/'case.json';case.write_text(json.dumps({'package':self.signed()['package'],'password':self.password,'expected':self.expected,'signed_sha256':hashlib.sha256(self.raw()).hexdigest()}));case.chmod(0o600)
   run=subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/local_signer_interop.cjs')],env={**os.environ,'SIGNER_BROWSER_CASE':str(case),'PLAYWRIGHT_MODULE':str(ROOT/'DESKTOP/asistencia-sgacd/node_modules/playwright')},capture_output=True,text=True,timeout=45);self.assertEqual(run.returncode,0,run.stderr);self.assertTrue(json.loads(run.stdout)['passed'])
 @unittest.skipUnless(sys.platform=='linux','POSIX laboratory CLI contract')
 def test_interactive_cli_writes_only_encrypted_package(self):
  import pty,fcntl,termios,select,time
  with tempfile.TemporaryDirectory(prefix='local-signer-cli-') as folder:
   folder=Path(folder);values={'input':json.dumps(self.value).encode(),'profile':json.dumps(self.profile).encode(),'key':self.key_pem,'leaf':self.leaf_pem,'root':self.root_pem,'policy':self.policy};args=[]
   for name,data in values.items():
    path=folder/name;path.write_bytes(data);path.chmod(0o600);args.extend(['--'+name,str(path)])
   output=folder/'signed.json';args.extend(['--output',str(output)]);master,slave=pty.openpty()
   def terminal():os.setsid();fcntl.ioctl(slave,termios.TIOCSCTTY,0)
   process=subprocess.Popen([sys.executable,str(ROOT/'DESKTOP/fiscal-signer/sign_local.py'),*args],stdin=slave,stdout=slave,stderr=slave,preexec_fn=terminal,close_fds=True);os.close(slave);transcript=b''
   try:
    for prompt,answer in [('Contraseña local del paquete:',self.password),('Primera revisión',self.args()['source_confirmation']),('Segunda autorización',self.args()['sign_confirmation']),('Contraseña de la llave PKCS8 cifrada:',self.key_password.decode())]:
     deadline=time.monotonic()+30
     while prompt.encode() not in transcript:
      if time.monotonic()>deadline:raise AssertionError('Laboratory CLI prompt timeout')
      ready,_,_=select.select([master],[],[],1)
      if ready:transcript+=os.read(master,4096)
      if process.poll() is not None:raise AssertionError('Laboratory CLI exited before confirmation')
     os.write(master,answer.encode()+b'\n')
    self.assertEqual(process.wait(timeout=30),0)
    while select.select([master],[],[],0)[0]:
     try:transcript+=os.read(master,4096)
     except OSError:break
    self.assertNotIn(self.password.encode(),transcript);self.assertNotIn(self.key_password,transcript);self.assertEqual(output.stat().st_mode&0o077,0)
    packaged=json.loads(output.read_text());raw,_=open_package(packaged,self.password,self.expected);self.assertTrue(self.verify(raw)['xml_signature_verified']);self.assertFalse(self.verify(raw)['fiscal_accepted']);self.assertEqual(json.loads((folder/'input').read_text()),self.value)
   finally:
    if process.poll() is None:process.kill();process.wait(timeout=5)
    os.close(master)
if __name__=='__main__':unittest.main()
