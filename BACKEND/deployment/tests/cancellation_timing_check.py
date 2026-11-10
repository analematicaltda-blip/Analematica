"""Cancellation calendar bands and blocked Bold orders; no external payments."""
import runpy,unittest,uuid,ast
from pathlib import Path
from datetime import timedelta,datetime,time,timezone as dt_timezone
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('cancellation_policy_check.py')),run_name='cancellation_timing_fixture')
from apps.prestadores.mi_negocio.gestion_comercial import cancellation_policies as service,refund_orders as refund
from apps.domain_business.operativa.models import Reservation
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
class TimingAndRefundChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['CancellationPolicyChecks']();self.base.setUp();self.scope=self.base.scope;self.booking=self.base.booking;self.tiers=[{'min_days_before':30,'percentage':'5.00'},{'min_days_before':15,'percentage':'10.00'},{'min_days_before':7,'percentage':'20.00'},{'min_days_before':0,'percentage':'40.00'}];self.config={**self.base.config,'percentage':'40.00','timing_tiers':self.tiers}
 def calculate(self,days,reason='STANDARD_CANCELLATION'):
  self.booking.start_date=timezone.localdate()+timedelta(days=days)
  return service.calculation(self.booking,self.config,'100.00',reason,timezone.now().isoformat())
 def saved_proposal(self):
  self.base.bind(self.base.publish());r=self.base.review();self.base.confirm(r)
 def review_refund(self,**kw):return refund.review_refund(**self.scope,**{'reservation_id':str(self.booking.pk),'request_id':str(uuid.uuid4()),'original_payment_reference':'synthetic-bold-payment','evidence_digest':'e'*64,'confirmed':True,**kw})
 def authorize(self,r,**kw):return refund.authorize_refund(**self.scope,reservation_id=str(self.booking.pk),review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def test_exact_boundaries_month_fifteen_seven_and_last_days(self):
  for days,pct in [(31,'5.00'),(30,'5.00'),(29,'10.00'),(15,'10.00'),(14,'20.00'),(7,'20.00'),(6,'40.00'),(0,'40.00')]:
   r=self.calculate(days);self.assertEqual(r['percentage'],pct);self.assertEqual(r['fee_amount'],pct);self.assertEqual(r['days_before_service'],days)
 def test_calendar_is_colombian_not_utc_date(self):
  at=datetime(2026,11,9,2,tzinfo=dt_timezone.utc);self.booking.start_date=at.date()+timedelta(days=6)
  with patch.object(service.timezone,'now',return_value=at+timedelta(minutes=1)):r=service.calculation(self.booking,self.config,'100.00','STANDARD_CANCELLATION',at.isoformat())
  self.assertEqual(r['days_before_service'],7);self.assertEqual(r['percentage'],'20.00')
 def test_exceptions_override_all_time_bands(self):
  for reason in ['STATUTORY_EXCEPTION','SUPPLIER_FAILURE','COMPANY_WAIVER']:self.assertEqual(self.calculate(0,reason)['fee_amount'],'0.00')
 def test_reject_ascending_duplicate_missing_zero_or_decreasing_rates(self):
  bad=[list(reversed(self.tiers)),self.tiers[:-1],[self.tiers[0],self.tiers[0],self.tiers[-1]],[self.tiers[0],{**self.tiers[-1],'percentage':'1.00'}]]
  for tiers in bad:
   with self.assertRaises(AccountingError):service.config({**self.config,'timing_tiers':tiers})
 def test_requires_actual_nonfuture_aware_timestamp_before_service(self):
  for at in [None,'2026-01-01T00:00:00',(timezone.now()+timedelta(days=1)).isoformat()]:
   with self.assertRaises(AccountingError):service.calculation(self.booking,self.config,'100.00','STANDARD_CANCELLATION',at)
  with self.assertRaises(AccountingError):self.calculate(-1)
 def test_time_policy_version_preserved_when_later_rates_change(self):
  Reservation.plain_objects.filter(pk=self.booking.pk).update(start_date=timezone.now()+timedelta(days=15),end_date=timezone.now()+timedelta(days=16));self.booking.refresh_from_db();p=self.base.publish(values=self.config);self.base.bind(p);r=self.base.review(cancellation_at=timezone.now().isoformat());self.assertEqual(r['preview']['calculation']['percentage'],'10.00');self.base.publish(policy_id=p['policy_id'],expected_revision=1,values={**self.config,'percentage':'50.00','timing_tiers':[{**t,'percentage':'50.00'} for t in self.tiers]});self.assertEqual(self.base.confirm(r)['calculation']['percentage'],'10.00')
 def test_explicit_cancellation_before_acceptance_is_rejected(self):
  p=self.base.publish(values=self.config);self.base.bind(p)
  with self.assertRaises(AccountingError):self.base.review(cancellation_at=(timezone.now()-timedelta(hours=1)).isoformat())
 def test_financial_order_is_blocked_not_paid_or_posted(self):
  self.saved_proposal();before=JournalEntry.plain_objects.count();r=self.review_refund();order=self.authorize(r);self.assertEqual(order['order']['amount'],'90.00');self.assertEqual(order['order']['status'],'BLOCKED_BOLD_VERIFICATION');self.assertIsNone(order['order']['journal_id']);self.assertFalse(order['money_transferred']);self.assertFalse(order['network_called']);self.assertEqual(before,JournalEntry.plain_objects.count())
 def test_financial_authorizations_are_separate_and_both_required(self):
  self.saved_proposal()
  with self.assertRaises(AccountingError):self.review_refund(confirmed=False)
  r=self.review_refund()
  with self.assertRaises(AccountingError):self.authorize(r,confirmed=False)
 def test_repeat_authorization_never_duplicates_financial_order(self):
  self.saved_proposal();r=self.review_refund();a=self.authorize(r);n=OutboxEvent.objects.count();b=self.authorize(r);self.assertEqual(a['order_id'],b['order_id']);self.assertTrue(b['replayed']);self.assertEqual(n,OutboxEvent.objects.count())
 def test_no_proposal_no_refund(self):
  with self.assertRaises(AccountingError):self.review_refund()
 def test_recovery_never_restores_payment_approval(self):
  self.saved_proposal();self.authorize(self.review_refund());r=refund.refund_state(**self.scope,reservation_id=str(self.booking.pk));self.assertFalse(r['confirmations_restored']);self.assertFalse(r['bank_receipt_verified']);self.assertTrue(r['read_only'])
 def test_legacy_bold_callback_cannot_approve_unverified_payload(self):
  file=Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND/app/services/payment_gateway_adapter.py';ns={'__name__':'bold_test','__file__':str(file)}
  with patch.dict('os.environ',{'BOLD_IDENTITY_KEY':'synthetic','BOLD_SECRET_KEY':'synthetic'}):exec(compile(file.read_text(),str(file),'exec'),ns)
  with self.assertRaises(ValueError):ns['BoldPaymentGateway']('test','test').validar_webhook_confirmacion({'reference':'unverified'},'fake')
 def test_expired_financial_review_cannot_authorize_an_order(self):
  self.saved_proposal();r=self.review_refund()
  with patch.object(refund.timezone,'now',return_value=timezone.now()+timedelta(minutes=16)):
   with self.assertRaises(AccountingError):self.authorize(r)
  self.assertFalse(OutboxEvent.objects.filter(event_type=refund.ORDER).exists())
 def test_null_tiers_and_disagreement_with_last_band_rejected(self):
  for c in [{**self.config,'timing_tiers':None},{**self.config,'percentage':'1.00'}]:
   with self.assertRaises(AccountingError):service.config(c)
 def test_changed_contract_blocks_financial_confirmation(self):
  self.saved_proposal();r=self.review_refund();Reservation.plain_objects.filter(pk=self.booking.pk).update(total_price='101.00')
  with self.assertRaises(AccountingError):self.authorize(r)
 def test_foreign_owner_cannot_recover_a_refund_order(self):
  from django.contrib.auth import get_user_model
  other=get_user_model().objects.filter(is_active=True).exclude(pk=self.scope['actor'].pk).first();self.saved_proposal();self.authorize(self.review_refund())
  with self.assertRaises(PermissionDenied):refund.refund_state(actor=other,provider_id=self.scope['provider_id'],reservation_id=str(self.booking.pk))
 def test_zero_net_does_not_create_zero_value_bank_order(self):
  self.base.bind(self.base.publish(values={**self.base.config,'percentage':'100.00'}));self.base.confirm(self.base.review())
  with self.assertRaises(AccountingError):self.review_refund()
 def test_refund_evidence_tamper_is_rejected_on_recovery(self):
  self.saved_proposal();r=self.review_refund();self.authorize(r);row=OutboxEvent.objects.get(pk=r['review_id']);row.payload['body']['amount']='0.01';OutboxEvent.objects.filter(pk=row.pk).update(payload=row.payload)
  with self.assertRaises(AccountingError):refund.refund_state(**self.scope,reservation_id=str(self.booking.pk))
if __name__=='__main__':unittest.main()
