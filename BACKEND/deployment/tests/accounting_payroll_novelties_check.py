"""Existing deduction sources consumed exactly once with ledger and payroll detail."""
import copy,runpy,unittest,uuid,sys
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_payroll_check.py')),run_name='novelty_fixture')
from apps.prestadores.mi_negocio.gestion_contable.nomina import reviewed_payroll as engine,reviewed_novelties as source
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import NovedadNomina,ConceptoNomina,DetalleLiquidacion,Planilla
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.exceptions import AccountingError
class NoveltyChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['PayrollChecks']();self.base.setUp();self.policy={**copy.deepcopy(self.base.policy),'code':'NOVELTY_SOURCE','novelty_mode':source.MODE};self.workers=copy.deepcopy(self.base.args['workers']);self.concept=ConceptoNomina.objects.create(codigo=uuid.uuid4().hex[:10],descripcion='Synthetic fixed liability',tipo='DEDUCCION');self.novelty=NovedadNomina.objects.create(empleado=self.base.employee,planilla=None,concepto=self.concept,fecha_evento=self.base.day,valor='25.00',cantidad='1.00',descripcion='PRIVATE-SOURCE-TEXT');self.workers[0]['novelty_deductions']=[{'novelty_id':self.novelty.pk,'evidence_digest':'c'*64,'authorization_digest':'d'*64}]
 def review(self,**kw):return self.base.review(**{'policy':self.policy,'workers':self.workers,**kw})
 def test_existing_source_to_net_liability_consumption_and_replay(self):
  r=self.review();w=r['preview']['snapshot']['workers'][0];self.assertEqual(w['novelty_deductions_total'],'25.00');self.assertEqual(w['net'],'455.00');self.assertNotIn('PRIVATE-SOURCE-TEXT',str(r));self.novelty.refresh_from_db();self.assertFalse(self.novelty.procesada);a=self.base.post(r);self.novelty.refresh_from_db();self.assertTrue(self.novelty.procesada);self.assertEqual(self.novelty.planilla_id,self.base.payroll.pk);self.assertEqual(self.base.post(r)['journal_id'],a['journal_id']);self.assertEqual(format(LedgerEntry.plain_objects.get(journal_entry_id=a['journal_id'],account_id=self.base.args['account_mapping']['deductions_payable']).credit_amount,'.2f'),'45.00');self.assertEqual(OutboxEvent.objects.filter(pk=source.key(self.base.company,self.novelty.pk)).count(),1);self.assertNotIn(self.novelty.pk,[n['id'] for n in engine.payroll_sources(actor=self.base.owner,provider_id=self.base.provider.pk)['novelties']])
 def test_legacy_mode_still_blocks_unreviewed_novelties(self):
  with self.assertRaises(AccountingError):self.base.review()
 def test_omitted_duplicate_unknown_and_missing_authorization_rejected(self):
  for values in [[],self.workers[0]['novelty_deductions']*2,[{'novelty_id':9007199254740991,'evidence_digest':'c'*64,'authorization_digest':'d'*64}],[{'novelty_id':self.novelty.pk,'evidence_digest':'c'*64}]]:
   w=copy.deepcopy(self.workers);w[0]['novelty_deductions']=values
   with self.assertRaises((AccountingError,ValueError)):self.review(workers=w)
 def test_changed_source_or_concept_after_review_rejects_without_partial_ledger(self):
  r=self.review();NovedadNomina.objects.filter(pk=self.novelty.pk).update(valor='26.00')
  with self.assertRaises(AccountingError):self.base.post(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.base.company).exists())
 def test_added_novelty_after_review_cannot_be_silently_ignored(self):
  r=self.review();NovedadNomina.objects.create(empleado=self.base.employee,planilla=self.base.payroll,concepto=self.concept,fecha_evento=self.base.day,valor='5.00',cantidad='1.00')
  with self.assertRaises(AccountingError):self.base.post(r)
 def test_unsupported_quantity_earning_date_or_processed_state_rejected(self):
  for change in [{'cantidad':'2.00'},{'fecha_evento':None},{'procesada':True},{'valor':'-1.00'}]:
   NovedadNomina.objects.filter(pk=self.novelty.pk).update(**change)
   with self.assertRaises(AccountingError):self.review()
   NovedadNomina.objects.filter(pk=self.novelty.pk).update(cantidad='1.00',fecha_evento=self.base.day,procesada=False,valor='25.00')
  ConceptoNomina.objects.filter(pk=self.concept.pk).update(tipo='DEVENGADO')
  with self.assertRaises(AccountingError):self.review()
 def test_rollback_restores_source_detail_and_journal_when_claim_write_fails(self):
  r=self.review();create=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==source.KIND:raise RuntimeError('Synthetic consumption proof failure')
   return create(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.base.post(r)
  self.novelty.refresh_from_db();self.assertFalse(self.novelty.procesada);self.assertIsNone(self.novelty.planilla_id);self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.base.company).exists());self.assertFalse(DetalleLiquidacion.objects.filter(planilla=self.base.payroll).exists());self.base.post(r)
 def test_consumed_source_tampering_or_missing_proof_blocks_recovery(self):
  r=self.review();self.base.post(r);NovedadNomina.objects.filter(pk=self.novelty.pk).update(procesada=False)
  with self.assertRaises(AccountingError):self.base.post(r)
  NovedadNomina.objects.filter(pk=self.novelty.pk).update(procesada=True);OutboxEvent.objects.filter(pk=source.key(self.base.company,self.novelty.pk))._raw_delete('default')
  with self.assertRaises(AccountingError):self.base.post(r)
 def test_fixed_manual_mode_cannot_double_count_source_mode(self):
  p={**self.policy,'fixed_deduction_rules':[{'code':'FIXED','kind':'FIXED_EMPLOYEE_LIABILITY'}]}
  with self.assertRaises(AccountingError):self.review(policy=p)
 def test_catalog_has_source_metadata_but_no_private_description(self):
  s=engine.payroll_sources(actor=self.base.owner,provider_id=self.base.provider.pk);n=next(n for n in s['novelties'] if n['id']==self.novelty.pk);self.assertEqual(n['amount'],'25.00');self.assertNotIn('PRIVATE-SOURCE-TEXT',str(s));self.assertNotIn('authorization_digest',n)
 def test_second_confirmation_is_required_before_source_consumption(self):
  r=self.review()
  with self.assertRaises(AccountingError):self.base.post(r,confirmed=False)
  self.novelty.refresh_from_db();self.assertFalse(self.novelty.procesada)
 def test_corporate_contract_rejects_changed_source_amount_authorization_and_digest(self):
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
  from app.services.payroll_deduction_contract import validate
  s=self.review()['preview']['snapshot'];requested={'policy':self.policy,'workers':self.workers};validate(s,requested)
  for mutate in [lambda d:d.update(amount='26.00'),lambda d:d.update(source_digest='a'*64),lambda d:d.update(authorization_independently_verified=True),lambda d:d['source'].update(employee_id=str(uuid.uuid4()))]:
   bad=copy.deepcopy(s);mutate(bad['workers'][0]['novelty_deductions'][0])
   with self.assertRaises(ValueError):validate(bad,requested)
 def test_unknown_processed_source_cannot_be_reclaimed_by_resetting_flag(self):
  r=self.review();self.base.post(r);NovedadNomina.objects.filter(pk=self.novelty.pk).update(procesada=False,planilla=None)
  with self.assertRaises(AccountingError):self.review(expected_revision=1)
 def test_foreign_company_novelty_cannot_be_selected_or_listed(self):
  other=fixture['PayrollChecks']();other.setUp();foreign=NovedadNomina.objects.create(empleado=other.employee,concepto=self.concept,fecha_evento=self.base.day,valor='7.00',cantidad='1.00')
  w=copy.deepcopy(self.workers);w[0]['novelty_deductions'][0]['novelty_id']=foreign.pk
  with self.assertRaises(AccountingError):self.review(workers=w)
  catalog=engine.payroll_sources(actor=self.base.owner,provider_id=self.base.provider.pk);self.assertNotIn(foreign.pk,[n['id'] for n in catalog['novelties']])
 def test_novelty_assigned_to_other_payroll_or_outside_dates_rejected(self):
  from datetime import timedelta
  other=Planilla.objects.create(perfil_id=self.base.provider.pk,periodo_inicio=self.base.start,periodo_fin=self.base.day)
  NovedadNomina.objects.filter(pk=self.novelty.pk).update(planilla=other)
  with self.assertRaises(AccountingError):self.review()
  NovedadNomina.objects.filter(pk=self.novelty.pk).update(planilla=None,fecha_evento=self.base.day+timedelta(days=1))
  with self.assertRaises(AccountingError):self.review()
 def test_more_than_eight_sources_cannot_be_silently_truncated(self):
  for _ in range(8):NovedadNomina.objects.create(empleado=self.base.employee,concepto=self.concept,fecha_evento=self.base.day,valor='1.00',cantidad='1.00')
  with self.assertRaises(AccountingError):self.review()
 def test_actual_private_api_review_and_consumption(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  def call(action,data):
   req=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),data,format='json');force_authenticate(req,user=self.base.owner);return PlanCuentaViewSet.as_view({'post':action})(req)
  payload={**self.base.args,'policy':self.policy,'workers':self.workers};payload.pop('actor',None);payload.pop('provider_id',None)
  r=call('review_payroll',payload);self.assertEqual(r.status_code,200,r.data);a=call('post_payroll',{'payroll_id':str(self.base.payroll.pk),'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(a.status_code,200,a.data);self.novelty.refresh_from_db();self.assertTrue(self.novelty.procesada)
 def test_source_already_assigned_to_selected_payroll_is_preserved(self):
  NovedadNomina.objects.filter(pk=self.novelty.pk).update(planilla=self.base.payroll)
  r=self.review();d=r['preview']['snapshot']['workers'][0]['novelty_deductions'][0];self.assertEqual(d['source']['payroll_id'],str(self.base.payroll.pk));self.base.post(r);self.assertEqual(self.base.post(r)['journal_id'],self.base.post(r)['journal_id'])
if __name__=='__main__':unittest.main()
