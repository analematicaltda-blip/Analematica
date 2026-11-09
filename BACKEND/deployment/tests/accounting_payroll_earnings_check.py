"""Exact declared overtime/surcharge -> existing payroll ledger/detail/cost sources."""
import runpy,unittest,copy,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_operational_cost_check.py')),run_name='earnings_fixture')
from apps.prestadores.mi_negocio.gestion_contable.nomina import reviewed_payroll as engine
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import DetalleLiquidacion,Contrato
from apps.prestadores.mi_negocio.gestion_contable.nomina import operational_costs
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
class PayrollEarningsChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['fixture']['PayrollChecks']();self.base.setUp();self.policy=copy.deepcopy(self.base.policy)
  self.policy.update(code='DECLARED_EARNINGS',earning_rules=[{'code':'EXTRA','kind':'OVERTIME','rate_bps':12500,'hour_divisor':200},{'code':'NIGHT','kind':'SURCHARGE','rate_bps':3500,'hour_divisor':200}])
  for r in self.policy['components']:r['basis']='GROSS'
  self.workers=copy.deepcopy(self.base.args['workers']);self.workers[0]['earnings']=[{'code':'EXTRA','minutes':120,'evidence_digest':'c'*64},{'code':'NIGHT','minutes':60,'evidence_digest':'d'*64}]
 def review(self,**kw):return self.base.review(**{'policy':self.policy,'workers':self.workers,**kw})
 def test_exact_gross_contributions_and_projection(self):
  r=self.review();snapshot=r['preview']['snapshot'];row=snapshot['workers'][0];self.assertEqual(row['base'],'500.00');self.assertEqual(row['gross'],'514.25');self.assertEqual(row['earning_totals'],{'horas_extras':'12.50','recargos':'1.75'});self.assertEqual(snapshot['totals'],{'gross':'514.25','net':'493.68','deductions':'20.57','employer':'61.71','provisions':'41.14'})
  p=self.base.post(r);self.assertFalse(p['money_transferred']);self.assertEqual(p['details_projection'],'DECLARED_EARNINGS_TOTALS');d=DetalleLiquidacion.objects.get(planilla=self.base.payroll);self.assertEqual(str(d.horas_extras),'12.50');self.assertEqual(str(d.recargos),'1.75');self.assertEqual(str(d.total_devengado),'514.25');self.assertEqual(str(d.basico),'500.00');self.assertEqual(self.base.post(r)['journal_id'],p['journal_id'])
 def test_explicit_base_contribution_basis_is_preserved(self):
  for r in self.policy['components']:r['basis']='BASE'
  s=self.review()['preview']['snapshot'];self.assertEqual(s['totals']['deductions'],'20.00');self.assertEqual(s['totals']['employer'],'60.00');self.assertEqual(s['totals']['net'],'494.25')
 def test_missing_contribution_basis_rejected(self):
  self.policy['components'][0].pop('basis')
  with self.assertRaises(AccountingError):self.review()
 def test_no_implicit_hour_divisor_or_legal_rate(self):
  for change in [{'hour_divisor':None},{'hour_divisor':True},{'rate_bps':0},{'rate_bps':12500.0},{'kind':'INFERRED_LEGAL'}]:
   policy=copy.deepcopy(self.policy);policy['earning_rules'][0].update(change)
   with self.assertRaises(AccountingError):self.review(policy=policy)
 def test_unknown_duplicate_and_boolean_minutes_rejected(self):
  for earnings in [[{**self.workers[0]['earnings'][0],'code':'UNKNOWN'}],self.workers[0]['earnings']*2,[{**self.workers[0]['earnings'][0],'minutes':True}],[{**self.workers[0]['earnings'][0],'minutes':1.5}]]:
   w=copy.deepcopy(self.workers);w[0]['earnings']=earnings
   with self.assertRaises(AccountingError):self.review(workers=w)
 def test_source_evidence_required(self):
  self.workers[0]['earnings'][0]['evidence_digest']='not-a-proof'
  with self.assertRaises(AccountingError):self.review()
 def test_total_minutes_bounded_to_period_capacity(self):
  self.workers[0]['earnings'][0]['minutes']=15*1440;self.workers[0]['earnings'][1]['minutes']=1
  with self.assertRaises(AccountingError):self.review()
 def test_rule_version_cannot_be_redefined(self):
  self.review();self.policy['earning_rules'][0]['rate_bps']=15000
  with self.assertRaises(AccountingError):self.review(expected_revision=1)
 def test_changed_contract_blocks_post_without_partial_ledger(self):
  r=self.review();Contrato.objects.filter(pk=self.base.contract.pk).update(salario='1100.00')
  with self.assertRaises(AccountingError):self.base.post(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.base.company).exists())
 def test_tampered_supplement_projection_rejected_on_recovery(self):
  r=self.review();self.base.post(r);DetalleLiquidacion.objects.filter(planilla=self.base.payroll).update(recargos='2.00')
  with self.assertRaises(AccountingError):self.base.post(r)
 def test_empty_declared_earnings_keep_base_total_without_inventing_work(self):
  self.workers[0]['earnings']=[];r=self.review();self.assertEqual(r['preview']['snapshot']['totals']['gross'],'500.00');self.base.post(r)
 def test_operational_source_includes_posted_supplemental_salary(self):
  self.base.post(self.review());s=operational_costs.cost_sources(actor=self.base.owner,provider_id=self.base.provider.pk,payroll_id=self.base.payroll.pk);self.assertEqual(s['workers'][0]['salary'],'514.25')
 def test_operational_allocation_includes_entire_posted_salary_cost(self):
  from datetime import datetime,time,timedelta
  from zoneinfo import ZoneInfo
  from apps.prestadores.mi_negocio.gestion_operativa.models import OrdenOperativa
  from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data_service import record_work
  self.base.post(self.review());start=datetime.combine(self.base.day-timedelta(days=1),time(9),ZoneInfo('America/Bogota'));end=start+timedelta(hours=8)
  order=OrdenOperativa.objects.create(provider_id=self.base.provider.pk,contrato_ref_id=uuid.uuid4(),descripcion_servicio='Synthetic supplement cost',fecha_inicio=start,fecha_fin_estimada=end)
  record_work(actor_id=self.base.owner.pk,provider_id=self.base.provider.pk,employee_id=str(self.base.employee.pk),request_id=str(uuid.uuid4()),expected_revision=0,evidence_digest='e'*64,started_at=start.isoformat(),ended_at=end.isoformat(),operation_reference=str(order.pk),confirmed=True)
  scope={'actor':self.base.owner,'provider_id':self.base.provider.pk,'payroll_id':self.base.payroll.pk}
  r=operational_costs.review_costs(**scope,capacities=[{'employee_id':str(self.base.employee.pk),'capacity_seconds':28800}],operation_centers={str(order.pk):'SUPPLEMENT'},evidence_digest='f'*64,reason_code='INITIAL',expected_revision=0,confirmed=True)
  self.assertEqual(r['preview']['posted_total_cost'],'617.10');self.assertEqual(r['preview']['allocations'][0]['total_cost'],'617.10');self.assertEqual(r['preview']['unallocated'][0]['total_cost'],'0.00')
  operational_costs.record_costs(**scope,review_id=r['review_id'],confirmed=True);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.company).count(),1)
 def test_second_payroll_cannot_accrue_same_employee_period(self):
  from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Planilla
  self.base.post(self.review());other=Planilla.objects.create(perfil_id=self.base.provider.pk,periodo_inicio=self.base.start,periodo_fin=self.base.day)
  with self.assertRaises(AccountingError):self.review(payroll_id=other.pk)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.company).count(),1)
 def test_two_previously_reviewed_drafts_recheck_overlap_on_post(self):
  from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Planilla
  first=self.review();other=Planilla.objects.create(perfil_id=self.base.provider.pk,periodo_inicio=self.base.start,periodo_fin=self.base.day);second=self.review(payroll_id=other.pk)
  posted=self.base.post(first)
  with self.assertRaises(AccountingError):self.base.post(second,payroll_id=other.pk)
  self.assertEqual(self.base.post(first)['journal_id'],posted['journal_id']);other.refresh_from_db();self.assertEqual(other.estado,'BORRADOR');self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.company).count(),1)
 def test_each_confirmation_still_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  with self.assertRaises(AccountingError):self.base.post(self.review(),confirmed=False)
if __name__=='__main__':unittest.main()
