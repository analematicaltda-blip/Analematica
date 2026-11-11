"""Declared fixed deductions reconcile net salary, liabilities, history and costs."""
import runpy,unittest,copy
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_payroll_earnings_check.py')),run_name='deductions_fixture')
from apps.prestadores.mi_negocio.gestion_contable.nomina import reviewed_payroll as engine
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import DetalleLiquidacion
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
class DeductionChecks(unittest.TestCase):
 def setUp(self):
  self.earnings=fixture['PayrollEarningsChecks']();self.earnings.setUp();self.base=self.earnings.base;self.policy=copy.deepcopy(self.base.policy);self.policy['code']='FIXED_LIABILITY';self.policy['fixed_deduction_rules']=[{'code':'OTHER_FIXED','kind':'FIXED_EMPLOYEE_LIABILITY'}];self.workers=copy.deepcopy(self.base.args['workers']);self.workers[0]['fixed_deductions']=[{'code':'OTHER_FIXED','amount':'25.00','evidence_digest':'d'*64,'authorization_digest':'e'*64}]
 def review(self,**kw):return self.base.review(**{'policy':self.policy,'workers':self.workers,**kw})
 def test_exact_net_and_liability_post_replay(self):
  r=self.review();s=r['preview']['snapshot'];w=s['workers'][0];self.assertEqual(s['totals']['deductions'],'45.00');self.assertEqual(s['totals']['net'],'455.00');self.assertEqual(w['percentage_deductions'],'20.00');self.assertEqual(w['fixed_deductions_total'],'25.00');self.assertFalse(w['fixed_deductions'][0]['authorization_independently_verified']);a=self.base.post(r);self.assertEqual(self.base.post(r)['journal_id'],a['journal_id']);d=DetalleLiquidacion.objects.get(planilla=self.base.payroll);self.assertEqual(str(d.total_neto),'455.00');self.assertEqual(str(d.total_deduccion),'45.00');self.assertFalse(a['money_transferred']);self.assertEqual(format(LedgerEntry.plain_objects.get(journal_entry_id=a['journal_id'],account_id=self.base.args['account_mapping']['deductions_payable']).credit_amount,'.2f'),'45.00');self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.company).count(),1)
 def test_combines_earnings_without_changing_contribution_base_or_cost(self):
  self.policy=copy.deepcopy(self.earnings.policy);self.policy.update(code='FIXED_AND_EARNINGS',fixed_deduction_rules=[{'code':'OTHER_FIXED','kind':'FIXED_EMPLOYEE_LIABILITY'}]);self.workers[0]['earnings']=self.earnings.workers[0]['earnings'];r=self.review();s=r['preview']['snapshot'];self.assertEqual(s['totals']['gross'],'514.25');self.assertEqual(s['totals']['deductions'],'45.57');self.assertEqual(s['totals']['net'],'468.68');self.assertEqual(s['totals']['employer'],'61.71');self.base.post(r)
 def test_over_net_fractional_float_zero_negative_or_nonfinite_rejected(self):
  for value in ['480.01','1.001',1.0,'0.00','-1.00','NaN']:
   w=copy.deepcopy(self.workers);w[0]['fixed_deductions'][0]['amount']=value
   with self.assertRaises((AccountingError,ValueError)):self.review(workers=w)
 def test_unknown_duplicate_missing_authorization_or_support_rejected(self):
  for mutate in [lambda d:d.update(code='UNKNOWN'),lambda d:d.pop('authorization_digest'),lambda d:d.update(authorization_digest='bad'),lambda d:d.update(evidence_digest='bad')]:
   w=copy.deepcopy(self.workers);mutate(w[0]['fixed_deductions'][0])
   with self.assertRaises((AccountingError,ValueError)):self.review(workers=w)
  w=copy.deepcopy(self.workers);w[0]['fixed_deductions']*=2
  with self.assertRaises(AccountingError):self.review(workers=w)
 def test_zero_net_is_exact_and_empty_optional_list_has_no_deduction(self):
  self.workers[0]['fixed_deductions'][0]['amount']='480.00';self.assertEqual(self.review()['preview']['snapshot']['totals']['net'],'0.00');self.workers[0]['fixed_deductions']=[];self.assertEqual(self.review(expected_revision=1)['preview']['snapshot']['totals']['net'],'480.00')
 def test_cannot_redefine_policy_version_or_reuse_component_code(self):
  self.review();p=copy.deepcopy(self.policy);p['fixed_deduction_rules'][0]['code']='CHANGED'
  with self.assertRaises(AccountingError):self.review(policy=p,expected_revision=1)
  p=copy.deepcopy(self.policy);p['fixed_deduction_rules'][0]['code']=p['components'][0]['code']
  with self.assertRaises(AccountingError):self.review(policy=p,expected_revision=1)
 def test_second_confirmation_required_and_projection_tampering_blocks_recovery(self):
  r=self.review()
  with self.assertRaises(AccountingError):self.base.post(r,confirmed=False)
  self.base.post(r);DetalleLiquidacion.objects.filter(planilla=self.base.payroll).update(total_deduccion='46.00')
  with self.assertRaises(AccountingError):self.base.post(r)
 def test_corporate_contract_rejects_altered_amount_authorization_and_worker(self):
  import sys
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
  from app.services.payroll_deduction_contract import validate
  s=self.review()['preview']['snapshot'];requested={'policy':self.policy,'workers':self.workers};validate(s,requested)
  for mutate in [lambda w:w['fixed_deductions'][0].update(amount='26.00'),lambda w:w['fixed_deductions'][0].update(authorization_independently_verified=True),lambda w:w['fixed_deductions'][0].update(authorization_digest='f'*64),lambda w:w.update(net='456.00')]:
   changed=copy.deepcopy(s);mutate(changed['workers'][0])
   with self.assertRaises(ValueError):validate(changed,requested)
 def test_failure_after_posting_rolls_back_before_retry(self):
  r=self.review();original=DetalleLiquidacion.objects.create
  with patch.object(DetalleLiquidacion.objects,'create',side_effect=RuntimeError('Synthetic detail failure')):
   with self.assertRaises(RuntimeError):self.base.post(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.base.company).exists());self.base.post(r)
 def test_actual_owner_scoped_api_posts_declared_deductions(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  payload={**self.base.args,'policy':self.policy,'workers':self.workers};payload.pop('actor',None);payload.pop('provider_id',None)
  req=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),payload,format='json');force_authenticate(req,user=self.base.owner)
  r=PlanCuentaViewSet.as_view({'post':'review_payroll'})(req);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['preview']['snapshot']['totals']['net'],'455.00')
 def test_fixed_deductions_do_not_reduce_gross_operational_cost_source(self):
  from apps.prestadores.mi_negocio.gestion_contable.nomina import operational_costs
  self.base.post(self.review());s=operational_costs.cost_sources(actor=self.base.owner,provider_id=self.base.provider.pk,payroll_id=self.base.payroll.pk);w=s['workers'][0];self.assertEqual(w['salary'],'500.00');self.assertEqual(w['employer'],'60.00');self.assertEqual(w['provisions'],'40.00')
if __name__=='__main__':unittest.main()
