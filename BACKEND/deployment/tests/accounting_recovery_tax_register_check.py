"""Real proportional-return ledger attribution, without fiscal acceptance."""
import runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_purchase_recovery_check.py')),run_name='recovery_tax_fixture')
from apps.core_erp.accounting.tax_register import reconcile_tax_register
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import AccountingEventReceipt,JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_recovery as engine
class RecoveryTaxChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['PurchaseRecoveryChecks']();self.base.setUp();self.base.post();self.company=self.base.base.company;self.day=self.base.base.invoice_args['issue_date']
 def returned(self,bps=5000):return self.base.returned(self.base.review_return(return_bps=bps))
 def report(self,retention=False):
  account=self.base.base.case.retention if retention else self.base.base.case.input_tax
  return reconcile_tax_register(self.company.pk,account_id=str(account.pk),since=self.day,until=self.day)
 def test_partial_return_reduces_input_tax_and_has_no_unattributed_movement(self):
  self.returned();r=self.report();self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'9.50');self.assertEqual(r['unattributed_normal_movement'],'0.00');self.assertFalse(r['fiscal_accepted']);self.assertFalse(r['dian_compared'])
 def test_withholding_tracks_same_proportional_return(self):
  self.returned();r=self.report(True);self.assertEqual(r['tax_by_kind']['WITHHOLDING'],'1.25');self.assertEqual(r['unattributed_normal_movement'],'0.00')
 def test_two_returns_exhaust_original_without_double_counting(self):
  a=self.returned();self.base.returned({'review_id':a['review_id']});self.returned();r=self.report();self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'0.00');self.assertEqual(len(r['lines']),3);self.assertEqual(r['unattributed_normal_movement'],'0.00')
 def test_missing_return_proof_cannot_downgrade_to_manual(self):
  self.returned();OutboxEvent.objects.filter(event_type=engine.RETURNED,aggregate_root=str(self.company.pk)).delete()
  with self.assertRaises(AccountingError):self.report()
 def test_missing_receipt_is_rejected(self):
  result=self.returned();AccountingEventReceipt.objects.filter(journal_id=result['journal_id']).delete()
  with self.assertRaises(AccountingError):self.report()
 def test_changed_receipt_contract_is_rejected(self):
  result=self.returned();AccountingEventReceipt.objects.filter(journal_id=result['journal_id']).update(payload_hash='f'*64)
  with self.assertRaises(AccountingError):self.report()
 def test_proof_digest_tampering_is_rejected(self):
  self.returned();row=OutboxEvent.objects.filter(event_type=engine.RETURNED,aggregate_root=str(self.company.pk)).first();row.payload['body']['return_bps']=10000;row.save()
  with self.assertRaises(AccountingError):self.report()
 def test_deleted_prior_proof_breaks_revision_chain(self):
  a=self.returned();self.returned();OutboxEvent.objects.filter(event_type=engine.RETURNED,payload__body__journal_id=a['journal_id']).delete()
  with self.assertRaises(AccountingError):self.report()
 def test_erp_api_exposes_corrected_register_without_claiming_dian_acceptance(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  self.returned();base=self.base.base
  request=APIRequestFactory().get('/fixture/',{'provider_id':str(base.provider.pk),'cuenta_id':str(base.case.input_tax.pk),'desde':self.day,'hasta':self.day});force_authenticate(request,user=base.actor)
  r=PlanCuentaViewSet.as_view({'get':'tax_register'})(request);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['tax_by_kind']['INPUT_TAX'],'9.50');self.assertFalse(r.data['dian_compared']);self.assertIn('no-store',r['Cache-Control'])
if __name__=='__main__':unittest.main()
