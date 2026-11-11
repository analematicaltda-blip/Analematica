"""ACC008 persisted CRM ownership, real source state and no invented payment/receipt."""
import runpy,unittest,uuid,copy
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
f=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_fiscal_check.py')),run_name='acc008_fixture')
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException
from apps.comercial.models import Lead,Opportunity
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_queue import EVENT_TYPE
from apps.domain_business.comercial.services import crm_fiscal as crm
from apps.domain_business.comercial.services import reservation_fiscal as reservation
for model in [Lead,Opportunity]:f['fixture']['fixture']['fixture']['create'](model)
class ACC008Acceptance(unittest.TestCase):
 def setUp(self):
  self.c=f['FiscalReservationTests']();self.c.setUp();self.base=self.c.case
  self.lead=Lead.objects.create(name='Synthetic lead',email=uuid.uuid4().hex+'@example.test')
  self.source=Opportunity.objects.create(lead=self.lead,stage=Opportunity.Stage.WON,estimated_revenue='100.00')
  self.args={'actor':self.base.actor,'provider_id':self.base.provider.pk,'opportunity_id':self.source.pk}
 def bind(self,**extra):
  args={'operator':self.base.operator,'provider_id':self.base.provider.pk,'opportunity_id':self.source.pk,'evidence_digest':'c'*64,'valid_until':timezone.now()+timedelta(days=1),'apply':True};args.update(extra);return crm.bind_crm_source(**args)
 def review(self,**extra):
  args={**self.args,'items':self.c.items,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True};args.update(extra);return crm.review_crm_invoice(**args)
 def request(self,review,**extra):
  args={**self.args,'review_id':review['review_id'],'confirmed':True};args.update(extra);return crm.request_crm_invoice(**args)
 def assert_no_money(self,result):
  for key in crm.FLAGS:self.assertIs(result[key],False)
 def test_unbound_crm_uuid_is_not_company_authority(self):
  with self.assertRaises(APIException):self.review()
  self.assertFalse(OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(self.source.pk)).exists())
 def test_dry_run_does_not_bind_and_owner_cannot_claim_lead(self):
  result=self.bind(apply=False);self.assertFalse(result['binding_recorded']);self.assert_no_money(result)
  with self.assertRaises(APIException):self.review()
  with self.assertRaises(APIException):self.bind(operator=self.base.actor)
 def test_won_source_review_second_confirmation_and_one_durable_request(self):
  self.bind();review=self.review();self.assert_no_money(review)
  with self.assertRaises(APIException):self.request(review,confirmed=False)
  first=self.request(review);second=self.request(review);self.assertFalse(first['replayed']);self.assertTrue(second['replayed']);self.assert_no_money(first)
  self.assertEqual(OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(self.source.pk)).count(),1)
  row=OutboxEvent.objects.get(pk=first['outbox_id']);self.assertEqual(row.payload['intent']['payload']['state'],'WON');self.assertEqual(row.payload['intent']['payload']['source_type'],'crm_opportunity');self.assertFalse(row.payload['intent']['fiscal_accepted']);self.assertIsNone(row.published_at)
 def test_lost_and_prospecting_never_fabricate_won_confirmation(self):
  self.bind()
  for stage in [Opportunity.Stage.PROSPECTING,Opportunity.Stage.LOST]:
   Opportunity.objects.filter(pk=self.source.pk).update(stage=stage)
   with self.assertRaises(APIException):self.review()
  self.assertFalse(OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(self.source.pk)).exists())
 def test_live_source_amount_change_requires_new_review(self):
  self.bind();review=self.review();Opportunity.objects.filter(pk=self.source.pk).update(estimated_revenue='101.00')
  with self.assertRaises(APIException):self.request(review)
  items=copy.deepcopy(self.c.items);items[0]['net']='101.00';second=self.review(items=items,expected_revision=1)
  self.assertEqual(self.request(second)['revision'],2)
 def test_changed_customer_invalidates_ownership_review(self):
  self.bind();lead=Lead.objects.create(name='Other synthetic',email=uuid.uuid4().hex+'@example.test');Opportunity.objects.filter(pk=self.source.pk).update(lead=lead)
  with self.assertRaises(APIException):self.review()
 def test_independent_reviewer_revocation_is_rechecked(self):
  self.bind();review=self.review();type(self.base.operator).objects.filter(pk=self.base.operator.pk).update(is_superuser=False)
  with self.assertRaises(APIException):self.request(review)
 def test_other_company_or_actor_cannot_reuse_binding(self):
  self.bind()
  with self.assertRaises(APIException):self.review(actor=f['fixture']['fixture']['F'].other)
  row=OutboxEvent.objects.get(event_type=crm.BIND_EVENT,aggregate_root=str(self.source.pk));p=copy.deepcopy(row.payload);p['proof']['company_id']=str(uuid.uuid4());p['proof_digest']=fingerprint(p['proof']);OutboxEvent.objects.filter(pk=row.pk).update(payload=p)
  with self.assertRaises(APIException):self.review()
 def test_boolean_reviewer_identifier_cannot_bypass_independence(self):
  self.bind();row=OutboxEvent.objects.get(event_type=crm.BIND_EVENT,aggregate_root=str(self.source.pk));p=copy.deepcopy(row.payload);p['proof']['reviewer_id']=True;p['proof_digest']=fingerprint(p['proof']);OutboxEvent.objects.filter(pk=row.pk).update(payload=p)
  with self.assertRaises(APIException):self.review()
 def test_binding_cannot_be_silently_overwritten(self):
  self.bind()
  with self.assertRaises(APIException):self.bind()
 def test_binding_expiry_is_not_a_new_confirmation(self):
  self.bind();row=OutboxEvent.objects.get(event_type=crm.BIND_EVENT,aggregate_root=str(self.source.pk));p=copy.deepcopy(row.payload);p['proof']['reviewed_at']=(timezone.now()-timedelta(days=2)).isoformat();p['proof']['valid_until']=(timezone.now()-timedelta(days=1)).isoformat();p['proof_digest']=fingerprint(p['proof']);OutboxEvent.objects.filter(pk=row.pk).update(payload=p)
  with self.assertRaises(APIException):self.review()
 def test_changed_review_evidence_or_version_rejected(self):
  self.bind();review=self.review();row=OutboxEvent.objects.get(pk=review['review_id']);p=copy.deepcopy(row.payload);p['proof']['evidence_digest']='f'*64;OutboxEvent.objects.filter(pk=row.pk).update(payload=p)
  with self.assertRaises(APIException):self.request(review)
 def test_revision_conflict_and_old_review_rejected(self):
  self.bind();first=self.review()
  with self.assertRaises(APIException):self.review()
  second=self.review(expected_revision=1)
  with self.assertRaises(APIException):self.request(first)
  self.request(second)
  with self.assertRaises(APIException):self.review(expected_revision=2)
 def test_wrong_gross_rejected_without_persisting_review(self):
  self.bind();items=copy.deepcopy(self.c.items);items[0]['net']='99.00'
  with self.assertRaises(APIException):self.review(items=items)
  self.assertFalse(OutboxEvent.objects.filter(event_type=crm.REVIEW_EVENT,aggregate_root=str(self.source.pk)).exists())
 def test_outer_rollback_and_request_failure_leave_no_fabricated_result(self):
  self.bind()
  with self.assertRaises(RuntimeError):
   with transaction.atomic():self.review();raise RuntimeError('Synthetic producer failure')
  review=self.review();original=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==EVENT_TYPE:raise RuntimeError('Synthetic queue failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.request(review)
  self.assertTrue(OutboxEvent.objects.filter(pk=review['review_id']).exists());self.assertFalse(OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(self.source.pk)).exists())
 def test_delivery_processed_is_not_fiscal_payment_or_publication(self):
  self.bind();review=self.review();result=self.request(review);OutboxEvent.objects.filter(pk=result['outbox_id']).update(status='PROCESSED')
  again=self.request(review);self.assertEqual(again['outbox_status'],'PROCESSED');self.assert_no_money(again);self.assertFalse(again['published_by_this_call'])
  OutboxEvent.objects.filter(pk=result['outbox_id']).update(status='FISCAL_ACCEPTED')
  with self.assertRaises(ValueError):self.request(review)
 def test_authenticated_api_reads_real_crm_and_rejects_injected_confirmations(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  self.bind()
  def call(action,body):
   request=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),body,format='json');force_authenticate(request,user=self.base.actor)
   return PlanCuentaViewSet.as_view({'post':action})(request)
  body={'opportunity_id':str(self.source.pk),'items':self.c.items,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True}
  self.assertEqual(call('review_crm_invoice',{**body,'state':'WON','paid':True}).status_code,400)
  review=call('review_crm_invoice',body);self.assertEqual(review.status_code,200,review.data)
  request={'opportunity_id':str(self.source.pk),'review_id':review.data['review_id'],'confirmed':True}
  self.assertEqual(call('request_crm_invoice',{**request,'fiscal_accepted':True}).status_code,400)
  result=call('request_crm_invoice',request);self.assertEqual(result.status_code,200,result.data);self.assert_no_money(result.data)
 def test_real_crm_producer_to_won_and_invoice_request_preserves_exact_amount(self):
  from apps.comercial.services.crm_service import CRMService
  from apps.comercial.engines.funnel_engine import FunnelEngine
  lead=CRMService.register_new_lead({'name':'Synthetic complete CRM','email':uuid.uuid4().hex+'@example.test','company_size':'ENTERPRISE','industry':'TURISMO','source':'referral','estimated_value':'6000.01','target_plan':'PRO'})
  source=Opportunity.objects.get(lead=lead);self.assertEqual(str(source.estimated_revenue),'6000.01');self.assertEqual(source.expected_plan,'PRO');self.assertEqual(source.stage,'prospecting')
  source=FunnelEngine.transition_stage(source,Opportunity.Stage.PROPOSAL);source=FunnelEngine.transition_stage(source,Opportunity.Stage.NEGOTIATION);source=FunnelEngine.transition_stage(source,Opportunity.Stage.WON)
  lead.refresh_from_db();self.assertEqual(lead.status,Lead.Status.CONVERTED);self.assertEqual(source.probability,100)
  self.source=source;self.args['opportunity_id']=source.pk;self.bind();items=copy.deepcopy(self.c.items);items[0]['net']='6000.01';review=self.review(items=items);result=self.request(review);self.assert_no_money(result)
 def test_crm_producer_rejects_float_and_uses_current_closed_state(self):
  from apps.comercial.engines.funnel_engine import FunnelEngine
  from apps.core_erp.accounting.exceptions import AccountingError
  with self.assertRaises(AccountingError):FunnelEngine.create_opportunity(self.lead,'PRO',1.0)
  stale=Opportunity.objects.get(pk=self.source.pk)
  with self.assertRaises(ValueError):FunnelEngine.transition_stage(stale,Opportunity.Stage.PROSPECTING)
  self.assertEqual(FunnelEngine.transition_stage(stale,Opportunity.Stage.WON).stage,Opportunity.Stage.WON)
 def test_queue_does_not_accept_a_fabricated_source_review_reference(self):
  from apps.core_erp.accounting.invoice_queue import enqueue_invoice_intent
  from apps.core_erp.accounting.invoice_intent import prepare_invoice_intent
  self.bind();review=self.review();row=OutboxEvent.objects.get(pk=review['review_id']);proof=row.payload['proof'];snapshot=proof['snapshot'];intent=prepare_invoice_intent(snapshot,str(self.base.tenant.pk))
  reference={'review_id':str(uuid.uuid4()),'intent_digest':intent['payload_digest'],'source_fingerprint':proof['source_fingerprint'],'evidence_digest':proof['evidence_digest']}
  with self.assertRaises(ValueError):enqueue_invoice_intent(snapshot,company_id=self.base.tenant.pk,actor=self.base.actor,source_review=reference)
  reference['review_id']=review['review_id'];reference['evidence_digest']='f'*64
  with self.assertRaises(ValueError):enqueue_invoice_intent(snapshot,company_id=self.base.tenant.pk,actor=self.base.actor,source_review=reference)
  self.assertFalse(OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(self.source.pk)).exists())
 def test_reservation_review_cannot_claim_external_fiscal_acceptance(self):
  review=self.c.review();row=OutboxEvent.objects.get(pk=review['review_id']);p=copy.deepcopy(row.payload);p['legal_tax_policy_verified']=True;OutboxEvent.objects.filter(pk=row.pk).update(payload=p)
  with self.assertRaises(APIException):self.c.submit(review)
if __name__=='__main__':unittest.main()
