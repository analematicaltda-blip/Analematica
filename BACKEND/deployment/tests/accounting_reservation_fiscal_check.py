"""Authorized persisted reservation review and transactional invoice request."""
import runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from django.db import transaction
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_source_check.py')),run_name='fiscal_source_fixture')
from apps.domain_business.comercial.services.reservation_fiscal import review_reservation,request_reservation_invoice,list_reservation_sources,REVIEW_EVENT
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.invoice_queue import EVENT_TYPE
from apps.domain_business.operativa.models import Reservation
from apps.turismo.models import VerifiedCompanyLink
from rest_framework.exceptions import APIException
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class FiscalReservationTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['ReservationSourceTests']();self.case.setUp();self.case.confirm()
  self.args={'actor':self.case.actor,'provider_id':self.case.provider.pk,'reservation_id':self.case.reservation.pk}
  self.items=[{'item_id':str(uuid.uuid4()),'net':'100.00','tax':'0.00','tax_category':'EXCLUDED','policy_reference':'human-reviewed-fixture:1'}]
 def review(self,**extra):
  args={**self.args,'items':self.items,'evidence_digest':'b'*64,'confirmed':True,'expected_revision':0};args.update(extra)
  return review_reservation(**args)
 def submit(self,review):return request_reservation_invoice(**self.args,review_id=review['review_id'],confirmed=True)
 def test_complete_review_request_and_replay_from_persisted_source(self):
  review=self.review();a=self.submit(review);b=self.submit(review)
  self.assertFalse(a['replayed']);self.assertTrue(b['replayed']);self.assertTrue(a['source_authority_verified'])
  self.assertFalse(a['legal_tax_policy_verified']);self.assertFalse(a['fiscal_accepted']);self.assertFalse(a['ledger_written'])
  self.assertEqual(OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(self.case.reservation.pk)).count(),1)
 def test_second_confirmation_required_and_review_reference_persisted(self):
  review=self.review()
  with self.assertRaises(APIException):request_reservation_invoice(**self.args,review_id=review['review_id'],confirmed=False)
  result=self.submit(review);payload=OutboxEvent.objects.get(pk=result['outbox_id']).payload
  self.assertEqual(payload['source_review']['review_id'],review['review_id'])
  self.assertEqual(payload['source_review']['intent_digest'],payload['intent']['payload_digest'])
 def test_gross_mismatch_rejected_without_review(self):
  self.items[0]['net']='99.00'
  with self.assertRaises(APIException):self.review()
  self.assertFalse(OutboxEvent.objects.filter(event_type=REVIEW_EVENT,aggregate_root=str(self.case.reservation.pk)).exists())
 def test_source_change_blocks_submission(self):
  review=self.review();Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(total_price='101.00')
  with self.assertRaises(APIException):self.submit(review)
 def test_revocation_and_foreign_actor_cannot_review(self):
  with self.assertRaises(APIException):self.review(actor=fixture['fixture']['F'].other)
  VerifiedCompanyLink.objects.filter(provider=self.case.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.review()
 def test_pending_source_cannot_review(self):
  Reservation.plain_objects.filter(pk=self.case.reservation.pk).update(status='PENDING')
  with self.assertRaises(APIException):self.review()
 def test_review_conflict_and_stale_submission(self):
  first=self.review()
  with self.assertRaises(APIException):self.review()
  second=self.review(expected_revision=1)
  with self.assertRaises(APIException):self.submit(first)
  self.assertEqual(self.submit(second)['revision'],2)
 def test_no_new_revision_after_invoice_request(self):
  first=self.review();self.submit(first)
  with self.assertRaises(APIException):self.review(expected_revision=1)
 def test_review_outer_rollback(self):
  with self.assertRaises(RuntimeError):
   with transaction.atomic():self.review();raise RuntimeError('Rollback')
  self.assertFalse(OutboxEvent.objects.filter(event_type=REVIEW_EVENT,aggregate_root=str(self.case.reservation.pk)).exists())
 def test_request_failure_preserves_review_without_request(self):
  first=self.review()
  with patch.object(OutboxEvent.objects,'create',side_effect=RuntimeError('Write failed')):
   with self.assertRaises(RuntimeError):self.submit(first)
  self.assertTrue(OutboxEvent.objects.filter(pk=first['review_id']).exists())
  self.assertFalse(OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(self.case.reservation.pk)).exists())
 def test_sources_are_scoped_and_include_review_state(self):
  review=self.review();result=list_reservation_sources(actor=self.case.actor,provider_id=self.case.provider.pk)
  self.assertEqual(result['sources'][0]['review_id'],review['review_id']);self.assertEqual(result['sources'][0]['revision'],1)
  self.assertFalse(result['sources'][0]['request_created']);self.submit(review)
  self.assertTrue(list_reservation_sources(actor=self.case.actor,provider_id=self.case.provider.pk)['sources'][0]['request_created'])
 def test_real_view_flow_and_spoofed_snapshot_rejected(self):
  def call(action,body,user=None,method='post'):
   request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.case.provider.pk),body,format='json');force_authenticate(request,user=user or self.case.actor)
   return PlanCuentaViewSet.as_view({method:action})(request)
  body={'reservation_id':str(self.case.reservation.pk),'items':self.items,'evidence_digest':'b'*64,'confirmed':True,'expected_revision':0}
  self.assertEqual(call('review_reservation_fiscal',{**body,'reservation_id':'invalid-uuid'}).status_code,400)
  review=call('review_reservation_fiscal',body);self.assertEqual(review.status_code,201,review.data)
  payload={'reservation_id':body['reservation_id'],'review_id':review.data['review_id'],'confirmed':True}
  self.assertEqual(call('request_reservation_invoice',{**payload,'snapshot':{}}).status_code,400)
  self.assertEqual(call('request_reservation_invoice',payload).status_code,201)
  self.assertEqual(call('request_reservation_invoice',payload).status_code,200)
if __name__=='__main__':unittest.main()
