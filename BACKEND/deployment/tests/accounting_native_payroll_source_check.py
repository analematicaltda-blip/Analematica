"""Native source intake, recovery, duplicate guards and actual ledger consumption."""
import copy,runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_operational_cost_check.py')),run_name='native_source_fixture')
from apps.prestadores.mi_negocio.gestion_contable.nomina import native_novelty as engine,reviewed_payroll as payroll
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import NovedadNomina,ConceptoNomina,DetalleLiquidacion,Planilla
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.accounting.exceptions import AccountingError
class NativeSourceChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['fixture']['PayrollChecks']();self.base.setUp();self.concept=ConceptoNomina.objects.create(codigo=uuid.uuid4().hex[:10],descripcion='Synthetic bonus concept',tipo='DEVENGADO');self.args={'actor':self.base.owner,'provider_id':self.base.provider.pk,'payroll_id':str(self.base.payroll.pk),'request_id':str(uuid.uuid4()),'employee_id':str(self.base.employee.pk),'concept_id':self.concept.pk,'event_date':self.base.day.isoformat(),'amount':'50.00','source_reference':'PRIVATE-NATIVE-REFERENCE','evidence_digest':'a'*64,'authorization_digest':'b'*64,'confirmed':True}
 def record(self,**kw):return engine.record(**{**self.args,**kw})
 def lookup(self):return engine.lookup(actor=self.base.owner,provider_id=self.base.provider.pk,payroll_id=str(self.base.payroll.pk),source_reference=self.args['source_reference'])
 def review(self,capture,**kw):
  policy=copy.deepcopy(self.base.policy);policy.update(code='NATIVE_BONUS',novelty_mode='COMPENSATION_FROM_SOURCE',source_earning_rules=[{'concept_id':self.concept.pk,'detail_field':'bonificaciones'}]);[c.update(basis='GROSS') for c in policy['components']];workers=copy.deepcopy(self.base.args['workers']);workers[0]['novelty_items']=[{'novelty_id':capture['novelty_id'],'evidence_digest':self.args['evidence_digest'],'authorization_digest':self.args['authorization_digest']}]
  return self.base.review(**{'policy':policy,'workers':workers,**kw})
 def test_capture_is_metadata_only_and_keeps_reference_hashed(self):
  r=self.record();self.assertFalse(r['ledger_written']);self.assertFalse(r['money_transferred']);self.assertFalse(r['document_uploaded']);row=NovedadNomina.objects.get(pk=r['novelty_id']);self.assertFalse(row.procesada);self.assertEqual(str(row.cantidad),'1.00');self.assertEqual(row.descripcion,'');self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.base.company).exists());self.assertNotIn(self.args['source_reference'],str(list(OutboxEvent.objects.filter(aggregate_root=str(self.base.company.pk)).values_list('payload',flat=True))))
 def test_same_request_replays_without_duplicate_source(self):
  a=self.record();b=self.record();self.assertEqual(a['novelty_id'],b['novelty_id']);self.assertTrue(b['replayed']);self.assertFalse(b['metadata_written']);self.assertEqual(NovedadNomina.objects.filter(empleado=self.base.employee).count(),1)
  with self.assertRaises(AccountingError):self.record(amount='51.00')
 def test_same_reference_new_request_rejected_and_lookup_recovers_without_authorization(self):
  a=self.record()
  with self.assertRaises(AccountingError):self.record(request_id=str(uuid.uuid4()))
  s=self.lookup();self.assertEqual(a['novelty_id'],s['novelty_id']);self.assertTrue(s['read_only']);self.assertFalse(s['confirmations_restored']);self.assertFalse(s['authorization_independently_verified'])
 def test_not_found_is_read_only_and_writes_nothing(self):
  before=NovedadNomina.objects.count();r=self.lookup();self.assertFalse(r['found']);self.assertTrue(r['read_only']);self.assertFalse(r['metadata_written']);self.assertEqual(NovedadNomina.objects.count(),before)
 def test_missing_confirmation_reference_dates_precision_and_scope_rejected(self):
  from datetime import timedelta
  for change in [{'confirmed':False},{'source_reference':' BAD '},{'event_date':(self.base.day+timedelta(days=1)).isoformat()},{'amount':'1.001'},{'amount':1.0},{'amount':'0.00'},{'employee_id':str(uuid.uuid4())},{'concept_id':True}]:
   with self.assertRaises((AccountingError,ValueError)):self.record(**change)
  self.assertFalse(NovedadNomina.objects.filter(empleado=self.base.employee).exists())
 def test_reference_failure_rolls_back_source_and_capture_evidence(self):
  create=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.REFERENCE:raise RuntimeError('Synthetic source reference failure')
   return create(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.record()
  self.assertFalse(NovedadNomina.objects.filter(empleado=self.base.employee).exists());self.assertFalse(OutboxEvent.objects.filter(event_type=engine.RECORDED,payload__body__company_id=str(self.base.company.pk)).exists());self.record()
 def test_mutated_native_source_is_not_adopted_as_legacy_or_reposted(self):
  r=self.record();NovedadNomina.objects.filter(pk=r['novelty_id']).update(valor='51.00')
  with self.assertRaises(AccountingError):self.lookup()
  with self.assertRaises(AccountingError):self.review(r)
 def test_missing_binding_or_reference_cannot_release_duplicate_protection(self):
  r=self.record();binding=OutboxEvent.objects.get(pk=engine.key('source',self.base.company,r['novelty_id']));saved=copy.deepcopy(binding);binding.delete()
  with self.assertRaises(AccountingError):self.review(r)
  saved.save(force_insert=True);OutboxEvent.objects.filter(pk=engine.key('reference',self.base.company,engine.reference(self.args['source_reference']))).delete()
  with self.assertRaises(AccountingError):self.lookup()
  with self.assertRaises(AccountingError):self.record(request_id=str(uuid.uuid4()))
 def test_capture_review_post_and_lookup_share_the_same_native_source(self):
  r=self.record();review=self.review(r);self.assertEqual(review['preview']['snapshot']['totals']['gross'],'550.00');self.assertEqual(review['preview']['snapshot']['totals']['net'],'528.00');a=self.base.post(review);s=self.lookup();self.assertTrue(s['processed']);self.assertEqual(r['novelty_id'],s['novelty_id']);self.assertEqual(self.base.post(review)['journal_id'],a['journal_id']);self.assertEqual(str(DetalleLiquidacion.objects.get(planilla=self.base.payroll).bonificaciones),'50.00');self.assertTrue(self.record()['replayed'])
 def test_posting_must_use_the_captured_support_references(self):
  r=self.record();review=self.review(r);workers=copy.deepcopy(self.base.args['workers']);workers[0]['novelty_items']=[{'novelty_id':r['novelty_id'],'evidence_digest':'c'*64,'authorization_digest':'b'*64}]
  with self.assertRaises(AccountingError):self.review(r,workers=workers,expected_revision=1)
 def test_closed_source_capture_is_blocked(self):
  Planilla.objects.filter(pk=self.base.payroll.pk).update(estado='CONTABILIZADA')
  with self.assertRaises(AccountingError):self.record()
 def test_private_api_strict_fields_and_successful_capture(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  def call(action,values):
   req=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),values,format='json');force_authenticate(req,user=self.base.owner);return PlanCuentaViewSet.as_view({'post':action})(req)
  data={k:v for k,v in self.args.items() if k not in ['actor','provider_id']};self.assertEqual(call('record_native_payroll_novelty',{**data,'procesada':True}).status_code,400);r=call('record_native_payroll_novelty',data);self.assertEqual(r.status_code,200,r.data);s=call('lookup_native_payroll_novelty',{'payroll_id':data['payroll_id'],'source_reference':data['source_reference']});self.assertEqual(s.status_code,200,s.data);self.assertTrue(s.data['found'])
 def test_source_catalog_includes_concepts_and_captured_references(self):
  r=self.record();s=payroll.payroll_sources(actor=self.base.owner,provider_id=self.base.provider.pk);self.assertIn(self.concept.pk,[c['id'] for c in s['concepts']]);n=next(n for n in s['novelties'] if n['id']==r['novelty_id']);self.assertTrue(n['native_source']);self.assertEqual(n['evidence_digest'],self.args['evidence_digest'])
 def test_corporate_contract_rejects_changed_capture_and_false_upload_flags(self):
  import sys
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
  from app.services.native_payroll_source_contract import validate
  data=self.record();payload={k:v for k,v in self.args.items() if k not in ['actor','provider_id']};scope={'tenant_id':str(self.base.company.pk)};validate('record_native_payroll_novelty',data,payload,scope)
  for change in [{'source_digest':'c'*64},{'company_id':str(uuid.uuid4())},{'document_uploaded':True},{'reference_digest':'d'*64}]:
   with self.assertRaises(ValueError):validate('record_native_payroll_novelty',{**data,**change},payload,scope)
  query={'payroll_id':str(self.base.payroll.pk),'source_reference':self.args['source_reference']};validate('lookup_native_payroll_novelty',self.lookup(),query,scope)
 def test_reference_lookup_cannot_switch_payroll_or_source_company(self):
  self.record();other=Planilla.objects.create(perfil_id=self.base.provider.pk,periodo_inicio=self.base.start,periodo_fin=self.base.day)
  with self.assertRaises(AccountingError):engine.lookup(actor=self.base.owner,provider_id=self.base.provider.pk,payroll_id=str(other.pk),source_reference=self.args['source_reference'])
if __name__=='__main__':unittest.main()
