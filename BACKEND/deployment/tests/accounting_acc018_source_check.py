"""Operational source-segment uniqueness and append-only corrections, synthetic data."""
import runpy,unittest,copy,uuid
from pathlib import Path
from datetime import datetime,time,timedelta
from decimal import localcontext,Inexact,Rounded,ROUND_DOWN
from zoneinfo import ZoneInfo
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_environmental_records_check.py')),run_name='acc018_environmental_fixture')
from apps.prestadores.mi_negocio.gestion_operativa.models import OrdenOperativa
from apps.prestadores.mi_negocio.gestion_contable.contabilidad import environmental_records as engine,environmental_corrections as correction
from apps.core_erp.accounting.environmental import estimate
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from django.db import connection
for model in [OrdenOperativa]:
 if model._meta.db_table not in connection.introspection.table_names():
  with connection.schema_editor() as editor:editor.create_model(model)
class SourceChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['EnvironmentalRecordChecks']();self.base.setUp();self.addCleanup(self.base.doCleanups)
  day=datetime.fromisoformat(self.base.day).date();begin=datetime.combine(day,time.min,ZoneInfo('America/Bogota'))
  self.order=OrdenOperativa.objects.create(provider=self.base.provider,contrato_ref_id=uuid.uuid4(),descripcion_servicio='Synthetic measured operation',fecha_inicio=begin,fecha_fin_estimada=begin+timedelta(hours=23))
  self.activity={**self.base.activity,'source_reference':str(self.order.pk),'source_segment':'OUTBOUND'}
 def review(self,**extra):return self.base.review(activities=[self.activity],**extra)
 def test_source_is_preserved_in_snapshot_and_receipt_is_idempotent(self):
  r=self.review();self.base.record(r);self.assertEqual(self.base.state(r)['preview']['assessment']['snapshot']['activities'][0]['source_reference'],str(self.order.pk));self.assertTrue(self.base.record(r)['replayed']);self.assertEqual(OutboxEvent.objects.filter(event_type=engine.SOURCE,payload__company_id=str(self.base.company.pk)).count(),1)
 def test_renamed_activity_same_source_segment_cannot_be_recorded(self):
  self.base.record(self.review());other=self.base.review(activities=[{**self.activity,'id':'renamed-route'}]);before=OutboxEvent.objects.count()
  with self.assertRaises(AccountingError):self.base.record(other)
  self.assertEqual(OutboxEvent.objects.count(),before)
 def test_changed_factor_does_not_duplicate_original_source_segment(self):
  self.base.record(self.review());other=self.base.review(activities=[{**self.activity,'id':'renamed-route'}],factors=[{**self.base.factor,'version':'synthetic-v2'}])
  with self.assertRaises(AccountingError):self.base.record(other)
 def test_duplicate_source_inside_assessment_rejected(self):
  with self.assertRaises(AccountingError):self.base.review(activities=[self.activity,{**self.activity,'id':'renamed'}])
 def test_foreign_or_missing_operational_source_rejected(self):
  with self.assertRaises(AccountingError):self.base.review(activities=[{**self.activity,'source_reference':str(uuid.uuid4())}])
 def test_source_claim_removal_detected_without_repair(self):
  r=self.review();self.base.record(r);OutboxEvent.objects.filter(event_type=engine.SOURCE,payload__company_id=str(self.base.company.pk)).delete()
  with self.assertRaises(AccountingError):self.base.state(r)
 def test_decimal_precision_and_traps_do_not_change_assessment(self):
  activity={**self.activity,'passengers':3};args={'company_id':self.base.company.pk,'activities':[activity],'factors':[self.base.factor]};expected=estimate(**args)
  with localcontext() as ctx:
   ctx.prec=2;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True;self.assertEqual(estimate(**args),expected)
 def test_partial_reference_or_noncanonical_segment_is_rejected(self):
  for change in [{'source_segment':'outbound'},{'source_reference':{}},{'source_reference':'not-a-uuid'}]:
   with self.assertRaises(AccountingError):self.base.review(activities=[{**self.activity,**change}])
 def test_correction_cannot_move_original_source_binding(self):
  r=self.review();posted=self.base.record(r)
  with self.assertRaises(AccountingError):correction.review_correction(actor=self.base.owner,provider_id=self.base.provider.pk,observation_id=posted['observation_id'],expected_revision=0,activities=[{**self.activity,'source_segment':'OTHER'}],factors=[self.base.factor],evidence_digest='c'*64,reason_code='QUANTITY_ERROR',confirmed=True)
 def test_metadata_tampering_is_rejected_without_repair(self):
  r=self.review();self.base.record(r)
  for kind in [engine.REVIEW,engine.RECORDED,engine.FACTOR,engine.ACTIVITY,engine.SOURCE]:
   row=OutboxEvent.objects.filter(event_type=kind,payload__company_id=str(self.base.company.pk)).first();OutboxEvent.objects.filter(pk=row.pk).update(domain='other')
   with self.assertRaises(AccountingError):self.base.state(r)
   OutboxEvent.objects.filter(pk=row.pk).update(domain='accounting')
 def test_source_change_between_confirmations_is_rejected_atomically(self):
  review=self.review();self.order.is_active=False;self.order.save(update_fields=['is_active'])
  before=OutboxEvent.objects.count()
  with self.assertRaises(AccountingError):self.base.record(review)
  self.assertEqual(OutboxEvent.objects.count(),before)
 def test_quantity_correction_keeps_one_original_source_claim(self):
  review=self.review();original=self.base.record(review)
  proposal=correction.review_correction(actor=self.base.owner,provider_id=self.base.provider.pk,observation_id=original['observation_id'],expected_revision=0,activities=[{**self.activity,'quantity':'200'}],factors=[self.base.factor],evidence_digest='c'*64,reason_code='QUANTITY_ERROR',confirmed=True)
  correction.record_correction(actor=self.base.owner,provider_id=self.base.provider.pk,observation_id=original['observation_id'],review_id=proposal['review_id'],confirmed=True)
  state=self.base.state(review);self.assertEqual(state['corrections']['effective_assessment']['kg_co2e'],'24.691200');self.assertEqual(OutboxEvent.objects.filter(event_type=engine.SOURCE,payload__company_id=str(self.base.company.pk)).count(),1)
if __name__=='__main__':unittest.main(verbosity=2)
