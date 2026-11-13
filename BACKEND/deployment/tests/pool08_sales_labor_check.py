"""Actual professional/EPP/rest dispatch and posted-payroll operational cost gates."""
import runpy,unittest,importlib,uuid
from pathlib import Path
from types import SimpleNamespace
from datetime import timedelta
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_worker_safety_check.py')),run_name='sales_labor_fixture')
from apps.prestadores.mi_negocio.gestion_operativa import dispatch_authorization as dispatch
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst import worker_data_service as work
from apps.prestadores.mi_negocio.gestion_contable.nomina import reviewed_payroll as payroll,operational_costs as costs
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Planilla,Contrato,DetalleLiquidacion,NovedadNomina,ConceptoNomina
from apps.core_erp.accounting.models import Account,ChartOfAccounts,JournalEntry
from apps.turismo.models import VerifiedCompanyLink
create=fixture['create']
from apps.prestadores.mi_negocio.gestion_contable.nomina import models as payroll_models
for name in ('Planilla','Contrato','HistorialSalarial','ConceptoNomina','DetalleLiquidacion','NovedadNomina','IncapacidadLaboral','Ausencia','ProvisionNomina','IndicadorLaboral'):create(getattr(payroll_models,name))
class LaborChecks(unittest.TestCase):
 def setUp(self):
  self.c=fixture['WorkerSafetyChecks']();self.c.setUp();self.addCleanup(self.c.doCleanups);self.c.attest();self.c.apply(self.c.review());self.link=VerifiedCompanyLink.objects.get(provider=self.c.provider,revoked_at=None);self.company=self.link.tenant
  self.args=dict(mode='EXISTING_LABOR_ORDER',order_id=str(self.c.order.pk),reason='Orden con autorización registrada',support_digest='c'*64)
 def operations(self,path):return importlib.import_module(path+'.sales_operations').Operations(SimpleNamespace(crm=SimpleNamespace(actor=str(self.c.owner.pk),store=SimpleNamespace(provider=str(self.c.provider.pk)))))
 def test_actual_authorized_dispatch_is_accepted_without_clinical_details(self):
  for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
   result=self.operations(path).labor({},self.args,'UNCONDITIONAL_RECEIVABLE');self.assertEqual(result['order_id'],str(self.c.order.pk));self.assertTrue(result['dispatch_id']);self.assertFalse(result['physical_execution_verified']);self.assertNotIn('fitness',str(result));self.assertNotIn('HELMET',str(result))
 def test_completed_dispatch_and_real_posted_payroll_cost_gate(self):
  actual_end=timezone.now();review=dispatch.review_end(actor_id=self.c.owner.pk,provider_id=self.c.provider.pk,order_id=self.c.order.pk,actual_end=actual_end.isoformat(),evidence_digest='e'*64,confirmed=True);dispatch.apply_end(actor_id=self.c.owner.pk,provider_id=self.c.provider.pk,order_id=self.c.order.pk,review_id=review['review_id'],confirmed=True)
  day=timezone.localdate();contract=Contrato.objects.create(empleado=self.c.worker,fecha_inicio=day,salario='3000.00',cargo='Synthetic',tipo_contrato='TERMINO_INDEFINIDO',activo=True);sheet=Planilla.objects.create(perfil=self.c.provider,periodo_inicio=day,periodo_fin=day)
  chart=ChartOfAccounts.plain_objects.filter(tenant=self.company).first();mapping={}
  for index,(key,kind) in enumerate(payroll.ACCOUNT_TYPES.items()):mapping[key]=str(Account.plain_objects.create(tenant=self.company,chart_of_accounts=chart,code='SALE-LABOR-'+str(index),name=key,type=kind).pk)
  policy=dict(code='SALE-LABOR-SYNTHETIC',revision=1,valid_from=day.isoformat(),valid_until=day.isoformat(),divisor_days=30,evidence_digest='a'*64,components=[dict(code="DECLARED_PROVISION",kind="PROVISION",rate_bps=800)])
  review=payroll.review_payroll(actor=self.c.owner,provider_id=self.c.provider.pk,payroll_id=sheet.pk,policy=policy,workers=[dict(employee_id=str(self.c.worker.pk),contract_id=str(contract.pk),worked_days=1)],account_mapping=mapping,evidence_digest='b'*64,expected_revision=0,confirmed=True);payroll.post_payroll(actor=self.c.owner,provider_id=self.c.provider.pk,payroll_id=sheet.pk,review_id=review['review_id'],confirmed=True)
  args=dict(actor=self.c.owner,provider_id=self.c.provider.pk,payroll_id=sheet.pk);review=costs.review_costs(**args,capacities=[dict(employee_id=str(self.c.worker.pk),capacity_seconds=3600)],operation_centers={str(self.c.order.pk):'LABOR-SALE'},evidence_digest='b'*64,reason_code='INITIAL',expected_revision=0,confirmed=True);costs.record_costs(**args,review_id=review['review_id'],confirmed=True)
  for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
   result=self.operations(path).labor({},dict(self.args,cost_since=day.isoformat(),cost_until=day.isoformat()),'SERVICE_DELIVERED');self.assertTrue(result['labor_cost_posted']);self.assertEqual(len(result['labor_cost_digest']),64)
if __name__=='__main__':unittest.main()
