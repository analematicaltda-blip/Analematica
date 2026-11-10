"""Pool02 protocol tests. Software fixture keys are NOT hardware attestation evidence."""
import base64,hashlib,runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).resolve().parents[2]/'BACKEND/deployment/tests/provider_security_check.py'),run_name='fixture_setup')
from django.test import override_settings
from django.utils import timezone
from django.http import Http404
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes,serialization
from rest_framework.exceptions import APIException
from rest_framework.test import APIClient
from api.models import CustomUser
from apps.wallet.models import Wallet,WalletLimiteOperativo,WalletTransferIntent,WalletTransaccion,WalletMovimiento,WalletDeviceCredential,WalletDeviceChallenge
from apps.wallet.services import internal_transfer as transfers,device_approvals as devices
from apps.core_erp.outbox_models import OutboxEvent
for model in [OutboxEvent,CustomUser,WalletDeviceChallenge,WalletLimiteOperativo,WalletMovimiento]:fixture['create'](model)
# Real audit table and in-memory channel layer make slow-request coverage deterministic.
from apps.core_erp.models import EventAuditLog
from django.conf import settings
fixture['create'](EventAuditLog)
settings.CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}}
AUDIENCE='00000000-0000-0000-0000-000000000123'

class ProtocolFixtureVerifier:
 def check_registered(self,credential):pass  # Synthetic fixture, never a production adapter.
 def __call__(self,*args):raise AssertionError('Protocol fixtures cannot attest devices')

class DeviceChecks(unittest.TestCase):
 def setUp(self):
  setting=override_settings(WALLET_INTERNAL_TRANSFERS_ENABLED=True,WALLET_DEVICE_APPROVALS_REQUIRED=True,WALLET_DEVICE_ENROLLMENT_ENABLED=True,WALLET_APPROVAL_AUDIENCE=AUDIENCE,WALLET_ATTESTATION_VERIFIER=ProtocolFixtureVerifier())
  setting.enable();self.addCleanup(setting.disable)
  self.owner=CustomUser(username='device-owner-'+uuid.uuid4().hex,role='BUSINESS_OWNER')
  self.other=CustomUser(username='device-other-'+uuid.uuid4().hex,role='BUSINESS_OWNER')
  CustomUser.objects.bulk_create([self.owner,self.other])
  self.source=Wallet.objects.create(user_id=self.owner.pk,owner_type='TURISTA',metadata={'wallet_signup':True},owner_id=str(uuid.uuid4()),currency='COP',saldo_disponible='100')
  self.target=Wallet.objects.create(user_id=self.other.pk,owner_type='TURISTA',metadata={'wallet_signup':True},owner_id=str(uuid.uuid4()),currency='COP')
  WalletLimiteOperativo.objects.create(wallet=self.source,monto_maximo_transaccion='40',monto_maximo_diario='60')
  self.key=ec.generate_private_key(ec.SECP256R1())
  self.public=base64.b64encode(self.key.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)).decode()
  # Synthetic preverified record to isolate signature/transaction contracts. The
  # production enrollment API cannot create this state without a trusted verifier.
  self.device=WalletDeviceCredential.objects.create(user_id=self.owner.pk,audience=uuid.UUID(AUDIENCE),public_key=self.public,status='VERIFIED',enrollment_nonce_hash='0'*64,enrollment_expires_at=timezone.now()+timedelta(minutes=5),verified_at=timezone.now(),valid_until=timezone.now()+timedelta(days=1))
  self.intent=transfers.prepare(self.owner,self.source.pk,self.target.pk,'10',uuid.uuid4())
  transfers.consent(self.other,self.intent.pk,self.intent.digest,True)
 def proof(self,phase,intent=None,device=None,key=None):
  challenge,message=devices.issue(self.owner,(intent or self.intent).pk,(device or self.device).pk,phase)
  signature=(key or self.key).sign(message,ec.ECDSA(hashes.SHA256()))
  return {'challenge':challenge.pk,'signature':base64.b64encode(signature).decode()},challenge
 def balances(self):
  self.source.refresh_from_db();self.target.refresh_from_db();return self.source.saldo_disponible,self.target.saldo_disponible
 def review(self):
  proof,_=self.proof('REVIEW');return transfers.review(self.owner,self.intent.pk,self.intent.digest,proof)
 def test_signed_two_stage_flow_and_idempotent_receipt(self):
  intent,token=self.review();self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')))
  proof,challenge=self.proof('EXECUTE',intent)
  result=transfers.execute(self.owner,intent.pk,intent.digest,token,proof)
  self.assertEqual(self.balances(),(Decimal('90'),Decimal('10')))
  self.assertEqual(result.transaction_id,transfers.execute(self.owner,intent.pk,intent.digest,token,proof).transaction_id)
  self.assertEqual(WalletMovimiento.objects.filter(transaccion=result.transaction).count(),2)
  challenge.refresh_from_db();self.assertIsNotNone(challenge.consumed_at)
 def test_plain_biometric_flag_and_legacy_token_are_not_authorization(self):
  for proof in [None,{'biometric':True},{'challenge':str(uuid.uuid4()),'biometric_verified':True}]:
   with self.subTest(proof=proof),self.assertRaises(APIException):transfers.review(self.owner,self.intent.pk,self.intent.digest,proof)
  intent,token=self.review()
  with self.assertRaises(APIException):transfers.execute(self.owner,intent.pk,intent.digest,token)
  self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')))
 def test_first_signature_cannot_approve_second_stage(self):
  proof,_=self.proof('REVIEW');intent,token=transfers.review(self.owner,self.intent.pk,self.intent.digest,proof)
  with self.assertRaises(APIException):transfers.execute(self.owner,intent.pk,intent.digest,token,proof)
 def test_wrong_key_and_cross_intent_signature_rejected(self):
  proof,_=self.proof('REVIEW',key=ec.generate_private_key(ec.SECP256R1()))
  with self.assertRaises(APIException):transfers.review(self.owner,self.intent.pk,self.intent.digest,proof)
  proof,_=self.proof('REVIEW')
  other_intent=transfers.prepare(self.owner,self.source.pk,self.target.pk,'11',uuid.uuid4())
  with self.assertRaises(Http404):transfers.review(self.owner,other_intent.pk,other_intent.digest,proof)
 def test_changed_amount_requires_new_signature(self):
  proof,_=self.proof('REVIEW')
  digest=transfers.fingerprint(self.source.pk,self.target.pk,Decimal('11.00'),'COP')
  WalletTransferIntent.objects.filter(pk=self.intent.pk).update(amount='11.00',digest=digest)
  with self.assertRaises(APIException):transfers.review(self.owner,self.intent.pk,digest,proof)
 def test_expiration_and_replaced_challenge_rejected(self):
  old,old_challenge=self.proof('REVIEW');fresh,challenge=self.proof('REVIEW')
  with self.assertRaises(APIException):transfers.review(self.owner,self.intent.pk,self.intent.digest,old)
  WalletDeviceChallenge.objects.filter(pk=challenge.pk).update(expires_at=timezone.now()-timedelta(seconds=1))
  with self.assertRaises(APIException):transfers.review(self.owner,self.intent.pk,self.intent.digest,fresh)
 def test_revocation_and_wrong_service_audience_rejected(self):
  proof,_=self.proof('REVIEW')
  with override_settings(WALLET_APPROVAL_AUDIENCE=str(uuid.uuid4())),self.assertRaises(APIException):transfers.review(self.owner,self.intent.pk,self.intent.digest,proof)
  devices.revoke(self.owner,self.device.pk)
  with self.assertRaises(APIException):transfers.review(self.owner,self.intent.pk,self.intent.digest,proof)
 def test_approvals_cannot_switch_device(self):
  self.review()
  second=WalletDeviceCredential.objects.create(user_id=self.owner.pk,audience=uuid.UUID(AUDIENCE),public_key=self.public,status='VERIFIED',enrollment_nonce_hash='0'*64,enrollment_expires_at=timezone.now()+timedelta(minutes=5),valid_until=timezone.now()+timedelta(days=1))
  with self.assertRaises(APIException):devices.issue(self.owner,self.intent.pk,second.pk,'EXECUTE')
 def test_failed_ledger_rolls_back_proof_consumption(self):
  intent,token=self.review();proof,challenge=self.proof('EXECUTE')
  with patch.object(WalletMovimiento.objects,'create',side_effect=RuntimeError('synthetic write failure')):
   with self.assertRaises(RuntimeError):transfers.execute(self.owner,intent.pk,intent.digest,token,proof)
  challenge.refresh_from_db();self.assertIsNone(challenge.consumed_at)
  self.assertEqual(self.balances(),(Decimal('100'),Decimal('0')))
  self.assertEqual(transfers.execute(self.owner,intent.pk,intent.digest,token,proof).state,'EXECUTED')
 def test_enrollment_stays_pending_without_attestation_verifier(self):
  credential,nonce=devices.begin_enrollment(self.owner)
  self.assertEqual(hashlib.sha256(base64.b64decode(nonce)).hexdigest(),credential.enrollment_nonce_hash)
  with override_settings(WALLET_ATTESTATION_VERIFIER=None),self.assertRaises(APIException):devices.attest(self.owner,credential.pk,self.public,[base64.b64encode(b'not a certificate').decode()])
  credential.refresh_from_db();self.assertEqual(credential.status,'PENDING');self.assertFalse(credential.public_key)
  with self.assertRaises(APIException):devices.issue(self.owner,self.intent.pk,credential.pk,'REVIEW')
 def test_client_supplied_trust_dictionary_is_not_server_evidence(self):
  credential,_=devices.begin_enrollment(self.owner)
  with override_settings(WALLET_ATTESTATION_VERIFIER=lambda *args:{'hardware_biometric':True}),self.assertRaises(APIException):
   devices.attest(self.owner,credential.pk,self.public,[base64.b64encode(b'synthetic cert').decode()])
  credential.refresh_from_db();self.assertEqual(credential.status,'PENDING')
 def test_enrollment_http_does_not_accept_status_or_biometric_claims(self):
  client=APIClient(HTTP_HOST='localhost');client.force_authenticate(self.owner)
  base='/api/v1/finance/wallet/devices/'
  response=client.post(base,{'status':'VERIFIED','hardware_biometric':True,'public_key':self.public},format='json')
  self.assertEqual(response.status_code,201,response.content);self.assertEqual(response.json()['data']['device']['status'],'PENDING')
  device=response.json()['data']['device']['id']
  self.assertEqual(client.patch(base+device+'/',{'status':'VERIFIED'},format='json').status_code,405)
  client.force_authenticate(self.other)
  self.assertEqual(client.get(base+device+'/').status_code,404)
 def test_signed_http_review_and_execution(self):
  client=APIClient(HTTP_HOST='localhost');client.force_authenticate(self.owner)
  base='/api/v1/finance/wallet/transfers/'+str(self.intent.pk)+'/'
  token=None
  for phase,action in [('REVIEW','review'),('EXECUTE','execute')]:
   response=client.post(base+'challenge/',{'credential':str(self.device.pk),'phase':phase},format='json')
   self.assertEqual(response.status_code,200,response.content);data=response.json()['data']
   message=base64.b64decode(data['payload']);signature=base64.b64encode(self.key.sign(message,ec.ECDSA(hashes.SHA256()))).decode()
   body={'digest':self.intent.digest,'device_proof':{'challenge':data['challenge'],'signature':signature}}
   if token:body['confirmation']=token
   response=client.post(base+action+'/',body,format='json');self.assertEqual(response.status_code,200,response.content)
   self.assertEqual(response['Cache-Control'],'no-store')
   if phase=='REVIEW':token=response.json()['data']['confirmation']
  self.assertEqual(self.balances(),(Decimal('90'),Decimal('10')))

if __name__=='__main__':unittest.main()
