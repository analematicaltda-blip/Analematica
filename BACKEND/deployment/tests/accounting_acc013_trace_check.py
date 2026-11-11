"""Operational labor cost provenance, not professional acceptance of payroll law."""
import runpy,unittest,uuid,copy
from pathlib import Path
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_operational_cost_check.py')),run_name='acc013_trace_fixture')
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
class PayrollTraceChecks(unittest.TestCase):
 def setUp(self):self.base=fixture['OperationalCostChecks']();self.base.setUp();self.addCleanup(self.base.doCleanups)
 def test_work_center_business_reference_and_posted_totals_trace(self):
  r=self.base.review();p=r['preview'];self.assertEqual(p['schema'],'sgacd-payroll-operation-cost-v2');self.assertEqual(len(p['operation_sources']),2)
  for source in p['operation_sources']:
   order=next(o for o in self.base.orders if str(o.pk)==source['operation_id']);self.assertEqual(source['commercial_reference_id'],str(order.contrato_ref_id));self.assertTrue(source['active'])
  self.assertEqual({x['operation_id'] for x in p['work_source']},set(self.base.centers));self.assertEqual(p['posted_total_cost'],'600.00')
 def test_changed_commercial_reference_invalidates_pending_review(self):
  r=self.base.review();order=self.base.orders[0];order.contrato_ref_id=uuid.uuid4();order.save(update_fields=['contrato_ref_id'])
  with self.assertRaises(AccountingError):self.base.record(r)
 def test_changed_operation_window_invalidates_pending_review(self):
  r=self.base.review();order=self.base.orders[0];order.fecha_fin_estimada+=timedelta(minutes=10);order.save(update_fields=['fecha_fin_estimada'])
  with self.assertRaises(AccountingError):self.base.record(r)
 def test_changed_business_reference_marks_old_report_incomplete(self):
  self.base.record(self.base.review());order=self.base.orders[0];order.contrato_ref_id=uuid.uuid4();order.save(update_fields=['contrato_ref_id']);r=self.base.report();self.assertFalse(r['source_complete']);self.assertIsNone(r['total_cost'])
 def test_rereview_replaces_attribution_without_extra_provision(self):
  self.base.record(self.base.review());before=JournalEntry.plain_objects.filter(tenant=self.base.company).count();order=self.base.orders[0];order.contrato_ref_id=uuid.uuid4();order.save(update_fields=['contrato_ref_id']);r=self.base.review(expected_revision=1);self.base.record(r);self.assertEqual(self.base.report()['total_cost'],'150.00');self.assertTrue(self.base.record(r)['replayed']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.company).count(),before)
 def test_snapshot_has_no_medical_data(self):
  r=self.base.review();text=str(r['preview']['operation_sources']);self.assertNotIn('diagnosis',text);self.assertNotIn('fitness',text)
if __name__=='__main__':unittest.main(verbosity=2)
