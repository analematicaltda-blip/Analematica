"""Order-specific risk gate regression with synthetic professional records."""
import runpy,unittest,copy,uuid
from pathlib import Path
from datetime import timedelta
from django.test import override_settings
from rest_framework.exceptions import ValidationError,PermissionDenied
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_worker_safety_check.py')),run_name='acc012_risk_fixture')
from apps.prestadores.mi_negocio.gestion_operativa import dispatch_authorization as engine
from apps.core_erp.outbox_models import OutboxEvent
class RiskChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['WorkerSafetyChecks']();self.base.setUp();self.addCleanup(self.base.doCleanups)
 def reject(self):
  self.base.attest()
  with self.assertRaises((ValidationError,PermissionDenied)):self.base.review()
  self.base.order.refresh_from_db();self.assertEqual(self.base.order.estado,'PREPARACION');self.assertFalse(OutboxEvent.objects.filter(event_type=engine.PREFIX+'started.v1',aggregate_root=str(self.base.order.pk)).exists())
 def test_missing_order_risk_never_defaults_safe(self):
  with override_settings(OPERATIONAL_RISK_ASSESSMENTS={}):self.reject()
 def test_another_order_assessment_is_not_reused(self):
  with override_settings(OPERATIONAL_RISK_ASSESSMENTS={str(self.base.provider.pk):{str(uuid.uuid4()):self.base.risk}}):self.reject()
 def test_risk_revoked_between_confirmations(self):
  self.base.attest();review=self.base.review();self.base.risk['approved']=False
  with self.assertRaises(ValidationError):self.base.apply(review)
 def test_control_evidence_change_between_confirmations(self):
  self.base.attest();review=self.base.review();self.base.risk['hazards'][0]['evidence_digest']='e'*64
  with self.assertRaises(ValidationError):self.base.apply(review)
 def test_uncontrolled_hazard_blocks(self):self.base.risk['hazards'][0]['controlled']=False;self.reject()
 def test_duplicate_hazards_block(self):self.base.risk['hazards']*=2;self.reject()
 def test_missing_per_worker_risk_class_blocks(self):self.base.risk['worker_risk_classes']={};self.reject()
 def test_boolean_or_out_of_range_risk_class_blocks(self):
  self.base.risk['worker_risk_classes'][str(self.base.worker.pk)]=True;self.reject()
 def test_risk_specific_extra_ppe_is_required(self):self.base.risk['required_ppe'].append('HARNESS');self.reject()
 def test_expiry_must_cover_full_service(self):self.base.risk['valid_until']=(self.base.now+timedelta(minutes=1)).isoformat();self.reject()
 def test_nonprovisioned_reviewer_blocks(self):self.base.risk['reviewer_id']=str(self.base.owner.pk);self.reject()
 def test_nested_malformed_ppe_reference_is_validation_error(self):
  refs=self.base.records();refs['ppe_assignment_ids']=[{}]
  with self.assertRaises(ValidationError):self.base.attest(refs)
 def test_noncanonical_fitness_and_rest_references_rejected(self):
  refs=self.base.records()
  for name in ['fitness_authorization_id','rest_period_id']:
   with self.assertRaises(ValidationError):self.base.attest({**refs,name:'not-a-uuid'})
 def test_positive_risk_bound_without_clinical_leak(self):
  self.base.attest();review=self.base.review();result=self.base.apply(review)
  self.assertTrue(result['dispatch_recorded']);self.assertFalse(result['clinical_source_independently_verified']);self.assertFalse(result['regulatory_verified'])
  payload=OutboxEvent.objects.get(pk=result['dispatch_id']).payload
  self.assertNotIn('decision',str(payload));self.assertNotIn('diagnosis',str(payload));self.assertNotIn('worker_risk_classes',str(payload))
if __name__=='__main__':unittest.main(verbosity=2)
