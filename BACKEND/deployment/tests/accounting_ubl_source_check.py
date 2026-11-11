"""Current-source authorization and immutable structural draft linkage."""
import copy,runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_fiscal_check.py')),run_name='ubl_source_fixture')
from apps.domain_business.comercial.services.reservation_fiscal import reviewed_ubl_source
from apps.domain_business.operativa.models import Reservation
from apps.core_erp.outbox_models import OutboxEvent
from apps.turismo.models import VerifiedCompanyLink
from django.utils import timezone
from rest_framework.exceptions import APIException
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
from app.services.ubl_source_contract import validate

class UblSourceTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['FiscalReservationTests']();self.case.setUp();self.review=self.case.review()
  self.args={**self.case.args,'review_id':self.review['review_id']}
 def source(self,**changes):return reviewed_ubl_source(**{**self.args,**changes})
 def test_source_exact_and_read_only_without_new_event(self):
  before=OutboxEvent.objects.count();r=self.source();self.assertEqual(r['snapshot']['totals'],{'net':'100.00','tax':'0.00','gross':'100.00'})
  self.assertEqual(r['review_id'],self.review['review_id']);self.assertEqual(OutboxEvent.objects.count(),before)
  self.assertTrue(r['read_only']);self.assertFalse(r['fiscal_accepted']);self.assertFalse(r['ledger_written'])
  validate(r,r['company_id'],{'reservation_id':str(self.case.case.reservation.pk),'review_id':r['review_id']})
 def test_changed_total_blocked(self):
  Reservation.plain_objects.filter(pk=self.case.case.reservation.pk).update(total_price='101.00')
  with self.assertRaises(APIException):self.source()
 def test_cancelled_source_blocked(self):
  Reservation.plain_objects.filter(pk=self.case.case.reservation.pk).update(status='CANCELLED')
  with self.assertRaises(APIException):self.source()
 def test_stale_revision_blocked(self):
  self.case.review(expected_revision=1)
  with self.assertRaises(APIException):self.source()
 def test_foreign_actor_blocked(self):
  with self.assertRaises(APIException):self.source(actor=fixture['fixture']['fixture']['F'].other)
 def test_revoked_company_blocked(self):
  VerifiedCompanyLink.objects.filter(provider=self.case.case.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.source()
 def test_missing_review_blocked(self):
  with self.assertRaises(APIException):self.source(review_id=uuid.uuid4())
 def test_contract_rejects_tampering_and_claimed_acceptance(self):
  r=self.source();params={'reservation_id':str(self.case.case.reservation.pk),'review_id':r['review_id']}
  for mutate in [lambda x:x['snapshot']['items'][0].update(net='99.00'),lambda x:x.update(fiscal_accepted=True),lambda x:x.update(company_id=str(uuid.uuid4())),lambda x:x.update(xml='secret'),lambda x:x['snapshot'].update(revision=True),lambda x:x.update(intent_digest='a'*64)]:
   bad=copy.deepcopy(r);mutate(bad)
   with self.assertRaises(ValueError):validate(bad,r['company_id'],params)
 def test_view_strict_query_and_current_authorized_source(self):
  params={'provider_id':str(self.case.case.provider.pk),'reservation_id':str(self.case.case.reservation.pk),'review_id':self.review['review_id']}
  def call(query):
   request=APIRequestFactory().get('/fixture/',query);force_authenticate(request,user=self.case.case.actor)
   return PlanCuentaViewSet.as_view({'get':'reviewed_ubl_source'})(request)
  self.assertEqual(call(params).status_code,200)
  self.assertEqual(call({**params,'snapshot':'spoof'}).status_code,400)
  self.assertEqual(call({**params,'review_id':[params['review_id'],params['review_id']]}).status_code,400)
  self.assertEqual(call({**params,'reservation_id':'invalid'}).status_code,400)
if __name__=='__main__':unittest.main()
