"""Local funded refunds, consent and expiry lifecycle; no bank/provider execution."""
import runpy,unittest,uuid,copy
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
from decimal import Decimal
fixture=runpy.run_path(str(Path(__file__).resolve().parents[3]/'BACKEND/deployment/tests/accounting_native_purchase_check.py'),run_name='funded_refund_fixture')
from django.test import override_settings
from django.utils import timezone
from rest_framework.exceptions import APIException
from django.http import Http404
from apps.wallet.models import Wallet, WalletLimiteOperativo, WalletTransferIntent, WalletMovimiento, WalletTransaccion, WalletDeviceChallenge
from apps.wallet.services import internal_transfer as transfers, funded_refund as refunds
from apps.wallet.services.access_policy import VerifiedCompanyAdministrator
from apps.core_erp.accounting.return_policy import quote
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
for model in (WalletDeviceChallenge,WalletMovimiento,WalletLimiteOperativo):fixture['create'](model)

class RecoveryChecks(unittest.TestCase):
 def new_customer(self):
  from api.models import CustomUser
  user=CustomUser(username='wallet-person-'+uuid.uuid4().hex,role='TURISTA');CustomUser.objects.bulk_create([user]);return user
 def setUp(self):
  self.base=fixture['NativePurchaseChecks']();self.base.setUp();self.owner=self.base.actor;self.customer=self.new_customer()
  self.provider=self.base.provider;self.company=self.base.company
  self.source=Wallet.objects.create(owner_type='CORPORATIVO',owner_id=str(self.provider.pk),currency='COP')
  self.destination=Wallet.objects.create(user_id=self.customer.pk,owner_type='TURISTA',owner_id=str(uuid.uuid4()),metadata={'wallet_signup':True},currency='COP',saldo_disponible='200')
  def verifier(user,wallet):
   if user.pk==self.owner.pk and wallet.pk==self.source.pk:
    return VerifiedCompanyAdministrator(user.pk,wallet.pk,wallet.owner_id,'ERP_TUR','COMPANY_ADMINISTRATOR','a'*64,timezone.now(),timezone.now()+timedelta(minutes=1))
  verifier.wallet_ids=lambda user:[self.source.pk] if user.pk==self.owner.pk else []
  setting=override_settings(WALLET_INTERNAL_TRANSFERS_ENABLED=True,WALLET_DEVICE_APPROVALS_REQUIRED=False,WALLET_COMPANY_ADMIN_VERIFIER=verifier);setting.enable();self.addCleanup(setting.disable)
  for wallet in (self.source,self.destination):WalletLimiteOperativo.objects.create(wallet=wallet,monto_maximo_transaccion='200',monto_maximo_diario='500')
  original=transfers.prepare(self.customer,self.destination.pk,self.source.pk,'100',uuid.uuid4());transfers.consent(self.owner,original.pk,original.digest,True);original,token=transfers.review(self.customer,original.pk,original.digest);self.original=transfers.execute(self.customer,original.pk,original.digest,token)
  day=timezone.localdate();self.policy={'code':'DECLARED','version':'v1','valid_from':day.replace(month=1,day=1).isoformat(),'valid_until':day.replace(month=12,day=31).isoformat(),'tiers':[{'minimum_days':0,'refund_bps':0},{'minimum_days':7,'refund_bps':10000}],'evidence_digest':'b'*64}
  self.args={'provider_id':self.provider.pk,'original_intent_id':self.original.pk,'source_id':self.source.pk,'destination_id':self.destination.pk,'amount':'40','key':uuid.uuid4(),'policy':self.policy,'scheduled_date':(day+timedelta(days=7)).isoformat(),'debit_account_id':str(self.base.case.payable.pk),'credit_account_id':str(self.base.case.base.asset.pk)}
 def prepare(self,**kw):return refunds.prepare(self.owner,**{**self.args,**kw})
 def approve(self,intent,consent=True):
  if consent:transfers.consent(self.customer,intent.pk,intent.digest,True)
  return transfers.review(self.owner,intent.pk,intent.digest)
 def execute(self,intent,token):return transfers.execute(self.owner,intent.pk,intent.digest,token)
 def balances(self):
  self.source.refresh_from_db();self.destination.refresh_from_db();return self.source.saldo_disponible,self.destination.saldo_disponible
 def test_funded_refund_atomic_journal_and_idempotency(self):
  a=self.prepare();self.assertEqual(a.pk,self.prepare().pk);a,token=self.approve(a);result=self.execute(a,token);self.assertEqual(self.balances(),(Decimal('60'),Decimal('140')))
  tx=result.transaction;self.assertEqual(tx.metadata['kind'],'FUNDED_REFUND_V1');journal=JournalEntry.plain_objects.get(pk=tx.metadata['journal_id']);self.assertTrue(journal.is_posted);self.assertEqual(journal.compute_hash(),journal.system_hash);self.assertEqual(result.transaction_id,self.execute(a,token).transaction_id)
 def test_recipient_consent_required_and_foreign_actor_denied(self):
  a=self.prepare();a,token=self.approve(a,False)
  with self.assertRaises(APIException):self.execute(a,token)
  with self.assertRaises(Http404):transfers.consent(self.owner,a.pk,a.digest,True)
  with self.assertRaises(APIException):transfers.consent(self.customer,a.pk,'f'*64,True)
  transfers.consent(self.customer,a.pk,a.digest,True);self.execute(a,token)
 def test_no_money_creation_or_duplicate_refund(self):
  a,token=self.approve(self.prepare(amount='60'));self.execute(a,token)
  with self.assertRaises(APIException):self.prepare(amount='50',key=uuid.uuid4())
  self.source.saldo_disponible=Decimal('1');self.source.save()
  with self.assertRaises(APIException):self.prepare(amount='2',key=uuid.uuid4())
 def test_accounting_failure_rolls_back_balances_movements_and_intent(self):
  a,token=self.approve(self.prepare());before=(WalletMovimiento.objects.count(),WalletTransaccion.objects.count(),JournalEntry.plain_objects.count())
  with patch('apps.core_erp.accounting.ledger_engine.LedgerEngine.post_lines',side_effect=RuntimeError('Synthetic journal failure')):
   with self.assertRaises(RuntimeError):self.execute(a,token)
  self.assertEqual(self.balances(),(Decimal('100'),Decimal('100')));a.refresh_from_db();self.assertEqual(a.state,'REVIEWED');self.assertIsNone(a.transaction_id);self.assertEqual(before,(WalletMovimiento.objects.count(),WalletTransaccion.objects.count(),JournalEntry.plain_objects.count()))
 def test_cancel_invalidates_authorizations(self):
  a,token=self.approve(self.prepare());transfers.cancel(self.owner,a.pk,a.digest,True)
  with self.assertRaises(APIException):self.execute(a,token)
  self.assertEqual(self.balances(),(Decimal('100'),Decimal('100')))
 def test_expired_renewal_needs_new_consent_and_two_new_approvals(self):
  a,token=self.approve(self.prepare());WalletTransferIntent.objects.filter(pk=a.pk).update(expires_at=timezone.now()-timedelta(seconds=1));key=uuid.uuid4()
  fresh=transfers.renew(self.owner,a.pk,a.digest,key,True);self.assertNotEqual(fresh.pk,a.pk);self.assertEqual(fresh.purpose,a.purpose);self.assertFalse(fresh.consent_digest);self.assertFalse(fresh.confirmation_hash);self.assertIsNone(fresh.review_device_id)
  with self.assertRaises(APIException):self.execute(fresh,token)
  self.assertEqual(fresh.pk,transfers.renew(self.owner,a.pk,a.digest,key,True).pk)
  fresh,new_token=self.approve(fresh);self.execute(fresh,new_token)
 def test_renewal_keeps_original_economic_request_date(self):
  a=self.prepare();original=copy.deepcopy(a.purpose)
  WalletTransferIntent.objects.filter(pk=a.pk).update(expires_at=timezone.now()-timedelta(seconds=1))
  later=timezone.localdate()+timedelta(days=2)
  with patch('apps.wallet.services.internal_transfer.timezone.localdate',return_value=later):
   fresh=transfers.renew(self.owner,a.pk,a.digest,uuid.uuid4(),True)
  self.assertEqual(fresh.purpose,original);self.assertFalse(fresh.consent_digest);self.assertFalse(fresh.confirmation_hash)
 def test_cannot_renew_live_or_executed_intents(self):
  a=self.prepare()
  with self.assertRaises(APIException):transfers.renew(self.owner,a.pk,a.digest,uuid.uuid4(),True)
  a,token=self.approve(a);self.execute(a,token)
  with self.assertRaises(APIException):transfers.cancel(self.owner,a.pk,a.digest,True)
 def test_policy_thresholds_and_fractional_cents(self):
  day=timezone.localdate();scheduled=(day+timedelta(days=7)).isoformat();r=quote(self.policy,paid='100.00',scheduled_date=scheduled,requested_date=day.isoformat());self.assertEqual(r['maximum_refund'],'100.00')
  r=quote(self.policy,paid='100.00',scheduled_date=(day+timedelta(days=6)).isoformat(),requested_date=day.isoformat());self.assertEqual(r['maximum_refund'],'0.00')
  p=copy.deepcopy(self.policy);p['tiers'][1]['refund_bps']=3333
  with self.assertRaises(AccountingError):quote(p,paid='0.01',scheduled_date=scheduled,requested_date=day.isoformat())
 def test_generic_prepare_cannot_downgrade_refund_purpose(self):
  a=self.prepare()
  with self.assertRaises(APIException):transfers.prepare(self.owner,self.source.pk,self.destination.pk,'40',a.idempotency_key)
 def test_replay_rejects_tampered_accounting_origin(self):
  a,token=self.approve(self.prepare());result=self.execute(a,token);tx=result.transaction;tx.metadata['journal_id']=str(uuid.uuid4());tx.save(update_fields=['metadata'])
  with self.assertRaises(APIException):self.execute(a,token)
 def test_execution_rechecks_existing_funds(self):
  a,token=self.approve(self.prepare());Wallet.objects.filter(pk=self.source.pk).update(saldo_disponible='1.00')
  with self.assertRaises(APIException):self.execute(a,token)
  self.assertIsNone(WalletTransferIntent.objects.get(pk=a.pk).transaction_id)
 def test_recovery_http_consent_cancel_and_private_state(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.wallet.views import WalletTransferViewSet
  a=self.prepare()
  def call(action,user,body):
   req=APIRequestFactory().post('/fixture/',body,format='json');force_authenticate(req,user=user);return WalletTransferViewSet.as_view({'post':action})(req,pk=str(a.pk))
  self.assertEqual(call('consent',self.owner,{'digest':a.digest,'confirmed':True}).status_code,404)
  r=call('consent',self.customer,{'digest':a.digest,'confirmed':True});self.assertEqual(r.status_code,200,r.data);self.assertIn('no-store',r['Cache-Control'])
  r=call('cancel',self.owner,{'digest':a.digest,'confirmed':True});self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['state'],'CANCELLED')
 def test_funded_refund_two_signed_device_approvals(self):
  import base64,hashlib
  from cryptography.hazmat.primitives.asymmetric import ec
  from cryptography.hazmat.primitives import serialization,hashes
  from apps.wallet.models import WalletDeviceCredential
  from apps.wallet.services import device_approvals as devices
  class FixtureVerifier:
   def check_registered(self,credential):pass
  audience=uuid.uuid4();key=ec.generate_private_key(ec.SECP256R1())
  device=WalletDeviceCredential.objects.create(user_id=self.owner.pk,audience=audience,public_key=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)).decode(),status='VERIFIED',enrollment_nonce_hash='a'*64,enrollment_expires_at=timezone.now()+timedelta(minutes=5),verified_at=timezone.now(),valid_until=timezone.now()+timedelta(days=1))
  with override_settings(WALLET_DEVICE_APPROVALS_REQUIRED=True,WALLET_APPROVAL_AUDIENCE=str(audience),WALLET_ATTESTATION_VERIFIER=FixtureVerifier()):
   intent=self.prepare();transfers.consent(self.customer,intent.pk,intent.digest,True)
   def proof(phase):
    challenge,message=devices.issue(self.owner,intent.pk,device.pk,phase)
    return {'challenge':challenge.pk,'signature':base64.b64encode(key.sign(message,ec.ECDSA(hashes.SHA256()))).decode()}
   intent,token=transfers.review(self.owner,intent.pk,intent.digest,proof('REVIEW'))
   with self.assertRaises(APIException):self.execute(intent,token)
   result=transfers.execute(self.owner,intent.pk,intent.digest,token,proof('EXECUTE'));self.assertIsNotNone(result.transaction_id)
 def test_migration_preserves_old_money_and_requires_new_consent(self):
  from django.db import connections
  from django.db.migrations.state import ProjectState
  import importlib
  alias='refund_migration_fixture'
  connections.databases[alias]={**connections['default'].settings_dict,'NAME':':memory:'}
  db=connections[alias];state=ProjectState()
  try:
   names=['0001_initial','0002_wallet_currency_wallettransferintent','0003_walletdevicecredential_walletdevicechallenge_and_more','0004_device_trust_and_independent_enrollment']
   for name in names:
    migration=importlib.import_module('fresh_migrations.wallet.'+name).Migration(name,'wallet')
    with db.schema_editor() as editor:state=migration.apply(state,editor)
   old_wallet=state.apps.get_model('wallet','Wallet');old_intent=state.apps.get_model('wallet','WalletTransferIntent')
   source=old_wallet.objects.using(alias).create(owner_type='TURISTA',owner_id='historical-source',currency='COP',saldo_disponible='57.00')
   dest=old_wallet.objects.using(alias).create(owner_type='TURISTA',owner_id='historical-target',currency='COP')
   intent=old_intent.objects.using(alias).create(requested_by_id=1,idempotency_key=uuid.uuid4(),source_id=source.pk,destination_id=dest.pk,amount='7.00',currency='COP',digest='a'*64,state='REVIEWED',confirmation_hash='b'*64,expires_at=timezone.now()+timedelta(minutes=5))
   migration=importlib.import_module('fresh_migrations.wallet.0005_consent_refund_lifecycle').Migration('0005','wallet')
   with db.schema_editor() as editor:state=migration.apply(state,editor)
   current=state.apps.get_model('wallet','WalletTransferIntent').objects.using(alias).get(pk=intent.pk)
   self.assertIsNone(current.consent_at);self.assertEqual(current.consent_digest,'');self.assertEqual(current.purpose,{});self.assertEqual(current.confirmation_hash,'b'*64)
   self.assertEqual(state.apps.get_model('wallet','Wallet').objects.using(alias).get(pk=source.pk).saldo_disponible,Decimal('57.00'))
  finally:
   db.close();del connections[alias];connections.databases.pop(alias,None)
if __name__=='__main__' :unittest.main()
