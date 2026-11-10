"""Actual funded wallet/ledger atomicity in disposable DB; no external money."""
import runpy,unittest,uuid
from pathlib import Path
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('cancellation_policy_check.py')),run_name='wallet_refund_fixture')
f=fixture
while 'create' not in f:f=f['fixture']
create=f['create']
from django.test import override_settings
from django.utils import timezone
from rest_framework.exceptions import APIException
from apps.prestadores.mi_negocio.gestion_comercial import wallet_refund as service
from apps.wallet.models import Wallet,WalletTransaccion,WalletMovimiento,WalletTransferIntent,WalletLimiteOperativo,WalletDeviceChallenge
from apps.wallet.services import internal_transfer,refund_guard
from apps.wallet.services.company_administrator import TourismCompanyAdministrator
from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
from apps.core_erp.fx.models import Currency,FXRateTable
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
for model in (Wallet,WalletTransaccion,WalletMovimiento,WalletTransferIntent,WalletLimiteOperativo,WalletDeviceChallenge,Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog,Currency,FXRateTable):create(model)
class WalletRefundChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['CancellationPolicyChecks']();self.base.setUp();self.scope=self.base.scope;self.company=self.base.company;self.provider=self.base.provider;self.rid=str(self.base.booking.pk);self.actor=self.scope['actor']
  self.base.bind(self.base.publish());self.base.confirm(self.base.review())
  chart=ChartOfAccounts.plain_objects.create(tenant=self.company,name='Synthetic refund chart');self.asset=Account.plain_objects.create(tenant=self.company,chart_of_accounts=chart,code='1109',name='Funded company wallet asset',type='ASSET');self.liability=Account.plain_objects.create(tenant=self.company,chart_of_accounts=chart,code='2380',name='Net customer refund obligation',type='LIABILITY');self.income=Account.plain_objects.create(tenant=self.company,chart_of_accounts=chart,code='4299',name='Previously reviewed commercial fee',type='REVENUE');day=timezone.localdate();self.period=FiscalPeriod.plain_objects.create(tenant=self.company,period_start=day,period_end=day,status='open')
  self.funding=LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=day,description='Synthetic pre-existing funded wallet and net refund liability',lines_data=[{'account':self.asset,'debit':'100.00'},{'account':self.liability,'credit':'90.00'},{'account':self.income,'credit':'10.00'}],actor=self.actor,idempotency_key='funding-'+self.rid);self.line=LedgerEntry.plain_objects.get(journal_entry=self.funding,account=self.liability)
  self.source=Wallet.objects.create(owner_type='CORPORATIVO',owner_id=str(self.company.pk),currency='COP',saldo_disponible='100.00',metadata={'accounting_asset_account_id':str(self.asset.pk)})
  from django.contrib.auth import get_user_model
  self.recipient=get_user_model().objects.filter(is_active=True).exclude(pk=self.actor.pk).first();self.dest=Wallet.objects.create(owner_type='TURISTA',owner_id=str(uuid.uuid4()),user_id=self.recipient.pk,currency='COP',metadata={'wallet_signup':True});WalletLimiteOperativo.objects.create(wallet=self.source,monto_maximo_transaccion='100.00',monto_maximo_diario='100.00')
  def verifier(company,customer,wallet):
   now=timezone.now();return service.VerifiedRefundBeneficiary(company_id=company.pk,customer_id=self.base.booking.customer_id,wallet_id=self.dest.pk,user_id=self.recipient.pk,reservation_id=self.base.booking.pk,accepts_wallet_refund=True,evidence_digest='f'*64,checked_at=now,valid_until=now+timedelta(minutes=2))
  verifier.wallet_id=lambda company,reservation:self.dest.pk
  self.settings=override_settings(WALLET_COMMERCIAL_REFUNDS_ENABLED=True,WALLET_INTERNAL_TRANSFERS_ENABLED=True,WALLET_DEVICE_APPROVALS_REQUIRED=False,WALLET_COMPANY_ADMIN_VERIFIER=TourismCompanyAdministrator(),WALLET_REFUND_BENEFICIARY_VERIFIER=verifier);self.settings.enable();self.addCleanup(self.settings.disable)
 def prepare(self,**kw):return service.prepare_wallet_refund(**self.scope,**{'reservation_id':self.rid,'source_wallet_id':str(self.source.pk),'destination_wallet_id':str(self.dest.pk),'liability_line_id':str(self.line.pk),'evidence_digest':'e'*64,'confirmed':True,**kw})
 def review(self,**kw):return service.review_wallet_refund(**self.scope,reservation_id=self.rid,device_proof=kw.get('device_proof'),confirmed=kw.get('confirmed',True))
 def execute(self,token,**kw):return service.execute_wallet_refund(**self.scope,reservation_id=self.rid,confirmation=token,device_proof=kw.get('device_proof'),confirmed=kw.get('confirmed',True))
 def balances(self):
  self.source.refresh_from_db();self.dest.refresh_from_db();return self.source.saldo_disponible,self.dest.saldo_disponible
 def test_funded_refund_moves_ninety_and_posts_balanced_company_journal(self):
  self.prepare();r=self.review();a=self.execute(r['confirmation']);self.assertEqual(self.balances(),(Decimal('10.00'),Decimal('90.00')));self.assertTrue(a['ledger_written']);self.assertTrue(a['money_transferred']);self.assertFalse(a['bank_transfer_executed']);j=JournalEntry.plain_objects.get(pk=a['settlement']['journal_id']);lines=list(LedgerEntry.plain_objects.filter(journal_entry=j));self.assertEqual(sum(l.debit_amount for l in lines),Decimal('90.00'));self.assertEqual(sum(l.credit_amount for l in lines),Decimal('90.00'));self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.wallet.views import WalletAccountViewSet,WalletTransactionViewSet
  req=APIRequestFactory().get('/fixture/');force_authenticate(req,user=self.recipient);response=WalletAccountViewSet.as_view({'get':'retrieve'})(req,pk=self.dest.pk);self.assertEqual(response.status_code,200,response.data);self.assertEqual(response.data['saldo_disponible'],'90.00')
  req=APIRequestFactory().get('/fixture/');force_authenticate(req,user=self.recipient);response=WalletTransactionViewSet.as_view({'get':'retrieve'})(req,pk=a['settlement']['transaction_id']);self.assertEqual(response.status_code,200,response.data);self.assertEqual(response.data['purpose'],'COMMERCIAL_REFUND');self.assertEqual(len(response.data['movimientos']),1)
 def test_generic_transfer_endpoint_cannot_skip_company_ledger(self):
  b=self.prepare()['binding'];r=self.review()
  with self.assertRaises(APIException):internal_transfer.execute(self.actor,b['intent_id'],b['intent_digest'],r['confirmation'])
  self.assertEqual(self.balances(),(Decimal('100.00'),Decimal('0.00')))
 def test_deleted_guard_never_frees_generic_execution(self):
  b=self.prepare()['binding'];r=self.review();OutboxEvent.objects.filter(pk=refund_guard.identity(b['intent_id']))._raw_delete('default')
  with self.assertRaises(APIException):internal_transfer.execute(self.actor,b['intent_id'],b['intent_digest'],r['confirmation'])
 def test_journal_failure_rolls_back_both_wallets_and_intent(self):
  b=self.prepare()['binding'];r=self.review()
  with patch.object(service.LedgerEngine,'post_lines',side_effect=AccountingError('Synthetic posting failure')):
   with self.assertRaises(AccountingError):self.execute(r['confirmation'])
  self.assertEqual(self.balances(),(Decimal('100.00'),Decimal('0.00')));self.assertEqual(WalletTransferIntent.objects.get(pk=b['intent_id']).state,'REVIEWED');self.assertFalse(WalletTransaccion.objects.filter(referencia_operativa='INTERNAL-'+b['intent_id']).exists())
 def test_replay_never_mints_or_double_posts(self):
  self.prepare();r=self.review();a=self.execute(r['confirmation']);count=JournalEntry.plain_objects.count();b=self.execute(r['confirmation']);self.assertTrue(b['replayed']);self.assertEqual(a['settlement'],b['settlement']);self.assertEqual(JournalEntry.plain_objects.count(),count);self.assertEqual(self.balances(),(Decimal('10.00'),Decimal('90.00')))
 def test_unreconciled_wallet_asset_balance_rejected(self):
  Wallet.objects.filter(pk=self.source.pk).update(saldo_disponible='99.00')
  with self.assertRaises(AccountingError):self.prepare()
 def test_missing_customer_identity_adapter_rejected(self):
  with override_settings(WALLET_REFUND_BENEFICIARY_VERIFIER=None):
   with self.assertRaises(APIException):self.prepare()
 def test_arbitrary_destination_is_rejected(self):
  other=Wallet.objects.create(owner_type='TURISTA',owner_id=str(uuid.uuid4()),user_id=self.actor.pk,currency='COP',metadata={'wallet_signup':True})
  with self.assertRaises(APIException):self.prepare(destination_wallet_id=str(other.pk))
 def test_first_and_second_financial_approval_are_required(self):
  self.prepare()
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.execute(r['confirmation'],confirmed=False)
 def test_native_device_requirement_is_not_bypassed(self):
  self.prepare()
  with override_settings(WALLET_DEVICE_APPROVALS_REQUIRED=True):
   with self.assertRaises(APIException):self.review()
  self.assertEqual(self.balances(),(Decimal('100.00'),Decimal('0.00')))
 def test_insufficient_available_wallet_never_mints_customer_credit(self):
  Wallet.objects.filter(pk=self.source.pk).update(saldo_disponible='10.00',saldo_bloqueado='90.00')
  with self.assertRaises(APIException):self.prepare()
 def test_closed_period_rolls_back_wallet_transfer(self):
  self.prepare();r=self.review();FiscalPeriod.plain_objects.filter(pk=self.period.pk).update(status='closed')
  with self.assertRaises(AccountingError):self.execute(r['confirmation'])
  self.assertEqual(self.balances(),(Decimal('100.00'),Decimal('0.00')))
 def test_state_recovery_restores_no_authorizations(self):
  self.prepare();r=self.review();self.execute(r['confirmation']);s=service.wallet_refund_state(**self.scope,reservation_id=self.rid);self.assertFalse(s['confirmations_restored']);self.assertTrue(s['read_only']);self.assertEqual(s['settlement']['amount'],'90.00')
 def test_employee_or_other_owner_cannot_credit_company_wallet(self):
  with self.assertRaises(APIException):service.prepare_wallet_refund(actor=self.recipient,provider_id=self.provider.pk,reservation_id=self.rid,source_wallet_id=str(self.source.pk),destination_wallet_id=str(self.dest.pk),liability_line_id=str(self.line.pk),evidence_digest='e'*64,confirmed=True)
 def test_changed_contract_blocks_wallet_transfer(self):
  from apps.domain_business.operativa.models import Reservation
  self.prepare();r=self.review();Reservation.plain_objects.filter(pk=self.rid).update(total_price='101.00')
  with self.assertRaises(AccountingError):self.execute(r['confirmation'])
 def test_deleted_consumption_proof_does_not_release_funding(self):
  self.prepare();r=self.review();self.execute(r['confirmation']);OutboxEvent.objects.filter(pk=service.policy.key(service.refund_liability.USED_SOURCE,self.company,str(self.line.pk)))._raw_delete('default')
  with self.assertRaises(AccountingError):service.refund_liability.source_line(self.company,str(self.line.pk),'90.00',timezone.localdate(),available=True)
 def test_default_disabled_and_cross_database_are_rejected(self):
  with override_settings(WALLET_COMMERCIAL_REFUNDS_ENABLED=False):
   with self.assertRaises(APIException):self.prepare()
  with patch.object(service.router,'db_for_write',return_value='wallet_remote'):
   with self.assertRaises(APIException):self.prepare()
 def test_refund_requires_customer_consent_for_this_booking(self):
  from dataclasses import replace
  from django.conf import settings
  original=settings.WALLET_REFUND_BENEFICIARY_VERIFIER
  for changes in [{'accepts_wallet_refund':False},{'reservation_id':uuid.uuid4()}]:
   with override_settings(WALLET_REFUND_BENEFICIARY_VERIFIER=lambda *args:replace(original(*args),**changes)):
    with self.assertRaises(APIException):self.prepare()
 def test_real_api_prep_and_two_authorizations_post_no_bank_movement(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_comercial.cancellation_views import CancellationPolicyCommand
  def call(op,data):
   r=APIRequestFactory().post('/fixture/?provider_id='+str(self.provider.pk),data,format='json');force_authenticate(r,user=self.actor);return CancellationPolicyCommand.as_view()(r,operation=op)
  prepared=call('prepare_wallet_refund',{'reservation_id':self.rid,'source_wallet_id':str(self.source.pk),'destination_wallet_id':str(self.dest.pk),'liability_line_id':str(self.line.pk),'evidence_digest':'e'*64,'confirmed':True});self.assertEqual(prepared.status_code,200,prepared.data);self.assertIn('no-store',prepared['Cache-Control'])
  reviewed=call('review_wallet_refund',{'reservation_id':self.rid,'device_proof':None,'confirmed':True});self.assertEqual(reviewed.status_code,200,reviewed.data)
  result=call('execute_wallet_refund',{'reservation_id':self.rid,'device_proof':None,'confirmation':reviewed.data['confirmation'],'confirmed':True});self.assertEqual(result.status_code,200,result.data);self.assertFalse(result.data['bank_transfer_executed']);self.assertTrue(result.data['ledger_written'])
 def test_catalog_selects_verified_recipient_without_private_balance(self):
  r=service.wallet_refund_sources(**self.scope,reservation_id=self.rid,after=None);self.assertEqual(r['destination_wallet_id'],str(self.dest.pk));self.assertEqual(r['source_wallets'][0]['available'],'100.00');self.assertEqual(r['liability_credits'][0]['line_id'],str(self.line.pk));self.assertNotIn('recipient_balance',r)
 def test_signed_device_approvals_and_atomic_retry_with_software_fixture(self):
  import base64
  from cryptography.hazmat.primitives.asymmetric import ec
  from cryptography.hazmat.primitives import hashes,serialization
  from apps.wallet.models import WalletDeviceCredential
  from apps.wallet.services import device_approvals as devices
  class ProtocolFixtureVerifier:
   def check_registered(self,credential):pass  # Laboratory signature contract, NOT attestation.
  key=ec.generate_private_key(ec.SECP256R1());audience=uuid.uuid4();public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)).decode();device=WalletDeviceCredential.objects.create(user_id=self.actor.pk,audience=audience,public_key=public,status='VERIFIED',enrollment_nonce_hash='0'*64,enrollment_expires_at=timezone.now()+timedelta(minutes=5),verified_at=timezone.now(),valid_until=timezone.now()+timedelta(days=1))
  b=self.prepare()['binding']
  with override_settings(WALLET_DEVICE_APPROVALS_REQUIRED=True,WALLET_APPROVAL_AUDIENCE=str(audience),WALLET_ATTESTATION_VERIFIER=ProtocolFixtureVerifier()):
   def proof(phase):
    c,message=devices.issue(self.actor,b['intent_id'],device.pk,phase);return {'challenge':str(c.pk),'signature':base64.b64encode(key.sign(message,ec.ECDSA(hashes.SHA256()))).decode()}
   r=self.review(device_proof=proof('REVIEW'));second=proof('EXECUTE')
   with patch.object(service.LedgerEngine,'post_lines',side_effect=AccountingError('Synthetic post failure')):
    with self.assertRaises(AccountingError):self.execute(r['confirmation'],device_proof=second)
   self.assertEqual(self.balances(),(Decimal('100.00'),Decimal('0.00')));self.execute(r['confirmation'],device_proof=second);self.assertEqual(self.balances(),(Decimal('10.00'),Decimal('90.00')))
 def test_missing_all_binding_indexes_cannot_downgrade_to_generic_transfer(self):
  b=self.prepare()['binding'];r=self.review();OutboxEvent.objects.filter(pk=refund_guard.identity(b['intent_id']))._raw_delete('default');OutboxEvent.objects.filter(pk=service.policy.key(service.BINDING,self.company,self.rid))._raw_delete('default')
  with self.assertRaises(APIException):internal_transfer.execute(self.actor,b['intent_id'],b['intent_digest'],r['confirmation'])
  self.assertEqual(self.balances(),(Decimal('100.00'),Decimal('0.00')))
 def test_client_cannot_prepare_a_reserved_refund_request_as_generic(self):
  with self.assertRaises(APIException):internal_transfer.prepare(self.actor,self.source.pk,self.dest.pk,'90.00',refund_guard.request_key(self.company.pk,self.rid))
if __name__=='__main__':unittest.main()
