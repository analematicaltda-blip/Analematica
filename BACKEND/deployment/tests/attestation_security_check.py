"""Cryptographic Android attestation fixtures; NOT real hardware or identity proof.
Every CA, key and independent approval below is temporary synthetic test data.
"""
import base64,hashlib,json,runpy,secrets,tempfile,unittest,uuid
from dataclasses import replace
from datetime import datetime,timedelta,timezone as dt_timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('provider_security_check.py')),run_name='fixture_setup')
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import ec,rsa
from cryptography.x509.oid import NameOID
from django.db import transaction
from django.test import override_settings
from django.utils import timezone
from django.http import Http404
from rest_framework.exceptions import APIException,PermissionDenied
from rest_framework.test import APIClient
from api.models import CustomUser
from apps.wallet.models import WalletDeviceCredential,WalletDeviceChallenge,Wallet,WalletLimiteOperativo,WalletMovimiento,WalletTransferIntent
from apps.wallet.services import device_approvals as devices,internal_transfer as transfers,enrollment_authorization as grants
from apps.wallet.services.android_attestation import AndroidAttestationPolicy,AndroidAttestationVerifier,RevocationSnapshot,AttestationRejected,ATTESTATION_OID,nodes
for model in [CustomUser,WalletDeviceChallenge,WalletLimiteOperativo,WalletMovimiento,WalletTransferIntent]:fixture['create'](model)
AUDIENCE='00000000-0000-0000-0000-000000000124'
PKG='co.analematica.fixture';SIGNER=hashlib.sha256(b'public synthetic application certificate').digest()


def der(tag,value):
 size=len(value);encoded=bytes([size]) if size<128 else bytes([128+(size.bit_length()+7)//8])+size.to_bytes((size.bit_length()+7)//8,'big')
 return bytes([tag])+encoded+value

def integer(value,tag=2):
 data=value.to_bytes(max(1,(value.bit_length()+7)//8),'big')
 return der(tag,(b'\x00' if data[0]&128 else b'')+data)

def seq(*values):return der(0x30,b''.join(values))
def octets(value):return der(4,value)
def integer_set(values):return der(0x31,b''.join(integer(value) for value in sorted(values)))
def context(tag,value):
 digits=[]
 while tag:digits.insert(0,tag&127);tag>>=7
 encoded=bytes([value|128 if index+1<len(digits) else value for index,value in enumerate(digits)])
 # Every authorization used here is a high-tag explicit context-specific value.
 return b'\xbf'+encoded+(bytes([len(value)]) if len(value)<128 else bytes([128+(len(value).bit_length()+7)//8])+len(value).to_bytes((len(value).bit_length()+7)//8,'big'))+value

def auth(values):return seq(*(context(tag,value) if tag>=31 else bytes([0xa0|tag])+der(4,value)[1:] for tag,value in sorted(values.items())))


def description(nonce,**options):
 now=datetime.now(dt_timezone.utc)
 app=seq(der(0x31,seq(octets(options.get('package',PKG).encode()),integer(options.get('version',42)))),der(0x31,octets(options.get('signer',SIGNER))))
 software={709:octets(app)}
 hardware={1:integer_set({2,3}),2:integer(3),3:integer(256),5:integer_set({4}),10:integer(1),504:integer(2),509:der(5,b''),702:integer(0),704:seq(octets(b'b'*32),der(1,b'\xff'),integer(0,10),octets(b'h'*32)),705:integer(140000),706:integer(int(now.strftime('%Y%m'))),718:integer(int(now.strftime('%Y%m%d'))),719:integer(int(now.strftime('%Y%m%d')))}
 hardware.update(options.get('hardware',{}));software.update(options.get('software',{}))
 for tag in options.get('remove',[]):hardware.pop(tag,None)
 return seq(integer(options.get('version_attestation',300)),integer(options.get('level',2),10),integer(options.get('version_keymaster',300)),integer(options.get('level',2),10),octets(nonce),octets(b''),auth(software),auth(hardware))

class AttestationChecks(unittest.TestCase):
 def setUp(self):
  self.now=timezone.now();self.ca=ec.generate_private_key(ec.SECP256R1());self.name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Public fixture CA, NOT Android trust')])
  self.root=self.certificate(self.ca,self.name,self.name,self.ca,True)
  self.root_der=self.root.public_bytes(serialization.Encoding.DER)
  self.snapshot=RevocationSnapshot(self.now-timedelta(seconds=1),self.now+timedelta(hours=1),frozenset())
  self.policy=AndroidAttestationPolicy((self.root_der,),PKG,frozenset({SIGNER.hex()}),42,120000,int(self.now.strftime('%Y%m')))
  self.verifier=AndroidAttestationVerifier(self.policy,lambda:self.snapshot)
  setting=override_settings(WALLET_DEVICE_ENROLLMENT_ENABLED=True,WALLET_APPROVAL_AUDIENCE=AUDIENCE,WALLET_ATTESTATION_VERIFIER=self.verifier,WALLET_ENROLLMENT_IDENTITY_VERIFIER=self.identity_fixture,WALLET_INTERNAL_TRANSFERS_ENABLED=True)
  setting.enable();self.addCleanup(setting.disable)
  self.owner=CustomUser(username='attestation-owner-'+uuid.uuid4().hex,role='BUSINESS_OWNER');CustomUser.objects.bulk_create([self.owner])
  self.device,self.nonce_text=devices.begin_enrollment(self.owner);self.nonce=base64.b64decode(self.nonce_text)
  self.key=ec.generate_private_key(ec.SECP256R1());self.raw=self.key.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint);self.public=base64.b64encode(self.raw).decode()
 def certificate(self,key,subject,issuer,signer,ca=False,extension=None,expired=False):
  start=self.now-timedelta(days=2);end=self.now-timedelta(days=1) if expired else self.now+timedelta(days=10)
  builder=x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(start).not_valid_after(end).add_extension(x509.BasicConstraints(ca=ca,path_length=1 if ca else None),True).add_extension(x509.KeyUsage(digital_signature=True,content_commitment=False,key_encipherment=False,data_encipherment=False,key_agreement=False,key_cert_sign=ca,crl_sign=ca,encipher_only=False,decipher_only=False),True)
  if extension is not None:builder=builder.add_extension(x509.UnrecognizedExtension(ATTESTATION_OID,extension),False)
  return builder.sign(signer,hashes.SHA256())
 def chain(self,description_bytes=None,**options):
  leaf=self.certificate(self.key,x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Public fixture key')]),self.name,options.pop('signer',self.ca),extension=description_bytes if description_bytes is not None else description(self.nonce),**options)
  return leaf,(leaf.public_bytes(serialization.Encoding.DER),self.root_der)
 def identity_fixture(self,user,credential,raw,reference,replaces_id):
  if reference!='independently-reviewed-fixture':raise PermissionDenied()
  return grants.IndependentEnrollmentApproval(uuid.uuid4(),user.pk,credential.pk,credential.audience,hashlib.sha256(raw).hexdigest(),credential.enrollment_nonce_hash,'REVIEWED_RECOVERY' if replaces_id else 'WEBAUTHN_UV',hashlib.sha256(b'synthetic independent verification').hexdigest(),timezone.now()-timedelta(seconds=1),min(timezone.now()+timedelta(minutes=4),credential.enrollment_expires_at),replaces_id)
 def permit(self,replaces=None):return grants.authorize_enrollment(self.owner,self.device.pk,self.public,'independently-reviewed-fixture',replaces)
 def enroll(self,replaces=None):
  leaf,chain=self.chain();permit=self.permit(replaces)
  result=devices.attest(self.owner,self.device.pk,self.public,[base64.b64encode(cert).decode() for cert in chain],permit)
  return result,leaf
 def test_valid_synthetic_chain_checks_cryptography_and_policy(self):
  leaf,chain=self.chain();evidence=self.verifier(self.device,self.raw,chain)
  self.assertEqual(evidence.platform,'ANDROID_KEY_ATTESTATION');self.assertEqual(evidence.policy_digest,self.policy.digest)
  self.assertEqual(evidence.certificate_serials[0],format(leaf.serial_number,'x'))
 def test_synthetic_rsa_root_and_ec_intermediate_chain(self):
  authority=rsa.generate_private_key(public_exponent=65537,key_size=2048)
  root_name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Public RSA fixture CA')])
  root=self.certificate(authority,root_name,root_name,authority,True)
  intermediate=self.certificate(self.ca,self.name,root_name,authority,True)
  leaf=self.certificate(self.key,x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Public fixture key')]),self.name,self.ca,extension=description(self.nonce))
  chain=tuple(cert.public_bytes(serialization.Encoding.DER) for cert in [leaf,intermediate,root])
  verifier=AndroidAttestationVerifier(replace(self.policy,trusted_roots=(chain[-1],)),lambda:self.snapshot)
  self.assertEqual(len(verifier(self.device,self.raw,chain).certificate_serials),3)
 def test_untrusted_root_and_invalid_certificate_signature(self):
  leaf,chain=self.chain()
  with self.assertRaises(AttestationRejected):AndroidAttestationVerifier(replace(self.policy,trusted_roots=(b'not a root',)),lambda:self.snapshot)(self.device,self.raw,chain)
  _,chain=self.chain(signer=ec.generate_private_key(ec.SECP256R1()))
  with self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,chain)
 def test_expired_certificate_wrong_nonce_and_wrong_public_key(self):
  for _,chain in [self.chain(expired=True),self.chain(description(secrets.token_bytes(32)))]:
   with self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,chain)
  _,chain=self.chain()
  with self.assertRaises(AttestationRejected):self.verifier(self.device,ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint),chain)
 def test_software_security_level_and_unlocked_or_unverified_boot(self):
  for data in [description(self.nonce,level=0),description(self.nonce,level=1),description(self.nonce,hardware={704:seq(octets(b'b'*32),der(1,b'\x00'),integer(0,10),octets(b'h'*32))}),description(self.nonce,hardware={704:seq(octets(b'b'*32),der(1,b'\xff'),integer(2,10),octets(b'h'*32))})]:
   with self.subTest(data=data[:12]),self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,self.chain(data)[1])
  tee=AndroidAttestationVerifier(replace(self.policy,require_strongbox=False),lambda:self.snapshot)
  self.assertTrue(tee(self.device,self.raw,self.chain(description(self.nonce,level=1))[1]).hardware_biometric)
 def test_per_operation_biometrics_and_key_purposes_required(self):
  for tag,value in [(503,der(5,b'')),(504,integer(1)),(504,integer(3)),(505,integer(30)),(506,der(5,b'')),(2,integer(1)),(3,integer(128)),(5,integer_set({0,4})),(10,integer(2)),(702,integer(2)),(1,integer_set({2}))]:
   with self.subTest(tag=tag),self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,self.chain(description(self.nonce,hardware={tag:value}))[1])
 def test_hardware_enforcement_and_unlocked_requirement(self):
  for data in [description(self.nonce,software={504:integer(2)}),description(self.nonce,remove=[509]),description(self.nonce,remove=[504]),description(self.nonce,version_attestation=2),description(self.nonce,version_keymaster=3)]:
   with self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,self.chain(data)[1])
 def test_application_package_signer_and_version_binding(self):
  for options in [{'package':'co.attacker.clone'},{'version':41},{'signer':b'z'*32}]:
   with self.subTest(options=options),self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,self.chain(description(self.nonce,**options))[1])
 def test_outdated_os_and_patch_levels_rejected(self):
  for fields in [{705:integer(110000)},{706:integer(202001)},{718:integer(20200101)},{719:integer(20200101)}]:
   with self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,self.chain(description(self.nonce,hardware=fields))[1])
 def test_revoked_leaf_or_root_and_stale_feed_rejected(self):
  leaf,chain=self.chain()
  for serial in [leaf.serial_number,self.root.serial_number]:
   self.snapshot=replace(self.snapshot,revoked_serials=frozenset({serial}))
   with self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,chain)
  self.snapshot=replace(self.snapshot,revoked_serials=frozenset(),valid_until=self.now-timedelta(seconds=1))
  with self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,chain)
 def test_malformed_der_duplicate_tags_and_trailing_data_rejected(self):
  for data in [b'',b'\x30\x80\x00\x00',description(self.nonce)+b'\x00',b'\x30\x81\x01\x00']:
   with self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,self.chain(data)[1])
  with self.assertRaises(AttestationRejected):nodes(b'\x30\x82\x00\x80')
 def test_hardware_alone_and_password_session_cannot_enroll(self):
  leaf,chain=self.chain()
  with self.assertRaises(APIException):devices.attest(self.owner,self.device.pk,self.public,[base64.b64encode(cert).decode() for cert in chain])
  with override_settings(WALLET_ENROLLMENT_IDENTITY_VERIFIER=None),self.assertRaises(APIException):self.permit()
  self.device.refresh_from_db();self.assertEqual(self.device.status,'PENDING')
 def test_verified_typed_independent_approval_and_attestation_activate_once(self):
  device,leaf=self.enroll();self.assertEqual(device.status,'VERIFIED');self.assertEqual(device.enrollment_method,'WEBAUTHN_UV')
  self.assertEqual(device.attestation_serials[0],format(leaf.serial_number,'x'));self.assertEqual(device.attestation_policy_digest,self.policy.digest);self.assertTrue(device.enrollment_authorization_digest)
  with transaction.atomic():self.assertEqual(devices.active_device(self.owner,device.pk).pk,device.pk)
  with self.assertRaises(APIException):self.enroll()
 def test_tampered_permit_and_changed_key_rejected(self):
  permit=self.permit();_,chain=self.chain();encoded=[base64.b64encode(cert).decode() for cert in chain]
  with self.assertRaises(APIException):devices.attest(self.owner,self.device.pk,self.public,encoded,permit+'x')
  different=base64.b64encode(ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)).decode()
  with self.assertRaises(APIException):devices.attest(self.owner,self.device.pk,different,encoded,permit)
 def test_client_dictionary_is_not_independent_approval(self):
  with override_settings(WALLET_ENROLLMENT_IDENTITY_VERIFIER=lambda *args:{'verified':True}),self.assertRaises(APIException):self.permit()
 def test_live_revocation_and_policy_change_block_registered_device(self):
  device,leaf=self.enroll();self.snapshot=replace(self.snapshot,revoked_serials=frozenset({leaf.serial_number}))
  with transaction.atomic(),self.assertRaises(APIException):devices.active_device(self.owner,device.pk)
  self.snapshot=replace(self.snapshot,revoked_serials=frozenset());changed=AndroidAttestationVerifier(replace(self.policy,minimum_package_version=43),lambda:self.snapshot)
  with override_settings(WALLET_ATTESTATION_VERIFIER=changed),transaction.atomic(),self.assertRaises(APIException):devices.active_device(self.owner,device.pk)
 def test_recovery_replaces_server_credential_atomically_without_deletion(self):
  old,_=self.enroll();self.device,self.nonce_text=devices.begin_enrollment(self.owner);self.nonce=base64.b64decode(self.nonce_text)
  self.key=ec.generate_private_key(ec.SECP256R1());self.raw=self.key.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint);self.public=base64.b64encode(self.raw).decode()
  new,_=self.enroll(old.pk);old.refresh_from_db()
  self.assertEqual(old.status,'REVOKED');self.assertEqual(new.replaces_id,old.pk);self.assertEqual(new.enrollment_method,'REVIEWED_RECOVERY');self.assertTrue(WalletDeviceCredential.objects.filter(pk=old.pk).exists())
  with transaction.atomic(),self.assertRaises(APIException):devices.active_device(self.owner,old.pk)
 def test_intermediate_attested_leaf_cannot_delegate_trust_to_software_key(self):
  original,chain=self.chain();attacker=ec.generate_private_key(ec.SECP256R1())
  forged=self.certificate(attacker,x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'forged fixture')]),original.subject,self.key,extension=description(self.nonce))
  raw=attacker.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)
  with self.assertRaises(AttestationRejected):self.verifier(self.device,raw,(forged.public_bytes(serialization.Encoding.DER),*chain))
 def test_duplicate_hardware_authorizations_rejected(self):
  fields=nodes(nodes(description(self.nonce))[0].value)
  encoded=[der((node.cls<<6)|(32 if node.constructed else 0)|node.tag,node.value) for node in fields[:7]]
  duplicate=seq(*encoded,der(0x30,fields[7].value+context(504,integer(2))))
  with self.assertRaises(AttestationRejected):self.verifier(self.device,self.raw,self.chain(duplicate)[1])
 def test_registered_device_without_live_verifier_or_fresh_feed_is_blocked(self):
  device,_=self.enroll()
  with override_settings(WALLET_ATTESTATION_VERIFIER=None),transaction.atomic(),self.assertRaises(APIException):devices.active_device(self.owner,device.pk)
  self.snapshot=replace(self.snapshot,valid_until=self.now-timedelta(seconds=1))
  with transaction.atomic(),self.assertRaises(APIException):devices.active_device(self.owner,device.pk)
 def new_pending_device(self):
  self.device,self.nonce_text=devices.begin_enrollment(self.owner);self.nonce=base64.b64decode(self.nonce_text)
  self.key=ec.generate_private_key(ec.SECP256R1());self.raw=self.key.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint);self.public=base64.b64encode(self.raw).decode()
 def test_failed_recovery_does_not_revoke_previous_device(self):
  old,_=self.enroll();self.new_pending_device();permit=self.permit(old.pk)
  _,chain=self.chain(description(secrets.token_bytes(32)))
  with self.assertRaises(APIException):devices.attest(self.owner,self.device.pk,self.public,[base64.b64encode(cert).decode() for cert in chain],permit)
  old.refresh_from_db();self.device.refresh_from_db();self.assertEqual(old.status,'VERIFIED');self.assertEqual(self.device.status,'PENDING')
 def test_database_failure_rolls_back_replacement_revocation(self):
  old,_=self.enroll();self.new_pending_device();new_id=self.device.pk;original=WalletDeviceCredential.save
  def fail_new(instance,*args,**kwargs):
   if instance.pk==new_id:raise RuntimeError('synthetic persistence failure')
   return original(instance,*args,**kwargs)
  with patch.object(WalletDeviceCredential,'save',fail_new),self.assertRaises(RuntimeError):self.enroll(old.pk)
  old.refresh_from_db();self.device.refresh_from_db();self.assertEqual(old.status,'VERIFIED');self.assertEqual(self.device.status,'PENDING')
 def test_cross_account_replacement_and_approval_are_rejected(self):
  other=CustomUser(username='other-recovery-'+uuid.uuid4().hex,role='BUSINESS_OWNER');CustomUser.objects.bulk_create([other])
  foreign,_=devices.begin_enrollment(other)
  with self.assertRaises(Http404):self.permit(foreign.pk)
  with override_settings(WALLET_ENROLLMENT_IDENTITY_VERIFIER=lambda *args:replace(self.identity_fixture(*args),user_id=other.pk)),self.assertRaises(APIException):self.permit()
 def test_operator_policy_files_pin_roots_and_refresh_revocations(self):
  from apps.wallet.services.attestation_config import load_android_verifier
  with tempfile.TemporaryDirectory() as temp:
   folder=Path(temp);root=folder/'root.der';root.write_bytes(self.root_der);feed=folder/'revocations.json';config=folder/'policy.json'
   value={'observed_at':self.snapshot.observed_at.isoformat(),'valid_until':self.snapshot.valid_until.isoformat(),'revoked_serial_numbers':[]};feed.write_text(json.dumps(value))
   policy={'trusted_roots':[{'path':str(root),'sha256':hashlib.sha256(self.root_der).hexdigest()}],'package_name':PKG,'signer_sha256':[SIGNER.hex()],'minimum_package_version':42,'minimum_os_version':120000,'minimum_patch_level':int(self.now.strftime('%Y%m')),'require_strongbox':True,'maximum_patch_age_days':90,'revocations_file':str(feed)};config.write_text(json.dumps(policy))
   verifier=load_android_verifier(str(config));leaf,chain=self.chain();self.assertTrue(verifier(self.device,self.raw,chain).hardware_biometric)
   value['revoked_serial_numbers']=[format(leaf.serial_number,'x')];feed.write_text(json.dumps(value))
   with self.assertRaises(AttestationRejected):verifier(self.device,self.raw,chain)
   root.write_bytes(b'root replaced')
   with self.assertRaises(AttestationRejected):load_android_verifier(str(config))
 def test_real_signature_protocol_rechecks_revocation_before_balance_change(self):
  device,leaf=self.enroll()
  other=CustomUser(username='attested-recipient-'+uuid.uuid4().hex,role='BUSINESS_OWNER');CustomUser.objects.bulk_create([other])
  source=Wallet.objects.create(user_id=self.owner.pk,owner_type='CORPORATIVO',owner_id=str(uuid.uuid4()),currency='COP',saldo_disponible='100')
  target=Wallet.objects.create(user_id=other.pk,owner_type='CORPORATIVO',owner_id=str(uuid.uuid4()),currency='COP')
  WalletLimiteOperativo.objects.create(wallet=source,monto_maximo_transaccion='40',monto_maximo_diario='60')
  def proof(intent,phase):
   challenge,message=devices.issue(self.owner,intent.pk,device.pk,phase)
   return {'challenge':challenge.pk,'signature':base64.b64encode(self.key.sign(message,ec.ECDSA(hashes.SHA256()))).decode()},challenge
  intent=transfers.prepare(self.owner,source.pk,target.pk,'5',uuid.uuid4());signed,_=proof(intent,'REVIEW');intent,token=transfers.review(self.owner,intent.pk,intent.digest,signed)
  signed,_=proof(intent,'EXECUTE');self.assertEqual(transfers.execute(self.owner,intent.pk,intent.digest,token,signed).state,'EXECUTED')
  intent=transfers.prepare(self.owner,source.pk,target.pk,'10',uuid.uuid4());signed,_=proof(intent,'REVIEW');intent,token=transfers.review(self.owner,intent.pk,intent.digest,signed)
  signed,challenge=proof(intent,'EXECUTE');self.snapshot=replace(self.snapshot,revoked_serials=frozenset({leaf.serial_number}))
  with self.assertRaises(APIException):transfers.execute(self.owner,intent.pk,intent.digest,token,signed)
  source.refresh_from_db();target.refresh_from_db();challenge.refresh_from_db()
  self.assertEqual((str(source.saldo_disponible),str(target.saldo_disponible)),('95.00','5.00'));self.assertIsNone(challenge.consumed_at)
 def test_hardware_flag_dictionary_is_rejected_even_with_valid_independent_permit(self):
  permit=self.permit();_,chain=self.chain()
  with override_settings(WALLET_ATTESTATION_VERIFIER=lambda *args:{'hardware_biometric':True}),self.assertRaises(APIException):devices.attest(self.owner,self.device.pk,self.public,[base64.b64encode(cert).decode() for cert in chain],permit)
  self.device.refresh_from_db();self.assertEqual(self.device.status,'PENDING')
 def test_http_activation_and_exact_permit_replay(self):
  client=APIClient(HTTP_HOST='localhost');client.force_authenticate(self.owner);_,chain=self.chain();permit=self.permit()
  endpoint='/api/v1/finance/wallet/devices/'+str(self.device.pk)+'/attest/'
  body={'public_key':self.public,'certificate_chain':[base64.b64encode(cert).decode() for cert in chain],'enrollment_authorization':permit}
  response=client.post(endpoint,body,format='json');self.assertEqual(response.status_code,200,response.content)
  self.assertEqual(response.json()['data']['status'],'VERIFIED');self.assertNotIn('enrollment_authorization',response.json()['data'])
  self.assertEqual(client.post(endpoint,body,format='json').status_code,403)
 def test_http_requires_authorization_and_cannot_issue_permits(self):
  client=APIClient(HTTP_HOST='localhost');client.force_authenticate(self.owner);_,chain=self.chain()
  base='/api/v1/finance/wallet/devices/'+str(self.device.pk)+'/'
  response=client.post(base+'attest/',{'public_key':self.public,'certificate_chain':[base64.b64encode(cert).decode() for cert in chain],'independent_verified':True},format='json')
  self.assertEqual(response.status_code,400)
  self.assertEqual(client.post(base+'authorize/',{'verified':True},format='json').status_code,404)

if __name__=='__main__':unittest.main()
