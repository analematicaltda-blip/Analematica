"""No-money lifecycle corrections for existing funded refunds; synthetic only."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_wallet_refund_check.py')),run_name='wallet_lifecycle_fixture')
from apps.prestadores.mi_negocio.gestion_comercial import wallet_refund_lifecycle as service,wallet_refund as refund
from apps.wallet.models import WalletTransferIntent,WalletDeviceChallenge,WalletDeviceCredential
from apps.wallet.services import internal_transfer,refund_guard
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
from django.utils import timezone
from rest_framework.exceptions import APIException
class LifecycleChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['WalletRefundChecks']();self.base.setUp();self.addCleanup(self.base.settings.disable);self.scope=self.base.scope;self.rid=self.base.rid;self.company=self.base.company;self.binding=self.base.prepare()['binding'];self.intent=WalletTransferIntent.objects.get(pk=self.binding['intent_id'])
 def expire(self):WalletTransferIntent.objects.filter(pk=self.intent.pk).update(expires_at=timezone.now()-timedelta(seconds=1))
 def review(self,action='CANCEL',**kw):return service.review_wallet_refund_lifecycle(**self.scope,**{'reservation_id':self.rid,'request_id':str(uuid.uuid4()),'action':action,'evidence_digest':'c'*64,'expected_revision':0,'confirmed':True,**kw})
 def confirm(self,r,**kw):return service.confirm_wallet_refund_lifecycle(**self.scope,reservation_id=self.rid,review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def state(self):return service.wallet_refund_lifecycle_state(**self.scope,reservation_id=self.rid)
 def test_cancel_has_no_balance_or_ledger_effect_and_is_terminal(self):
  count=JournalEntry.plain_objects.count();self.confirm(self.review());self.assertEqual(self.state()['status'],'CANCELLED');self.assertEqual(self.base.balances(),(100,0));self.assertEqual(count,JournalEntry.plain_objects.count())
  with self.assertRaises(APIException):self.base.review()
  with self.assertRaises(AccountingError):self.review('RENEW',expected_revision=1)
 def test_cancel_requires_two_separate_confirmations(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.confirm(r,confirmed=False)
 def test_renew_expired_intent_then_requires_two_new_financial_approvals(self):
  old=self.base.review()['confirmation'];self.expire();r=self.confirm(self.review('RENEW'));self.assertEqual(r['status'],'PENDING');self.assertFalse(r['financial_authorizations_restored']);self.intent.refresh_from_db();self.assertEqual(self.intent.confirmation_hash,'');self.assertIsNone(self.intent.reviewed_at)
  with self.assertRaises(APIException):self.base.execute(old)
  fresh=self.base.review()['confirmation'];result=self.base.execute(fresh);self.assertEqual(result['settlement']['amount'],'90.00');self.assertEqual(self.base.balances(),(10,90))
 def test_generic_cancel_cannot_bypass_accounting_lifecycle(self):
  with self.assertRaises(APIException):internal_transfer.cancel(self.base.actor,self.intent.pk,self.intent.digest,True)
  self.intent.refresh_from_db();self.assertEqual(self.intent.state,'PENDING')
 def test_generic_renew_cannot_replace_accounting_binding(self):
  self.expire()
  with self.assertRaises(APIException):internal_transfer.renew(self.base.actor,self.intent.pk,self.intent.digest,uuid.uuid4(),True)
  self.assertEqual(WalletTransferIntent.objects.filter(renewed_from=self.intent).count(),0)
 def test_active_intent_cannot_have_its_expiry_extended(self):
  with self.assertRaises(AccountingError):self.review('RENEW')
 def test_executed_intent_cannot_be_cancelled_or_renewed(self):
  self.base.execute(self.base.review()['confirmation'])
  for action in ['CANCEL','RENEW']:
   with self.assertRaises(AccountingError):self.review(action)
 def test_replay_is_idempotent_and_does_not_extend_expiry(self):
  self.expire();r=self.review('RENEW');a=self.confirm(r);b=self.confirm(r);self.assertTrue(b['replayed']);self.assertEqual(a['expires_at'],b['expires_at']);self.assertEqual(b['lifecycle_revision'],1)
 def test_old_native_challenges_are_invalidated_not_marked_as_used(self):
  c=WalletDeviceCredential.objects.create(user_id=self.base.actor.pk,audience=uuid.uuid4(),status='VERIFIED',enrollment_nonce_hash='0'*64,enrollment_expires_at=timezone.now()+timedelta(minutes=1));nonce=WalletDeviceChallenge.objects.create(credential=c,intent=self.intent,phase='REVIEW',nonce='a'*64,expires_at=timezone.now()+timedelta(minutes=5));self.expire();self.confirm(self.review('RENEW'));nonce.refresh_from_db();self.assertIsNotNone(nonce.invalidated_at);self.assertIsNone(nonce.consumed_at)
 def test_changed_intent_after_lifecycle_review_requires_new_review(self):
  r=self.review();self.base.review()
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_competing_lifecycle_reviews_cannot_overwrite(self):
  self.expire();renew=self.review('RENEW');cancel=self.review('CANCEL');self.confirm(renew)
  with self.assertRaises(AccountingError):self.confirm(cancel)
 def test_failure_to_record_lifecycle_rolls_back_reset(self):
  token=self.base.review()['confirmation'];self.expire();r=self.review('RENEW');self.intent.refresh_from_db();old=self.intent.confirmation_hash
  with patch.object(service.refund,'store',side_effect=AccountingError('Synthetic log failure')):
   with self.assertRaises(AccountingError):self.confirm(r)
  self.intent.refresh_from_db();self.assertEqual(self.intent.confirmation_hash,old);self.assertEqual(self.intent.state,'REVIEWED');self.assertLess(self.intent.expires_at,timezone.now())
 def test_cancel_can_stop_an_intent_even_if_contract_has_changed(self):
  from apps.domain_business.operativa.models import Reservation
  Reservation.plain_objects.filter(pk=self.rid).update(total_price='101.00');self.confirm(self.review());self.assertEqual(self.state()['status'],'CANCELLED')
 def test_renew_revalidates_funding_and_recipient(self):
  from apps.wallet.models import Wallet
  self.expire();Wallet.objects.filter(pk=self.base.source.pk).update(saldo_disponible='1.00')
  with self.assertRaises(AccountingError):self.review('RENEW')
 def test_stale_revision_is_rejected(self):
  self.expire();self.confirm(self.review('RENEW'))
  with self.assertRaises(AccountingError):self.review(expected_revision=0)
 def test_cancelled_effective_status_is_visible_in_wallet_api(self):
  from apps.wallet.serializers import TransferIntentSerializer
  self.confirm(self.review());self.assertEqual(TransferIntentSerializer(self.intent).data['state'],'CANCELLED')
 def test_deleted_cancel_marker_cannot_reactivate_transfer(self):
  self.confirm(self.review());OutboxEvent.objects.filter(pk=refund_guard.cancellation_id(self.intent.pk))._raw_delete('default')
  with self.assertRaises(APIException):internal_transfer.owned_intent(self.base.actor,self.intent.pk,self.intent.digest)
  with self.assertRaises(AccountingError):self.state()
 def test_foreign_owner_cannot_cancel_a_refund(self):
  with self.assertRaises(APIException):service.review_wallet_refund_lifecycle(actor=self.base.recipient,provider_id=self.base.provider.pk,reservation_id=self.rid,request_id=str(uuid.uuid4()),action='CANCEL',evidence_digest='e'*64,expected_revision=0,confirmed=True)
 def test_private_actual_api_contract(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_comercial.cancellation_views import CancellationPolicyCommand
  request=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),{'reservation_id':self.rid},format='json');force_authenticate(request,user=self.base.actor);r=CancellationPolicyCommand.as_view()(request,operation='wallet_refund_lifecycle_state');self.assertEqual(r.status_code,200,r.data);self.assertIn('no-store',r['Cache-Control']);self.assertEqual(r.data['lifecycle_revision'],0)
 def test_deleted_all_cancel_indexes_cannot_reactivate_terminal_model_state(self):
  self.confirm(self.review());OutboxEvent.objects.filter(event_type=service.RECORDED,payload__body__reservation_id=self.rid)._raw_delete('default');OutboxEvent.objects.filter(pk=refund_guard.cancellation_id(self.intent.pk))._raw_delete('default');self.intent.refresh_from_db();self.assertEqual(self.intent.state,'CANCELLED')
  with self.assertRaises(APIException):internal_transfer.owned_intent(self.base.actor,self.intent.pk,self.intent.digest)
 def test_expired_management_review_is_rejected(self):
  r=self.review()
  with patch.object(service.timezone,'now',return_value=timezone.now()+timedelta(minutes=16)):
   with self.assertRaises(AccountingError):self.confirm(r)
if __name__=='__main__':unittest.main()
