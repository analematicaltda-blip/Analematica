"""Unified selected-account register attributes real reviewed commercial/reservation tax."""
import copy,runpy,unittest,uuid
from pathlib import Path
from decimal import Decimal
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_commercial_tax_check.py')),run_name='tax_register_fixture')
from apps.core_erp.accounting import commercial_tax_posting as engine
from apps.core_erp.accounting.tax_register import reconcile_tax_register
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry,Account,AccountingEventReceipt
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class TaxRegisterChecks(unittest.TestCase):
 def setUp(self):
  self.purchase=fixture['CommercialTaxChecks']();self.purchase.setUp();self.company=self.purchase.company;self.owner=self.purchase.actor;self.rec=self.purchase.base;self.day=self.rec.day.isoformat()
 def report(self,account=None,**extra):return reconcile_tax_register(self.company.pk,**{'account_id':str((account or self.purchase.input_tax).pk),'since':self.day,'until':self.day,**extra})
 def post(self):return self.purchase.post(self.purchase.review())
 def sale(self):
  p=copy.deepcopy(self.purchase.policy);p['code']='SALE_REGISTER71';p['components'][0].update(code='OUTPUT',kind='OUTPUT_TAX');self.purchase.record_policy(p)
  f=self.purchase.fact;f.update(direction='SALE',settlement_account_id=str(self.rec.asset.pk));f['items'][0].update(policy_code=p['code'],basis_account_id=str(self.rec.revenue.pk),tax_accounts={'OUTPUT':str(self.rec.tax.pk),'RET':str(self.purchase.input_tax.pk)})
  return self.post()
 def reservation(self):
  self.rec.fiscal.items[0].update(net='84.03',tax='15.97',tax_category='TAXABLE');fiscal=self.rec.fiscal.review(expected_revision=1)
  r=self.rec.review(fiscal_review_id=fiscal['review_id'],account_mapping={'receivable':str(self.rec.asset.pk),'revenue':str(self.rec.revenue.pk),'tax_liability':str(self.rec.tax.pk)})
  return self.rec.post(r)
 def test_input_tax_purchase_reconciles_actual_debit(self):
  p=self.post();r=self.report();self.assertEqual(r['normal_side'],'DEBIT');self.assertEqual(r['normal_movement'],'19.00');self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'19.00');self.assertEqual(r['unattributed_normal_movement'],'0.00');self.assertEqual(r['lines'][0]['document_id'],self.purchase.fact['document_id']);self.assertFalse(r['ledger_written']);self.assertFalse(r['fiscal_accepted'])
 def test_withholding_practiced_is_credit_normal_liability(self):
  self.post();r=self.report(self.purchase.retention);self.assertEqual(r['normal_side'],'CREDIT');self.assertEqual(r['tax_by_kind']['WITHHOLDING'],'2.50')
 def test_sales_withholding_suffered_is_asset(self):
  self.sale();r=self.report();self.assertEqual(r['tax_by_kind']['WITHHOLDING'],'2.50');self.assertEqual(r['normal_movement'],'2.50')
 def test_reservation_and_commercial_output_tax_share_register(self):
  self.sale();self.reservation();r=self.report(self.rec.tax);self.assertEqual(r['credit'],'34.97');self.assertEqual(r['tax_by_kind']['OUTPUT_TAX'],'34.97');self.assertEqual({l['classification'] for l in r['lines']},{'REVIEWED_COMMERCIAL_TAX','REVIEWED_RESERVATION_TAX'});self.assertEqual(r['unattributed_normal_movement'],'0.00')
 def test_exact_commercial_reversal_offsets_input_tax(self):
  self.post();self.purchase.reverse(self.purchase.reversal_review());r=self.report();self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'0.00');self.assertEqual(len(r['lines']),2);self.assertTrue(any(l['is_reversal'] for l in r['lines']))
 def test_reservation_reversal_offsets_output_tax(self):
  self.reservation();self.rec.reverse(self.rec.reversal_review());self.assertEqual(self.report(self.rec.tax)['tax_by_kind']['OUTPUT_TAX'],'0.00')
 def test_cutoff_does_not_hide_prior_tax_when_reversed_later(self):
  yesterday=(self.rec.day-timedelta(days=1)).isoformat();self.purchase.fact['entry_date']=yesterday;self.post();self.purchase.reverse(self.purchase.reversal_review());r=self.report(since=yesterday,until=yesterday);self.assertEqual(r['normal_movement'],'19.00');self.assertEqual(len(r['lines']),1)
 def test_manual_movement_explicitly_unattributed(self):
  self.post();LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.rec.day,description='Synthetic manual tax adjustment',lines_data=[{'account':self.purchase.input_tax,'debit':'3.00'},{'account':self.purchase.payable,'credit':'3.00'}],actor=self.owner,idempotency_key='register-manual')
  r=self.report();self.assertEqual(r['normal_movement'],'22.00');self.assertEqual(r['attributed_normal_movement'],'19.00');self.assertEqual(r['unattributed_normal_movement'],'3.00');self.assertEqual(r['unattributed_journals'],1)
 def test_commercial_settlement_is_not_invented_as_tax(self):
  self.post();r=self.report(self.purchase.payable);self.assertEqual(r['normal_movement'],'116.50');self.assertEqual(r['attributed_normal_movement'],'0.00');self.assertEqual(r['lines'][0]['classification'],'UNATTRIBUTED_REQUIRES_REVIEW')
 def test_empty_register_has_zero_without_fabricated_source(self):
  r=self.report();self.assertEqual(r['lines'],[]);self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'0.00')
 def test_missing_commercial_proof_fails_closed(self):
  self.post();OutboxEvent.objects.filter(event_type=engine.POSTED,payload__company_id=str(self.company.pk)).delete()
  with self.assertRaises(AccountingError):self.report()
 def test_changed_review_is_not_accepted_as_attribution(self):
  self.post();row=OutboxEvent.objects.get(event_type=engine.REVIEW,payload__company_id=str(self.company.pk));row.payload['body']['preview']['lines'][0]['debit']='999.00';OutboxEvent.objects.filter(pk=row.pk).update(payload=row.payload)
  with self.assertRaises(AccountingError):self.report()
 def test_missing_document_claim_and_receipt_are_not_reconstructed(self):
  self.post();OutboxEvent.objects.filter(event_type=engine.DOCUMENT,payload__company_id=str(self.company.pk)).delete()
  with self.assertRaises(AccountingError):self.report()
 def test_wrong_role_account_and_foreign_account_rejected(self):
  with self.assertRaises(AccountingError):self.report(self.rec.revenue)
  other=fixture['CommercialTaxChecks']();other.setUp()
  with self.assertRaises(AccountingError):self.report(other.input_tax)
 def test_invalid_intervals_and_unknown_account_rejected(self):
  for args in [{'since':'2026-11-10','until':'2026-11-09'},{'since':'2020-01-01'},{'account_id':str(uuid.uuid4())}]:
   with self.assertRaises(AccountingError):self.report(**args)
 def test_positive_api_private_response_and_strict_query(self):
  self.post();params={'provider_id':str(self.rec.case.provider.pk),'cuenta_id':str(self.purchase.input_tax.pk),'desde':self.day,'hasta':self.day}
  request=APIRequestFactory().get('/fixture/',params);force_authenticate(request,user=self.owner);r=PlanCuentaViewSet.as_view({'get':'tax_register'})(request);self.assertEqual(r.status_code,200,r.data);self.assertIn('no-store',r['Cache-Control']);self.assertEqual(r.data['tax_by_kind']['INPUT_TAX'],'19.00')
  request=APIRequestFactory().get('/fixture/',{**params,'company_id':str(uuid.uuid4())});force_authenticate(request,user=self.owner);self.assertEqual(PlanCuentaViewSet.as_view({'get':'tax_register'})(request).status_code,400)
 def test_same_tax_account_multiple_components_not_double_counted(self):
  second=copy.deepcopy(self.purchase.fact['items'][0]);second.update(item_id=str(uuid.uuid4()),net='100.00');self.purchase.fact['items'].append(second);self.post();r=self.report();self.assertEqual(r['debit'],'38.00');self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'38.00');self.assertEqual(len(r['lines']),1);self.assertEqual(r['unattributed_journals'],0)
 def test_repeated_query_has_no_side_effects(self):
  self.post();before=(JournalEntry.plain_objects.filter(tenant=self.company).count(),OutboxEvent.objects.filter(payload__company_id=str(self.company.pk)).count());one=self.report();two=self.report();self.assertEqual(one,two);self.assertEqual(before,(JournalEntry.plain_objects.filter(tenant=self.company).count(),OutboxEvent.objects.filter(payload__company_id=str(self.company.pk)).count()))
 def test_receipt_tampering_blocks_tax_attribution(self):
  self.post();AccountingEventReceipt.objects.filter(tenant=self.company,event_id=engine.event_key(self.company.pk,self.purchase.fact['document_id'])).update(payload_hash='0'*64)
  with self.assertRaises(AccountingError):self.report()
 def test_duplicate_query_selectors_are_rejected(self):
  params={'provider_id':str(self.rec.case.provider.pk),'cuenta_id':[str(self.purchase.input_tax.pk),str(self.rec.tax.pk)],'desde':self.day,'hasta':self.day};request=APIRequestFactory().get('/fixture/',params);force_authenticate(request,user=self.owner);self.assertEqual(PlanCuentaViewSet.as_view({'get':'tax_register'})(request).status_code,400)
 def test_register_query_count_does_not_grow_per_document(self):
  from django.test.utils import CaptureQueriesContext
  from django.db import connection
  self.post()
  with CaptureQueriesContext(connection) as first:self.report()
  for index in range(9):
   self.purchase.fact.update(document_id=str(uuid.uuid4()),document_digest=uuid.uuid4().hex*2);self.post()
  with CaptureQueriesContext(connection) as many:result=self.report()
  self.assertEqual(result['tax_by_kind']['INPUT_TAX'],'190.00');self.assertLessEqual(len(many),len(first)+2)
if __name__=='__main__':unittest.main()
