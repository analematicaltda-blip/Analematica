"""Existing bonus/commission/deduction sources -> gross, net, ledger and costs."""
import copy,runpy,unittest,uuid,sys
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_operational_cost_check.py')),run_name='compensation_fixture')
from apps.prestadores.mi_negocio.gestion_contable.nomina import reviewed_payroll as engine,reviewed_novelties as source,operational_costs
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import ConceptoNomina,NovedadNomina,DetalleLiquidacion
from apps.core_erp.accounting.models import LedgerEntry,JournalEntry
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
class CompensationChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['fixture']['PayrollChecks']();self.base.setUp();self.policy=copy.deepcopy(self.base.policy);self.policy.update(code='SOURCE_COMPENSATION',novelty_mode=source.COMPENSATION_MODE);self.workers=copy.deepcopy(self.base.args['workers']);self.workers[0]['novelty_items']=[];self.sources=[];self.rules=[]
  for field,amount in [('bonificaciones','50.00'),('comisiones','30.00')]:
   concept=ConceptoNomina.objects.create(codigo=uuid.uuid4().hex[:10],descripcion='Synthetic '+field,tipo='DEVENGADO');row=NovedadNomina.objects.create(empleado=self.base.employee,concepto=concept,fecha_evento=self.base.day,valor=amount,cantidad='1.00');self.sources.append(row);self.rules.append({'concept_id':concept.pk,'detail_field':field});self.workers[0]['novelty_items'].append({'novelty_id':row.pk,'evidence_digest':'e'*64,'authorization_digest':'f'*64})
  concept=ConceptoNomina.objects.create(codigo=uuid.uuid4().hex[:10],descripcion='Synthetic fixed liability',tipo='DEDUCCION');row=NovedadNomina.objects.create(empleado=self.base.employee,concepto=concept,fecha_evento=self.base.day,valor='25.00',cantidad='1.00');self.sources.insert(0,row);self.workers[0]['novelty_items'].append({'novelty_id':row.pk,'evidence_digest':'c'*64,'authorization_digest':'d'*64})
  self.policy['source_earning_rules']=self.rules
  for c in self.policy['components']:c['basis']='GROSS'
 def review(self,**kw):return self.base.review(**{'policy':self.policy,'workers':self.workers,**kw})
 def test_full_compensation_post_consumption_recovery_and_cost_source(self):
  r=self.review();s=r['preview']['snapshot'];w=s['workers'][0];self.assertEqual(s['totals'],{'gross':'580.00','net':'531.80','deductions':'48.20','employer':'69.60','provisions':'46.40'});self.assertEqual(w['source_earning_totals'],{'bonificaciones':'50.00','comisiones':'30.00'});a=self.base.post(r);self.assertEqual(self.base.post(r)['journal_id'],a['journal_id']);d=DetalleLiquidacion.objects.get(planilla=self.base.payroll);self.assertEqual(str(d.bonificaciones),'50.00');self.assertEqual(str(d.comisiones),'30.00');self.assertEqual(str(d.total_devengado),'580.00');self.assertEqual(OutboxEvent.objects.filter(event_type=source.KIND,payload__company_id=str(self.base.company.pk)).count(),3)
  self.assertEqual(format(LedgerEntry.plain_objects.get(journal_entry_id=a['journal_id'],account_id=self.base.args['account_mapping']['salary_expense']).debit_amount,'.2f'),'580.00')
  costs=operational_costs.cost_sources(actor=self.base.owner,provider_id=self.base.provider.pk,payroll_id=self.base.payroll.pk);self.assertEqual(costs['workers'][0]['salary'],'580.00');self.assertEqual(costs['workers'][0]['employer'],'69.60');self.assertEqual(costs['workers'][0]['provisions'],'46.40')
  for row in self.sources:row.refresh_from_db();self.assertTrue(row.procesada)
 def test_explicit_base_basis_excludes_supplements_from_declared_contributions(self):
  for c in self.policy['components']:c['basis']='BASE'
  s=self.review()['preview']['snapshot'];self.assertEqual(s['totals']['gross'],'580.00');self.assertEqual(s['totals']['deductions'],'45.00');self.assertEqual(s['totals']['net'],'535.00');self.assertEqual(s['totals']['employer'],'60.00')
 def test_missing_basis_unknown_concept_or_unsupported_classification_rejected(self):
  for mutate in [lambda p:p['components'][0].pop('basis'),lambda p:p['source_earning_rules'].pop(),lambda p:p['source_earning_rules'][0].update(detail_field='auxilio_transporte'),lambda p:p.update(source_earning_rules=[])]:
   policy=copy.deepcopy(self.policy);mutate(policy)
   with self.assertRaises(AccountingError):self.review(policy=policy)
 def test_legacy_deduction_mode_still_blocks_unclassified_earnings(self):
  p=copy.deepcopy(self.policy);p['novelty_mode']=source.MODE;p.pop('source_earning_rules');[c.pop('basis') for c in p['components']];w=copy.deepcopy(self.workers);w[0]['novelty_deductions']=w[0].pop('novelty_items')
  with self.assertRaises(AccountingError):self.review(policy=p,workers=w)
 def test_classification_cannot_redefine_existing_policy_version(self):
  self.review();p=copy.deepcopy(self.policy);p['source_earning_rules'][0]['detail_field']='comisiones'
  with self.assertRaises(AccountingError):self.review(policy=p,expected_revision=1)
 def test_changed_bonus_after_review_blocks_all_posting_and_consumption(self):
  r=self.review();NovedadNomina.objects.filter(pk=self.sources[1].pk).update(valor='51.00')
  with self.assertRaises(AccountingError):self.base.post(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.base.company).exists());self.assertFalse(NovedadNomina.objects.filter(pk__in=[x.pk for x in self.sources],procesada=True).exists())
 def test_partial_claim_failure_rolls_back_all_three_sources_and_journal(self):
  r=self.review();create=OutboxEvent.objects.create;count=0
  def fail(**kw):
   nonlocal count
   if kw.get('event_type')==source.KIND:
    count+=1
    if count==2:raise RuntimeError('Synthetic second claim failure')
   return create(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.base.post(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.base.company).exists());self.assertFalse(NovedadNomina.objects.filter(pk__in=[x.pk for x in self.sources],procesada=True).exists());self.base.post(r)
 def test_projection_tampering_is_rejected(self):
  r=self.review();self.base.post(r);DetalleLiquidacion.objects.filter(planilla=self.base.payroll).update(comisiones='31.00')
  with self.assertRaises(AccountingError):self.base.post(r)
 def test_corporate_contract_rejects_earning_field_gross_and_basis_tampering(self):
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
  from app.services.payroll_deduction_contract import validate
  s=self.review()['preview']['snapshot'];request={'policy':self.policy,'workers':self.workers};validate(s,request)
  for mutate in [lambda w:w['novelty_items'][0].update(earning_field='comisiones'),lambda w:w.update(gross='581.00'),lambda w:w['source_earning_totals'].update(bonificaciones='51.00'),lambda w:w['components'][0].update(calculation_basis='BASE')]:
   bad=copy.deepcopy(s);mutate(bad['workers'][0])
   with self.assertRaises(ValueError):validate(bad,request)
 def test_combined_timed_and_registered_earnings_have_exact_gross_and_costs(self):
  self.policy['earning_rules']=[{'code':'EXTRA','kind':'OVERTIME','rate_bps':12500,'hour_divisor':200},{'code':'NIGHT','kind':'SURCHARGE','rate_bps':3500,'hour_divisor':200}];self.workers[0]['earnings']=[{'code':'EXTRA','minutes':120,'evidence_digest':'c'*64},{'code':'NIGHT','minutes':60,'evidence_digest':'d'*64}]
  r=self.review();self.assertEqual(r['preview']['snapshot']['totals'],{'gross':'594.25','net':'545.48','deductions':'48.77','employer':'71.31','provisions':'47.54'});self.base.post(r);d=DetalleLiquidacion.objects.get(planilla=self.base.payroll);self.assertEqual(str(d.horas_extras),'12.50');self.assertEqual(str(d.bonificaciones),'50.00');self.assertEqual(str(d.comisiones),'30.00')
 def test_actual_owner_scoped_api_reviews_and_posts_source_earnings(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  def call(action,data):
   req=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),data,format='json');force_authenticate(req,user=self.base.owner);return PlanCuentaViewSet.as_view({'post':action})(req)
  p={**self.base.args,'policy':self.policy,'workers':self.workers};p.pop('actor',None);p.pop('provider_id',None);r=call('review_payroll',p);self.assertEqual(r.status_code,200,r.data);a=call('post_payroll',{'payroll_id':str(self.base.payroll.pk),'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(a.status_code,200,a.data);self.assertEqual(a.data['details_projection'],'DECLARED_SOURCE_EARNINGS_TOTALS')
if __name__=='__main__':unittest.main()
