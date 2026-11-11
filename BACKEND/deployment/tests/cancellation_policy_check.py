"""Versioned commercial charge policies and declared refund proposals; no payments."""
import runpy,unittest,uuid,copy
from pathlib import Path
from django.utils import timezone
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_fiscal_check.py')),run_name='cancellation_policy_fixture')
from apps.prestadores.mi_negocio.gestion_comercial import cancellation_policies as service
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.models import PoliticaCancelacion
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from apps.domain_business.operativa.models import Reservation
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_comercial.cancellation_views import CancellationPolicyCommand
# Reuse the temporary schema creator; never selects a project database.
fixture['fixture']['fixture']['fixture']['create'](PoliticaCancelacion)
from apps.core_erp.accounting.models import JournalEntry
fixture['fixture']['fixture']['fixture']['create'](JournalEntry)
class CancellationPolicyChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['FiscalReservationTests']();self.base.setUp();self.user=self.base.case.actor;self.provider=self.base.case.provider;self.company=self.base.case.tenant;self.booking=self.base.case.reservation;self.booking.refresh_from_db();self.scope={'actor':self.user,'provider_id':self.provider.pk};self.day=timezone.localdate().isoformat();self.config={'name':'Synthetic tourism cancellation','terms':'Declared terms for testing; subject to applicable exceptions.','scope':'PLAN_TURISTICO','percentage':'10.00','basis':'REQUESTED_REFUND','active':True,'valid_from':self.day,'valid_until':self.day}
 def publish(self,**kw):
  args={'request_id':str(uuid.uuid4()),'policy_id':None,'expected_revision':0,'values':self.config.copy(),'confirmed':True};args.update(kw);r=service.review_policy(**self.scope,**args);return service.publish_policy(**self.scope,review_id=r['review_id'],confirmed=True)
 def bind(self,p,**kw):
  args={'reservation_id':str(self.booking.pk),'policy_id':p['policy_id'],'policy_revision':p['revision'],'accepted_at':timezone.now().isoformat(),'consent_kind':'ACCEPTED_AMENDMENT','consent_digest':'a'*64,'confirmed':True};args.update(kw);return service.bind_policy(**self.scope,**args)
 def review(self,**kw):
  args={'reservation_id':str(self.booking.pk),'request_id':str(uuid.uuid4()),'requested_refund':'100.00','reason_code':'STANDARD_CANCELLATION','evidence_digest':'b'*64,'expected_revision':0,'confirmed':True};args.update(kw);return service.review_case(**self.scope,**args)
 def confirm(self,r,**kw):return service.confirm_case(**self.scope,reservation_id=str(self.booking.pk),review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def test_acceptance_validity_uses_colombia_day_across_utc_midnight(self):
  from datetime import datetime,timezone as dt_timezone
  from unittest.mock import patch
  instant=datetime(2027,1,12,0,30,tzinfo=dt_timezone.utc)
  with timezone.override('America/Bogota'),patch.object(timezone,'now',return_value=instant),patch.object(service,'context',return_value=(self.user,self.provider,self.company)):
   self.config.update(valid_from='2027-01-11',valid_until='2027-01-11')
   published=self.publish();accepted=self.bind(published)
   self.assertIsNotNone(accepted)
 def test_ten_percent_retention_and_net_refund_proposal(self):
  p=self.publish();self.bind(p);r=self.review();self.assertEqual(r['preview']['calculation']['fee_amount'],'10.00');self.assertEqual(r['preview']['calculation']['refund_net'],'90.00');a=self.confirm(r);self.assertTrue(a['proposal_only']);self.assertFalse(a['tax_withholding']);self.assertFalse(a['money_transferred']);self.booking.refresh_from_db();self.assertEqual(self.booking.status,'CONFIRMED')
 def test_percentage_changes_do_not_change_existing_acceptance(self):
  p=self.publish();self.bind(p);changed=self.publish(policy_id=p['policy_id'],expected_revision=1,values={**self.config,'percentage':'20.00'});
  with self.assertRaises(AccountingError):self.bind(changed)
  r=self.review();self.assertEqual(r['preview']['policy_revision'],1);self.assertEqual(r['preview']['calculation']['fee_amount'],'10.00')
 def test_fee_requires_recorded_customer_acceptance(self):
  self.publish()
  with self.assertRaises(AccountingError):self.review()
 def test_exception_supplier_failure_and_waiver_have_zero_charge(self):
  self.bind(self.publish())
  for revision,reason in enumerate(['STATUTORY_EXCEPTION','SUPPLIER_FAILURE','COMPANY_WAIVER']):
   r=self.review(reason_code=reason,expected_revision=revision);self.assertEqual(r['preview']['calculation']['fee_amount'],'0.00');self.assertEqual(r['preview']['calculation']['refund_net'],'100.00')
 def test_contract_total_base_is_capped_at_declared_refund(self):
  p=self.publish(values={**self.config,'percentage':'50.00','basis':'CONTRACT_TOTAL'});self.bind(p);r=self.review(requested_refund='20.00');self.assertEqual(r['preview']['calculation']['fee_amount'],'20.00');self.assertTrue(r['preview']['calculation']['capped']);self.assertEqual(r['preview']['calculation']['refund_net'],'0.00')
 def test_zero_and_hundred_percent_and_exact_cents(self):
  for pct,amount,fee in [('0','0.05','0.00'),('10','0.05','0.01'),('100','100.00','100.00')]:
   result=service.calculation(self.booking,{**self.config,'percentage':pct},amount,'STANDARD_CANCELLATION');self.assertEqual(result['fee_amount'],fee)
 def test_bad_percentage_binary_float_and_excess_refund_rejected(self):
  for value in ['100.01','-1','1e2',10.0,'10.001']:
   with self.assertRaises(AccountingError):self.publish(values={**self.config,'percentage':value})
  self.bind(self.publish())
  with self.assertRaises(AccountingError):self.review(requested_refund='101.00')
 def test_publication_and_proposal_require_both_confirmations(self):
  with self.assertRaises(AccountingError):service.review_policy(**self.scope,request_id=str(uuid.uuid4()),policy_id=None,expected_revision=0,values=self.config,confirmed=False)
  r=service.review_policy(**self.scope,request_id=str(uuid.uuid4()),policy_id=None,expected_revision=0,values=self.config,confirmed=True)
  with self.assertRaises(AccountingError):service.publish_policy(**self.scope,review_id=r['review_id'],confirmed=False)
  p=service.publish_policy(**self.scope,review_id=r['review_id'],confirmed=True);self.bind(p)
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.confirm(r,confirmed=False)
 def test_retry_does_not_duplicate_policy_or_settlement(self):
  r=service.review_policy(**self.scope,request_id=str(uuid.uuid4()),policy_id=None,expected_revision=0,values=self.config,confirmed=True);a=service.publish_policy(**self.scope,review_id=r['review_id'],confirmed=True);b=service.publish_policy(**self.scope,review_id=r['review_id'],confirmed=True);self.assertEqual(a['policy_id'],b['policy_id']);self.assertTrue(b['replayed']);self.bind(a);r=self.review();self.confirm(r);self.assertTrue(self.confirm(r)['replayed'])
 def test_older_booking_requires_explicit_amendment_declaration(self):
  p=self.publish()
  with self.assertRaises(AccountingError):self.bind(p,consent_kind='NEW_CONTRACT')
 def test_other_owner_and_foreign_booking_are_rejected(self):
  from django.contrib.auth import get_user_model
  other=get_user_model().objects.filter(is_active=True).exclude(pk=self.user.pk).first()
  with self.assertRaises(PermissionDenied):service.sources(actor=other,provider_id=self.provider.pk,policy_after=None,reservation_after=None)
  self.publish()
  with self.assertRaises(AccountingError):service.case_state(**self.scope,reservation_id=str(uuid.uuid4()))
 def test_source_change_and_pending_review_replacement_are_rejected(self):
  self.bind(self.publish());first=self.review();self.review(requested_refund='50.00',expected_revision=1)
  with self.assertRaises(AccountingError):self.confirm(first)
  Reservation.plain_objects.filter(pk=self.booking.pk).update(total_price='101.00')
  with self.assertRaises(AccountingError):service.case_state(**self.scope,reservation_id=str(self.booking.pk))
 def test_managed_legacy_policy_cannot_be_directly_edited_or_deleted(self):
  from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.views import PoliticaCancelacionViewSet
  p=self.publish()
  for action,method,data in [('partial_update','patch',{'nombre':'Silent change'}),('destroy','delete',{})]:
   request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.provider.pk),data,format='json');force_authenticate(request,user=self.user);r=PoliticaCancelacionViewSet.as_view({method:action})(request,pk=p['policy_id']);self.assertEqual(r.status_code,400,r.data)
 def test_real_api_scope_and_no_store_headers(self):
  request=APIRequestFactory().post('/fixture/?provider_id='+str(self.provider.pk),{'policy_after':None,'reservation_after':None},format='json');force_authenticate(request,user=self.user);r=CancellationPolicyCommand.as_view()(request,operation='sources');self.assertEqual(r.status_code,200,r.data);self.assertIn('no-store',r['Cache-Control']);self.assertFalse(r.data['funds_verified'])
 def test_competing_policy_edits_cannot_overwrite_newer_version(self):
  p=self.publish();reviews=[]
  for percentage in ['15.00','20.00']:reviews.append(service.review_policy(**self.scope,request_id=str(uuid.uuid4()),policy_id=p['policy_id'],expected_revision=1,values={**self.config,'percentage':percentage},confirmed=True))
  service.publish_policy(**self.scope,review_id=reviews[0]['review_id'],confirmed=True)
  with self.assertRaises(AccountingError):service.publish_policy(**self.scope,review_id=reviews[1]['review_id'],confirmed=True)
 def test_unversioned_source_tampering_is_not_silently_used(self):
  p=self.publish();PoliticaCancelacion.objects.filter(pk=p['policy_id']).update(descripcion='Changed outside review')
  with self.assertRaises(AccountingError):service.policy_state(**self.scope,policy_id=p['policy_id'])
 def test_recovery_and_failures_do_not_post_or_duplicate_financial_events(self):
  from apps.core_erp.accounting.models import JournalEntry
  from unittest.mock import patch
  count=JournalEntry.plain_objects.count();p=self.publish();self.bind(p);r=self.review()
  with patch.object(service,'write',side_effect=AccountingError('synthetic proposal store failure')):
   with self.assertRaises(AccountingError):self.confirm(r)
  self.confirm(r);before=OutboxEvent.objects.count();state=service.case_state(**self.scope,reservation_id=str(self.booking.pk));self.assertEqual(state['registered']['calculation']['refund_net'],'90.00');self.assertFalse(state['confirmations_restored']);self.assertEqual(count,JournalEntry.plain_objects.count());self.assertEqual(before,OutboxEvent.objects.count())
if __name__=='__main__':unittest.main()
