"""ACC009 local-only increment; authentic DIAN acceptance is NOT certified here."""
import runpy,unittest,copy,uuid,sys
from pathlib import Path
from unittest.mock import patch
from datetime import date,datetime,timezone
f=runpy.run_path(str(Path(__file__).with_name('accounting_acc008_acceptance_check.py')),run_name='acc009_fixture')
from apps.domain_business.comercial.services import crm_fiscal as crm
from apps.comercial.models import Opportunity
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting import dian_readiness
from rest_framework.exceptions import APIException
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
from app.services.ubl_source_contract import validate
class ACC009Local(unittest.TestCase):
 def setUp(self):
  self.c=f['ACC008Acceptance']();self.c.setUp();self.c.bind();self.review=self.c.review();self.args={**self.c.args,'review_id':self.review['review_id']}
 def source(self,**extra):return crm.reviewed_crm_ubl_source(**{**self.args,**extra})
 def test_current_crm_source_is_readonly_not_issued_signed_or_accepted(self):
  before=OutboxEvent.objects.count();source=self.source();self.assertEqual(OutboxEvent.objects.count(),before);self.assertEqual(source['snapshot']['source_type'],'crm_opportunity');self.assertEqual(source['snapshot']['state'],'WON');self.assertFalse(source['fiscal_accepted']);self.assertFalse(source['identity_independently_verified'])
  validate(source,str(self.c.base.tenant.pk),{'opportunity_id':str(self.c.source.pk),'review_id':self.review['review_id']})
 def test_source_modified_amount_or_stage_requires_new_review(self):
  Opportunity.objects.filter(pk=self.c.source.pk).update(estimated_revenue='101.00')
  with self.assertRaises(APIException):self.source()
  Opportunity.objects.filter(pk=self.c.source.pk).update(estimated_revenue='100.00',stage='lost')
  with self.assertRaises(APIException):self.source()
 def test_stale_revision_cannot_build_current_fiscal_draft(self):
  self.c.review(expected_revision=1)
  with self.assertRaises(APIException):self.source()
 def test_revoked_reviewer_blocks_source_retrieval(self):
  type(self.c.base.operator).objects.filter(pk=self.c.base.operator.pk).update(is_superuser=False)
  with self.assertRaises(APIException):self.source()
 def test_crm_cannot_be_relabelled_reservation_or_fiscal_acceptance(self):
  source=self.source();params={'opportunity_id':str(self.c.source.pk),'review_id':self.review['review_id']}
  for key,value in [('fiscal_accepted',True),('identity_independently_verified',True),('intent_digest','0'*64)]:
   with self.assertRaises(ValueError):validate({**source,key:value},source['company_id'],params)
  with self.assertRaises(ValueError):validate(source,source['company_id'],{'reservation_id':str(self.c.source.pk),'review_id':self.review['review_id']})
 def test_crm_view_rejects_extra_and_duplicate_query_parameters(self):
  params={'provider_id':str(self.c.base.provider.pk),'opportunity_id':str(self.c.source.pk),'review_id':self.review['review_id']}
  def call(params):
   request=APIRequestFactory().get('/fixture/',params);force_authenticate(request,user=self.c.base.actor);return PlanCuentaViewSet.as_view({'get':'reviewed_crm_ubl_source'})(request)
  self.assertEqual(call(params).status_code,200);self.assertEqual(call({**params,'fiscal_accepted':True}).status_code,400);self.assertEqual(call({**params,'review_id':[self.review['review_id']]*2}).status_code,400)
 def profile(self):
  return {'company_id':str(self.c.base.tenant.pk),'supplier_nit':'900000001','resolution_number':'12345','prefix':'LAB','range_start':1,'range_end':100,'next_number':1,'valid_from':'2026-11-11','valid_until':'2026-11-11','environment':'HABILITACION','software_id':str(uuid.uuid4()),'test_set_id':'synthetic-not-official'}
 def test_resolution_uses_colombia_calendar_without_claiming_qualification(self):
  class Clock(datetime):
   @classmethod
   def now(cls,tz):return datetime(2026,11,12,1,tzinfo=timezone.utc).astimezone(tz)
  with patch.object(dian_readiness,'datetime',Clock):result=dian_readiness.inspect_readiness(self.c.base.tenant.pk,self.profile())
  self.assertTrue(result['public_configuration_valid']);self.assertFalse(result['ready_to_submit']);self.assertFalse(result['fiscal_accepted']);self.assertIn('AUTHENTIC_RECEIPT_VALIDATION_NOT_INTEGRATED',result['blocking_codes'])
 def test_noncanonical_resolution_dates_and_submission_remain_blocked(self):
  profile=self.profile();profile['valid_from']='20261111';result=dian_readiness.inspect_readiness(self.c.base.tenant.pk,profile,today=date(2026,11,11));self.assertIn('RESOLUTION_DATES_INVALID',result['blocking_codes'])
  with self.assertRaises(dian_readiness.DianIntegrationUnavailable):dian_readiness.block_unverified_submission(profile)
if __name__=='__main__':unittest.main()
