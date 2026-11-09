"""Tax account movements reconciled to actual reviewed recognition and reversal."""
import runpy,unittest
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='tax_fixture')
from apps.core_erp.accounting.tax_reconciliation import reconcile_tax_account
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class TaxReconciliationTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['RecognitionTests']();self.case.setUp();self.owner=self.case.case.actor;self.company=self.case.case.tenant
 def report(self,**extra):return reconcile_tax_account(self.company.pk,**{'account_id':self.case.tax.pk,'since':self.case.day.isoformat(),'until':self.case.day.isoformat(),**extra})
 def post_tax(self):
  self.case.fiscal.items[0].update(net='84.03',tax='15.97',tax_category='TAXABLE');fiscal=self.case.fiscal.review(expected_revision=1)
  review=self.case.review(fiscal_review_id=fiscal['review_id'],account_mapping={'receivable':str(self.case.asset.pk),'revenue':str(self.case.revenue.pk),'tax_liability':str(self.case.tax.pk)})
  return self.case.post(review)
 def test_tax_from_real_journal_matches_reviewed_source(self):
  posted=self.post_tax();r=self.report();self.assertEqual(r['credit'],'15.97');self.assertEqual(r['reviewed_reservation_tax'],'15.97');self.assertEqual(r['unattributed_net'],'0.00');self.assertEqual(r['lines'][0]['journal_id'],posted['journal_id']);self.assertFalse(r['dian_compared']);self.assertFalse(r['fiscal_accepted'])
 def test_reversal_offsets_tax_without_removing_original(self):
  self.post_tax();self.case.reverse(self.case.reversal_review());r=self.report();self.assertEqual(r['net_liability_movement'],'0.00');self.assertEqual(r['reviewed_reservation_tax'],'0.00');self.assertEqual(len(r['lines']),2)
 def test_manual_movement_remains_explicitly_unattributed(self):
  self.post_tax();LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.case.day,description='Reviewed manual tax adjustment',lines_data=[{'account':self.case.asset,'debit':'3.00'},{'account':self.case.tax,'credit':'3.00'}],actor=self.owner,idempotency_key='manual-tax-adjustment')
  r=self.report();self.assertEqual(r['credit'],'18.97');self.assertEqual(r['unattributed_net'],'3.00');self.assertEqual(r['unattributed_movements'],1)
 def test_wrong_role_foreign_or_missing_account_rejected(self):
  import uuid
  for account in (self.case.asset.pk,uuid.uuid4()):
   with self.assertRaises(AccountingError):self.report(account_id=account)
 def test_changed_review_proof_cannot_supply_tax_amount(self):
  self.post_tax();row=OutboxEvent.objects.get(event_type='accounting.reservation.recognition-reviewed.v1',aggregate_root=str(self.case.case.reservation.pk));row.payload['review']['totals']['tax']='1.00';row.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.report()
 def test_invalid_intervals_and_no_movements(self):
  self.assertEqual(self.report()['lines'],[])
  for since,until in [('2026-11-09','2026-11-08'),('2020-01-01','2026-11-08')]:
   with self.assertRaises(AccountingError):self.report(since=since,until=until)
 def test_real_api_uses_owner_company_and_private_response(self):
  self.post_tax();request=APIRequestFactory().get('/fixture/',{'provider_id':str(self.case.case.provider.pk),'cuenta_id':str(self.case.tax.pk),'desde':self.case.day.isoformat(),'hasta':self.case.day.isoformat()});force_authenticate(request,user=self.owner)
  response=PlanCuentaViewSet.as_view({'get':'tax_reconciliation'})(request);self.assertEqual(response.status_code,200,response.data);self.assertIn('no-store',response['Cache-Control']);self.assertEqual(response.data['credit'],'15.97')
if __name__=='__main__':unittest.main()
