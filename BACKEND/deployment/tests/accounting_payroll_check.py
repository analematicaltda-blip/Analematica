"""Declared base pay -> persisted review -> real shared-ledger accrual, isolated ORM."""
import copy,runpy,unittest,uuid
from datetime import timedelta,date
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_payroll_boundary_check.py')),run_name='reviewed_payroll_fixture')
from django.utils import timezone
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.nomina import reviewed_payroll as engine
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Planilla,Contrato,Empleado,DetalleLiquidacion,NovedadNomina,ConceptoNomina
from apps.core_erp.accounting.models import Account,JournalEntry
from apps.core_erp.accounting.reports_engine import ReportsEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from apps.turismo.models import VerifiedCompanyLink
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class PayrollChecks(unittest.TestCase):
 def setUp(self):
  self.boundary=fixture['PayrollBoundaryChecks']();self.boundary.setUp();self.owner=self.boundary.user;self.provider=self.boundary.provider
  self.recognition=self.boundary.case.case;self.company=self.recognition.case.tenant;self.payroll=self.boundary.planilla;self.employee=self.boundary.case.employee
  self.day=timezone.localdate();self.start=self.day-timedelta(days=14)
  Planilla.objects.filter(pk=self.payroll.pk).update(periodo_inicio=self.start,periodo_fin=self.day);self.payroll.refresh_from_db()
  self.recognition.period.period_start=date(self.start.year,1,1);self.recognition.period.save()
  self.contract=Contrato.objects.create(empleado=self.employee,fecha_inicio=self.start,salario='1000.00',cargo='Synthetic',tipo_contrato='TERMINO_INDEFINIDO',activo=True)
  self.mapping={}
  for i,(key,kind) in enumerate(engine.ACCOUNT_TYPES.items()):
   account=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.recognition.chart,code='PAY-'+str(i),name='Synthetic '+key,type=kind)
   self.mapping[key]=str(account.pk)
  self.policy={'code':'DECLARED_BASE','revision':1,'valid_from':self.start.isoformat(),'valid_until':self.day.isoformat(),'divisor_days':30,'evidence_digest':'a'*64,'components':[{'code':'DECLARED_DEDUCTION','kind':'EMPLOYEE_DEDUCTION','rate_bps':400},{'code':'DECLARED_EMPLOYER','kind':'EMPLOYER_CONTRIBUTION','rate_bps':1200},{'code':'DECLARED_PROVISION','kind':'PROVISION','rate_bps':800}]}
  self.args={'actor':self.owner,'provider_id':self.provider.pk,'payroll_id':self.payroll.pk,'policy':self.policy,'workers':[{'employee_id':str(self.employee.pk),'contract_id':str(self.contract.pk),'worked_days':15}],'account_mapping':self.mapping,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True}
 def review(self,**extra):return engine.review_payroll(**{**self.args,**extra})
 def post(self,review,**extra):return engine.post_payroll(**{'actor':self.owner,'provider_id':self.provider.pk,'payroll_id':self.payroll.pk,'review_id':review['review_id'],'confirmed':True,**extra})
 def test_preview_uses_contract_and_declared_rules_without_posting(self):
  review=self.review();totals=review['preview']['snapshot']['totals'];self.assertEqual(totals,{'gross':'500.00','net':'480.00','deductions':'20.00','employer':'60.00','provisions':'40.00'});self.assertFalse(review['ledger_written']);self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_real_accrual_balances_provisions_and_replay_without_payment(self):
  review=self.review();posted=self.post(review);again=self.post(review);self.assertFalse(posted['replayed']);self.assertTrue(again['replayed']);self.assertEqual(posted['journal_id'],again['journal_id']);self.assertFalse(posted['money_transferred']);self.assertFalse(posted['regulatory_verified'])
  self.payroll.refresh_from_db();self.assertEqual(self.payroll.estado,'CONTABILIZADA');self.assertEqual(self.payroll.total_neto,480);self.assertEqual(DetalleLiquidacion.objects.filter(planilla=self.payroll).count(),1)
  r=ReportsEngine.get_trial_balance(self.company.pk,self.day);self.assertEqual(str(r['total_debit']),'600.00');self.assertEqual(r['total_debit'],r['total_credit']);self.assertEqual(ReportsEngine.get_profitability(self.company.pk,self.start,self.day)['net_profit'],'-600.00')
 def test_each_confirmation_is_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  with self.assertRaises(AccountingError):self.post(self.review(),confirmed=False)
 def test_contract_salary_changed_after_review_rejects_post(self):
  review=self.review();Contrato.objects.filter(pk=self.contract.pk).update(salario='1100.00')
  with self.assertRaises(AccountingError):self.post(review)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_inactive_employee_or_closed_period_rejects(self):
  review=self.review();Empleado.objects.filter(pk=self.employee.pk).update(estado='RETIRADO')
  with self.assertRaises(AccountingError):self.post(review)
  Empleado.objects.filter(pk=self.employee.pk).update(estado='ACTIVO');self.recognition.period.status='closed';self.recognition.period.save()
  with self.assertRaises(AccountingError):self.post(review)
 def test_policy_requires_full_validity_and_exact_integer_rates(self):
  for change in [{'valid_from':self.day.isoformat()},{'divisor_days':True},{'components':[{'code':'BAD','kind':'PROVISION','rate_bps':0.5}]}]:
   with self.assertRaises((AccountingError,ValueError)):self.review(policy={**self.policy,**change})
 def test_days_beyond_economic_interval_and_duplicate_employee_rejected(self):
  workers=copy.deepcopy(self.args['workers']);workers[0]['worked_days']=16
  with self.assertRaises(AccountingError):self.review(workers=workers)
  with self.assertRaises(AccountingError):self.review(workers=self.args['workers']*2)
 def test_no_wrong_account_role_or_foreign_account(self):
  bad={**self.mapping,'salary_expense':self.mapping['employee_payable']}
  with self.assertRaises(AccountingError):self.review(account_mapping=bad)
  bad={**self.mapping,'salary_expense':str(uuid.uuid4())}
  with self.assertRaises(AccountingError):self.review(account_mapping=bad)
 def test_source_novelty_is_not_silently_ignored(self):
  concept=ConceptoNomina.objects.create(codigo=uuid.uuid4().hex[:10],descripcion='Synthetic',tipo='DEVENGADO')
  NovedadNomina.objects.create(empleado=self.employee,planilla=self.payroll,concepto=concept,valor='10.00')
  with self.assertRaises(AccountingError):self.review()
 def test_declared_policy_version_cannot_be_redefined(self):
  self.review();changed=copy.deepcopy(self.policy);changed['components'][0]['rate_bps']=500
  with self.assertRaises(AccountingError):self.review(policy=changed,expected_revision=1)
 def test_only_current_review_can_be_confirmed(self):
  first=self.review();self.review(expected_revision=1,evidence_digest='c'*64)
  with self.assertRaises(AccountingError):self.post(first)
 def test_failure_of_origin_proof_rolls_back_ledger_details_and_header(self):
  review=self.review();original=OutboxEvent.objects.create
  def create(**kwargs):
   if kwargs.get('event_type')==engine.APPLIED:raise RuntimeError('Proof failed')
   return original(**kwargs)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.post(review)
  self.payroll.refresh_from_db();self.assertEqual(self.payroll.estado,'BORRADOR');self.assertIsNone(self.payroll.asiento_contable_ref_id);self.assertFalse(DetalleLiquidacion.objects.filter(planilla=self.payroll).exists());self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_projection_tampering_blocks_replay(self):
  review=self.review();self.post(review);DetalleLiquidacion.objects.filter(planilla=self.payroll).update(total_neto='481.00')
  with self.assertRaises(AccountingError):self.post(review)
 def test_overlap_prevents_double_accrual_with_different_payroll_ids(self):
  self.post(self.review());other=Planilla.objects.create(perfil_id=self.provider.pk,periodo_inicio=self.start,periodo_fin=self.day)
  with self.assertRaises(AccountingError):self.review(payroll_id=other.pk)
 def test_state_recovers_same_journal_and_never_restores_confirmation(self):
  review=self.review();posted=self.post(review);state=engine.payroll_state(actor=self.owner,provider_id=self.provider.pk,payroll_id=self.payroll.pk)
  self.assertEqual(state['applied']['journal_id'],posted['journal_id']);self.assertFalse(state['confirmations_restored']);self.assertTrue(state['read_only'])
 def test_revoked_link_rejects_post_and_read(self):
  from rest_framework.exceptions import APIException
  review=self.review();VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.post(review)
  with self.assertRaises(APIException):engine.payroll_state(actor=self.owner,provider_id=self.provider.pk,payroll_id=self.payroll.pk)
 def test_retired_worker_after_post_preserves_intact_replay(self):
  review=self.review();posted=self.post(review);Empleado.objects.filter(pk=self.employee.pk).update(estado='RETIRADO');self.assertEqual(self.post(review)['journal_id'],posted['journal_id'])
 def test_actual_owner_scoped_api_and_private_responses(self):
  def call(action,body,method='post'):
   if method=='get':body={'provider_id':str(self.provider.pk),**body}
   request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.provider.pk),body,format='json');force_authenticate(request,user=self.owner);return PlanCuentaViewSet.as_view({method:action})(request)
  body={k:v for k,v in self.args.items() if k not in {'actor','provider_id'}};body['payroll_id']=str(body['payroll_id'])
  r=call('review_payroll',body);self.assertEqual(r.status_code,200,r.data)
  p=call('post_payroll',{'payroll_id':str(self.payroll.pk),'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(p.status_code,200,p.data);self.assertIn('no-store',p['Cache-Control'])
  state=call('payroll_state',{'payroll_id':str(self.payroll.pk)},'get');self.assertEqual(state.status_code,200,state.data);self.assertEqual(state.data['applied']['journal_id'],p.data['journal_id'])
  body['payroll_id']=str(self.boundary.foreign.pk);self.assertEqual(call('review_payroll',body).status_code,400)
 def test_absence_in_period_is_not_silently_ignored(self):
  from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Ausencia
  Ausencia.objects.create(empleado=self.employee,tipo='Synthetic',fecha_inicio=timezone.now()-timedelta(days=1),fecha_fin=timezone.now(),justificada=True)
  with self.assertRaises(AccountingError):self.review()
 def test_multiple_active_contracts_require_explicit_separate_processing(self):
  Contrato.objects.create(empleado=self.employee,fecha_inicio=self.start,salario='500.00',cargo='Second',tipo_contrato='TERMINO_INDEFINIDO',activo=True)
  with self.assertRaises(AccountingError):self.review()
 def test_prorating_half_cent_is_explicit_half_up(self):
  Contrato.objects.filter(pk=self.contract.pk).update(salario='0.01')
  args=copy.deepcopy(self.policy);args['divisor_days']=2
  workers=copy.deepcopy(self.args['workers']);workers[0]['worked_days']=1
  result=self.review(policy=args,workers=workers)
  self.assertEqual(result['preview']['snapshot']['totals']['gross'],'0.01')
  self.assertEqual(result['preview']['snapshot']['totals']['net'],'0.01')
 def test_unreconciled_initial_balances_block_new_payroll(self):
  Account.plain_objects.filter(pk=self.recognition.asset.pk).update(initial_balance='100.00')
  with self.assertRaises(AccountingError):self.review()
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
if __name__=='__main__':unittest.main()
