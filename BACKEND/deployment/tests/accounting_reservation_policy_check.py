"""Recorded policy -> reservation request and real canonical ledger posting."""
import copy,runpy,unittest,uuid
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='reservation_policy_fixture')
from apps.core_erp.accounting import tax_policies
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.reports_engine import ReportsEngine
from apps.core_erp.outbox_models import OutboxEvent
from apps.domain_business.comercial.services import reservation_tax_policy as engine,reservation_fiscal as fiscal
from apps.turismo.models import VerifiedCompanyLink
from rest_framework.exceptions import APIException,ValidationError
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet

class ReservationPolicyChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['RecognitionTests']();self.case.setUp();self.f=self.case.case;self.company=self.f.tenant;self.actor=self.f.actor
  year=timezone.localdate().year;self.day=timezone.localdate().isoformat()
  self.policy={'code':'DECLARED_TOURISM','jurisdiction':'CO','currency':'COP','valid_from':str(year)+'-01-01','valid_until':str(year)+'-12-31','rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'DECLARED_OUTPUT','kind':'OUTPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']}]}
  r=tax_policies.review_policy(self.company.pk,actor=self.actor,policy=self.policy,evidence_digest='a'*64,expected_revision=0,confirmed=True);tax_policies.record_policy(self.company.pk,actor=self.actor,review_id=r['review_id'],confirmed=True)
  self.selection=[{'item_id':str(uuid.uuid4()),'net':'84.03','tax_category':'TAXABLE','policy_code':self.policy['code'],'policy_revision':1}]
  self.args={'actor':self.actor,'provider_id':self.f.provider.pk,'reservation_id':self.f.reservation.pk,'selection':self.selection,'economic_date':self.day,'evidence_digest':'b'*64,'confirmed':True,'expected_revision':1}
 def review(self,**extra):return engine.review_with_policy(**{**self.args,**extra})
 def submit(self,r):return fiscal.request_reservation_invoice(actor=self.actor,provider_id=self.f.provider.pk,reservation_id=self.f.reservation.pk,review_id=r['review_id'],confirmed=True)
 def recognition(self,r):return self.case.review(fiscal_review_id=r['review_id'],account_mapping={'receivable':str(self.case.asset.pk),'revenue':str(self.case.revenue.pk),'tax_liability':str(self.case.tax.pk)})
 def test_exact_quote_source_and_request_without_emission(self):
  r=self.review();quote=r['preview']['quotes'][0]['quote'];self.assertEqual(quote['output_tax'],'15.97');self.assertEqual(quote['gross'],'100.00');self.assertFalse(r['regulatory_verified']);a=self.submit(r);self.assertTrue(self.submit(r)['replayed']);self.assertFalse(a['fiscal_accepted']);self.assertFalse(a['ledger_written'])
 def test_balanced_posting_and_replay_use_policy_tax(self):
  r=self.review();review=self.recognition(r);post=self.case.post(review);self.assertTrue(self.case.post(review)['replayed'])
  rows=LedgerEntry.plain_objects.filter(journal_entry_id=post['journal_id']);self.assertEqual(rows.count(),3);self.assertEqual(str(rows.get(account=self.case.tax).credit_amount),'15.97');self.assertEqual(str(rows.get(account=self.case.revenue).credit_amount),'84.03');self.assertEqual(str(rows.get(account=self.case.asset).debit_amount),'100.00');self.assertFalse(post['fiscal_accepted']);self.assertFalse(post['money_transferred'])
  report=ReportsEngine.get_trial_balance(self.company.pk,self.case.day);self.assertEqual(report['total_debit'],report['total_credit'])
 def test_mixed_taxable_and_exempt_exact_total(self):
  selection=[{**self.selection[0],'net':'50.00'},{**self.selection[0],'item_id':str(uuid.uuid4()),'net':'40.50','tax_category':'EXEMPT'}]
  r=self.review(selection=selection);record=OutboxEvent.objects.get(pk=r['review_id']);self.assertEqual(sum(Decimal(x['tax']) for x in record.payload['snapshot']['items']),Decimal('9.50'));self.submit(r)
 def test_nonzero_withholding_rejected_atomically(self):
  policy=copy.deepcopy(self.policy);policy['code']='DECLARED_WITHHOLDING';policy['components'].append({'code':'DECLARED_RET','kind':'WITHHOLDING','rate_bps':250,'applies_to':['TAXABLE']})
  r=tax_policies.review_policy(self.company.pk,actor=self.actor,policy=policy,evidence_digest='a'*64,expected_revision=0,confirmed=True);tax_policies.record_policy(self.company.pk,actor=self.actor,review_id=r['review_id'],confirmed=True)
  count=OutboxEvent.objects.count()
  with self.assertRaises(ValidationError):self.review(selection=[{**self.selection[0],'policy_code':policy['code']}])
  self.assertEqual(OutboxEvent.objects.count(),count)
 def test_missing_expired_version_or_total_mismatch_rejected(self):
  for changes in [{'selection':[{**self.selection[0],'policy_revision':2}]},{'economic_date':'2000-01-01'},{'selection':[{**self.selection[0],'net':'100.00'}]}]:
   with self.assertRaises((AccountingError,APIException)):self.review(**changes)
 def test_false_confirmation_duplicate_or_unknown_fields_rejected(self):
  for changes in [{'confirmed':False},{'selection':[self.selection[0],self.selection[0]]},{'selection':[{**self.selection[0],'tax':'0.00'}]},{'selection':[]}]:
   with self.assertRaises((AccountingError,APIException)):self.review(**changes)
 def test_source_change_and_binding_revocation_block_request(self):
  from apps.domain_business.operativa.models import Reservation
  r=self.review();Reservation.plain_objects.filter(pk=self.f.reservation.pk).update(total_price='101.00')
  with self.assertRaises(APIException):self.submit(r)
  Reservation.plain_objects.filter(pk=self.f.reservation.pk).update(total_price='100.00');VerifiedCompanyLink.objects.filter(provider=self.f.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.submit(r)
 def test_missing_policy_link_blocks_request_and_post(self):
  r=self.review();review=self.recognition(r);OutboxEvent.objects.filter(pk=r['policy_link_id']).delete()
  with self.assertRaises(APIException):self.submit(r)
  with self.assertRaises(APIException):self.case.post(review)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_tampered_quote_link_blocks_request(self):
  r=self.review();row=OutboxEvent.objects.get(pk=r['policy_link_id']);row.payload['proof']['quotes'][0]['quote']['output_tax']='0.00';row.save(update_fields=['payload'])
  with self.assertRaises(APIException):self.submit(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_reserved_reference_without_proof_is_rejected(self):
  items=[{'item_id':str(uuid.uuid4()),'net':'100.00','tax':'0.00','tax_category':'EXCLUDED','policy_reference':engine.PREFIX+'fake:1'}]
  r=fiscal.review_reservation(actor=self.actor,provider_id=self.f.provider.pk,reservation_id=self.f.reservation.pk,items=items,evidence_digest='b'*64,confirmed=True,expected_revision=1)
  with self.assertRaises(APIException):self.submit(r)
 def test_failed_link_write_rolls_back_fiscal_review(self):
  original=OutboxEvent.objects.create;count=OutboxEvent.objects.count()
  def create(**kwargs):
   if kwargs.get('event_type')==engine.EVENT:raise RuntimeError('Synthetic link storage failure')
   return original(**kwargs)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.review()
  self.assertEqual(OutboxEvent.objects.count(),count);self.assertEqual(fiscal.latest_review(self.company,self.f.reservation).payload['review_revision'],1)
 def test_tax_date_different_from_posting_date_rejected(self):
  from datetime import timedelta
  r=self.review(economic_date=(timezone.localdate()-timedelta(days=1)).isoformat())
  with self.assertRaises(APIException):self.recognition(r)
 def test_multiple_positive_tax_components_cannot_be_merged(self):
  policy=copy.deepcopy(self.policy);policy['code']='MULTIPLE_COMPONENTS';policy['components'].append({'code':'ANOTHER_DECLARED_TAX','kind':'OUTPUT_TAX','rate_bps':100,'applies_to':['TAXABLE']})
  r=tax_policies.review_policy(self.company.pk,actor=self.actor,policy=policy,evidence_digest='a'*64,expected_revision=0,confirmed=True);tax_policies.record_policy(self.company.pk,actor=self.actor,review_id=r['review_id'],confirmed=True)
  with self.assertRaises(APIException):self.review(selection=[{**self.selection[0],'policy_code':policy['code']}])
 def test_owner_api_is_private(self):
  body={k:(str(v) if k=='reservation_id' else v) for k,v in self.args.items() if k not in {'actor','provider_id'}}
  req=APIRequestFactory().post('/fixture/?provider_id='+str(self.f.provider.pk),body,format='json');force_authenticate(req,user=self.actor)
  r=PlanCuentaViewSet.as_view({'post':'review_reservation_policy'})(req);self.assertEqual(r.status_code,200,r.data);self.assertTrue(r.data['stored_policy_link_verified']);self.assertIn('no-store',r['Cache-Control'])
if __name__=='__main__':unittest.main()
