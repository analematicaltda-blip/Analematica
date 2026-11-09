"""Actual posted payroll + immutable work -> reviewed analytical operational costs."""
import runpy,unittest,uuid,copy
from pathlib import Path
from datetime import datetime,time,timedelta
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_payroll_check.py')),run_name='operational_cost_fixture')
from apps.prestadores.mi_negocio.gestion_contable.nomina import operational_costs as engine
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst import worker_data_service as work
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data import ProfessionalAuthorization,PPEAssignment,WorkPeriod,WorkPeriodEnd,RestPeriod,SafetyRevocation
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data_guards import install
from apps.prestadores.mi_negocio.gestion_operativa.models import OrdenOperativa
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from apps.turismo.models import VerifiedCompanyLink
from rest_framework.test import APIRequestFactory,force_authenticate
from rest_framework.exceptions import APIException
from django.db import connection
create=fixture['fixture']['fixture']['fixture']['create']
for model in [ProfessionalAuthorization,PPEAssignment,WorkPeriod,WorkPeriodEnd,RestPeriod,SafetyRevocation,OrdenOperativa]:create(model)
install(connection)
class OperationalCostChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['PayrollChecks']();self.base.setUp();self.actor=self.base.owner;self.provider=self.base.provider;self.company=self.base.company;self.employee=self.base.employee;self.payroll=self.base.payroll
  self.posted=self.base.post(self.base.review());self.day=self.base.day-timedelta(days=1);self.start=datetime.combine(self.day,time(9),engine.BOGOTA)
  self.orders=[OrdenOperativa.objects.create(provider_id=self.provider.pk,contrato_ref_id=uuid.uuid4(),descripcion_servicio='Synthetic operation '+str(i),fecha_inicio=self.start+timedelta(hours=i*2),fecha_fin_estimada=self.start+timedelta(hours=i*2+2)) for i in range(2)]
  self.scope={'actor':self.actor,'provider_id':self.provider.pk,'payroll_id':self.payroll.pk}
  self.capacities=[{'employee_id':str(self.employee.pk),'capacity_seconds':28800}];self.centers={str(row.pk):'SYNTHETIC_'+str(i) for i,row in enumerate(self.orders)}
  self.add_work(self.start,self.start+timedelta(hours=2),self.orders[0]);self.add_work(self.start+timedelta(hours=2),self.start+timedelta(hours=4),self.orders[1])
 def add_work(self,start,end,order=None):
  revision=WorkPeriod.objects.filter(provider_id=self.provider.pk,employee=self.employee).count()
  return work.record_work(actor_id=self.actor.pk,provider_id=self.provider.pk,employee_id=str(self.employee.pk),request_id=str(uuid.uuid4()),expected_revision=revision,evidence_digest='a'*64,started_at=start.isoformat(),ended_at=end.isoformat() if end else None,operation_reference=str(order.pk) if order else None,confirmed=True)
 def review(self,**extra):return engine.review_costs(**self.scope,**{'capacities':self.capacities,'operation_centers':self.centers,'evidence_digest':'b'*64,'reason_code':'INITIAL','expected_revision':0,'confirmed':True,**extra})
 def record(self,r,**extra):return engine.record_costs(**self.scope,**{'review_id':r['review_id'],'confirmed':True,**extra})
 def state(self):return engine.cost_state(**self.scope)
 def report(self,order=None):return engine.operation_cost_report(actor=self.actor,provider_id=self.provider.pk,order_id=str((order or self.orders[0]).pk),since=self.base.start.isoformat(),until=self.base.day.isoformat())
 def test_review_preserves_unallocated_cost_and_original_expense(self):
  r=self.review();p=r['preview'];self.assertEqual(p['posted_total_cost'],'600.00');self.assertEqual([a['total_cost'] for a in p['allocations']],['150.00','150.00']);self.assertEqual(p['unallocated'][0]['total_cost'],'300.00');self.assertEqual(p['coverage'][0]['missing_capacity_evidence_us'],14400000000);self.assertFalse(r['ledger_written']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1)
 def test_two_confirmations_record_once_without_new_journal_or_order_overwrite(self):
  r=self.review();a=self.record(r);b=self.record(r);self.assertTrue(b['replayed']);self.assertEqual(a['allocation_id'],b['allocation_id']);self.assertTrue(b['source_current']);self.assertFalse(a['ledger_written']);self.assertFalse(a['money_transferred']);self.assertEqual(self.report()['total_cost'],'150.00');self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1)
  self.orders[0].refresh_from_db();self.assertEqual(self.orders[0].costo_real_acumulado,0);self.assertEqual(self.orders[0].estado,'PENDIENTE')
 def test_each_confirmation_is_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  with self.assertRaises(AccountingError):self.record(self.review(),confirmed=False)
 def test_missing_or_duplicate_capacity_cannot_change_denominator(self):
  for caps in [[],self.capacities*2,[{'employee_id':str(uuid.uuid4()),'capacity_seconds':28800}],[{'employee_id':str(self.employee.pk),'capacity_seconds':True}]]:
   with self.assertRaises(AccountingError):self.review(capacities=caps)
 def test_excess_work_is_not_hidden_in_declared_capacity(self):
  with self.assertRaises(AccountingError):self.review(capacities=[{'employee_id':str(self.employee.pk),'capacity_seconds':3600}])
 def test_new_work_after_review_blocks_record_and_requires_new_review(self):
  r=self.review();self.add_work(self.start+timedelta(hours=5),self.start+timedelta(hours=6),self.orders[0])
  with self.assertRaises(AccountingError):self.record(r)
  self.record(self.review(expected_revision=1));self.assertEqual(self.report()['total_cost'],'225.00')
 def test_late_work_marks_old_allocation_incomplete_instead_of_false_total(self):
  self.record(self.review());self.add_work(self.start+timedelta(hours=5),self.start+timedelta(hours=6),self.orders[0]);r=self.report();self.assertIsNone(r['total_cost']);self.assertFalse(r['source_complete']);self.assertFalse(self.state()['recorded']['source_current'])
 def test_new_revision_replaces_analytical_totals_without_double_counting(self):
  self.record(self.review());self.add_work(self.start+timedelta(hours=5),self.start+timedelta(hours=6),self.orders[0]);self.record(self.review(expected_revision=1,reason_code='LATE_WORK'));self.assertEqual(self.report()['total_cost'],'225.00');self.assertEqual(len(self.report()['lines']),1);self.assertEqual(OutboxEvent.objects.filter(event_type=engine.RECORDED,payload__company_id=str(self.company.pk)).count(),2)
 def test_overlap_and_open_work_cannot_be_treated_as_complete(self):
  self.add_work(self.start+timedelta(minutes=30),self.start+timedelta(hours=1),self.orders[0])
  with self.assertRaises(AccountingError):self.review()
 def test_open_period_can_be_closed_by_append_only_closure(self):
  r=self.add_work(self.start+timedelta(hours=5),None,self.orders[0])
  with self.assertRaises(AccountingError):self.review()
  work.close_work(actor_id=self.actor.pk,provider_id=self.provider.pk,employee_id=str(self.employee.pk),request_id=str(uuid.uuid4()),expected_revision=0,evidence_digest='c'*64,work_period_id=r['record_id'],ended_at=(self.start+timedelta(hours=6)).isoformat(),confirmed=True)
  self.assertEqual(self.review()['preview']['allocations'][0]['operation_id'] in self.centers,True)
 def test_unassigned_work_and_missing_time_remain_unallocated(self):
  self.add_work(self.start+timedelta(hours=5),self.start+timedelta(hours=6));p=self.review()['preview'];self.assertEqual(p['unallocated'][0]['total_cost'],'300.00');self.assertEqual(p['coverage'][0]['recorded_unassigned_work_us'],3600000000);self.assertEqual(p['coverage'][0]['missing_capacity_evidence_us'],10800000000)
 def test_boundary_work_is_clipped_exactly_to_colombian_payroll_period(self):
  boundary=datetime.combine(self.base.start,time.min,engine.BOGOTA);self.add_work(boundary-timedelta(hours=1),boundary+timedelta(hours=1),self.orders[0]);p=self.review()['preview'];row=next(r for r in p['work_source'] if datetime.fromisoformat(r['started_at'])==boundary-timedelta(hours=1));self.assertEqual(row['duration_us'],3600000000)
 def test_center_keys_must_match_all_recorded_operations(self):
  for centers in [{}, {str(self.orders[0].pk):'ONE'}, {**self.centers,str(uuid.uuid4()):'FOREIGN'}]:
   with self.assertRaises(AccountingError):self.review(operation_centers=centers)
 def test_reversed_payroll_cannot_support_current_cost(self):
  self.record(self.review());LedgerEngine.reverse_entry(self.posted['journal_id'],tenant_id=self.company.pk,actor=self.actor);self.assertFalse(self.state()['recorded']['effective_for_current_source']);self.assertIsNone(self.report()['total_cost'])
 def test_expired_and_stale_review_cannot_be_confirmed(self):
  r=self.review()
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=16)):
   with self.assertRaises(AccountingError):self.record(r)
  self.review(expected_revision=1)
  with self.assertRaises(AccountingError):self.record(r)
 def test_record_failure_keeps_payroll_and_no_allocation(self):
  r=self.review();original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type')==engine.RECORDED:raise RuntimeError('Synthetic allocation write failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.record(r)
  self.assertIsNone(self.state()['recorded']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1);self.assertTrue(self.record(r)['allocation_recorded'])
 def test_tampered_review_fails_closed(self):
  r=self.review();row=OutboxEvent.objects.get(pk=r['review_id']);p=copy.deepcopy(row.payload);p['body']['preview']['posted_total_cost']='900.00';OutboxEvent.objects.filter(pk=row.pk).update(payload=p)
  with self.assertRaises(AccountingError):self.record(r)
 def test_missing_sql_guard_blocks_review_without_repair(self):
  from django.db import connection
  name='safety_update_sg_sst_workperiod'
  with connection.cursor() as cursor:
   cursor.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name=%s",[name]);definition=cursor.fetchone()[0];cursor.execute('DROP TRIGGER '+name)
  try:
   with self.assertRaises(APIException):self.review()
   with connection.cursor() as cursor:
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger' AND name=%s",[name]);self.assertEqual(cursor.fetchone()[0],0)
  finally:
   with connection.cursor() as cursor:cursor.execute(definition)
 def test_fake_dispatch_work_cannot_replace_provenance(self):
  WorkPeriod.objects.create(provider_id=self.provider.pk,employee=self.employee,recorded_by=self.actor,revision=3,evidence_digest='f'*64,started_at=self.start+timedelta(hours=5),ended_at=self.start+timedelta(hours=6),operation_reference=self.orders[0].pk,source_kind='DISPATCH')
  with self.assertRaises((AccountingError,APIException)):self.review()
 def test_largest_remainder_is_exact_and_unallocated_loses_ties(self):
  self.assertEqual(engine.split_cents(1,{'a':1,'UNALLOCATED':1}),{'a':1,'UNALLOCATED':0});r=engine.split_cents(101,{'a':1,'b':1,'c':1});self.assertEqual(sum(r.values()),101);self.assertEqual(r,{'a':34,'b':34,'c':33})
 def test_no_allocation_yet_is_not_a_zero_known_operation_cost(self):
  r=self.report();self.assertIsNone(r['total_cost']);self.assertFalse(r['source_complete']);self.assertIn(str(self.payroll.pk),r['unallocated_payrolls'])
 def test_private_api_scopes_sources_review_record_and_state(self):
  def call(action,body):
   r=APIRequestFactory().post('/fixture/?provider_id='+str(self.provider.pk),body,format='json');force_authenticate(r,user=self.actor);return PlanCuentaViewSet.as_view({'post':action})(r)
  source=call('payroll_cost_sources',{'payroll_id':str(self.payroll.pk)});self.assertEqual(source.status_code,200,source.data);self.assertFalse(source.data['clinical_content_returned']);self.assertIn('no-store',source['Cache-Control'])
  body={'payroll_id':str(self.payroll.pk),'capacities':self.capacities,'operation_centers':self.centers,'evidence_digest':'b'*64,'reason_code':'INITIAL','expected_revision':0,'confirmed':True};r=call('review_payroll_costs',body);self.assertEqual(r.status_code,200,r.data);p=call('record_payroll_costs',{'payroll_id':str(self.payroll.pk),'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(p.status_code,200,p.data)
  state=call('payroll_cost_state',{'payroll_id':str(self.payroll.pk)});self.assertEqual(state.status_code,200,state.data);self.assertFalse(state.data['confirmations_restored'])
 def test_revoked_company_link_blocks_history_and_record(self):
  r=self.review();VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.record(r)
  with self.assertRaises(APIException):self.state()
if __name__=='__main__':unittest.main()
