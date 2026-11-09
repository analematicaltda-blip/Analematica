"""Payroll draft scope and fail-closed incomplete fiscal/ledger pipeline."""
import runpy, unittest, uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_sst_check.py')),run_name='payroll_boundary_fixture')
from django.utils import timezone
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Planilla
from apps.prestadores.mi_negocio.gestion_contable.nomina.views import PlanillaViewSet
from apps.prestadores.mi_negocio.gestion_contable.nomina.services import NominaService,PayrollReadinessUnavailable
from apps.core_erp.accounting.models import JournalEntry
from apps.turismo.models import VerifiedCompanyLink
from apps.prestadores.mi_negocio.gestion_contable.nomina import models as payroll_models
for name in ('Planilla','Contrato','HistorialSalarial','ConceptoNomina','DetalleLiquidacion','NovedadNomina','IncapacidadLaboral','Ausencia','ProvisionNomina','IndicadorLaboral'):
 fixture['fixture']['create'](getattr(payroll_models,name))

class PayrollBoundaryChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['SSTChecks']();self.case.setUp();self.user=self.case.user;self.provider=self.case.provider
  day=timezone.localdate();self.planilla=Planilla.objects.create(perfil_id=self.provider.pk,periodo_inicio=day,periodo_fin=day)
  self.foreign=Planilla.objects.create(perfil_id=self.case.other.case.provider.pk,periodo_inicio=day,periodo_fin=day)
 def call(self,action='list',method='get',data=None,pk=None,user=None):
  request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.provider.pk),data or {},format='json')
  if user is not False:force_authenticate(request,user=user or self.user)
  return PlanillaViewSet.as_view({method:action})(request,**({'pk':str(pk)} if pk else {}))
 def test_list_detail_and_actions_cannot_cross_company(self):
  r=self.call();self.assertEqual(r.status_code,200,r.data);rows=r.data.get('results',[]) if isinstance(r.data,dict) else r.data;self.assertEqual([x['id'] for x in rows],[str(self.planilla.pk)])
  for action,method in [('retrieve','get'),('liquidar','post'),('contabilizar','post')]:self.assertEqual(self.call(action,method,pk=self.foreign.pk).status_code,404)
 def test_owner_actions_do_not_fabricate_accounting_or_mutate_payroll(self):
  count=JournalEntry.plain_objects.count()
  for action in ('liquidar','contabilizar'):
   r=self.call(action,'post',pk=self.planilla.pk);self.assertEqual(r.status_code,503,r.data);self.assertIn('no-store',r['Cache-Control'])
  self.planilla.refresh_from_db();self.assertEqual(self.planilla.estado,'BORRADOR');self.assertIsNone(self.planilla.asiento_contable_ref_id);self.assertEqual(JournalEntry.plain_objects.count(),count)
 def test_internal_service_cannot_use_old_rules_or_mark_draft_as_posted(self):
  for method in (NominaService.liquidar_periodo,NominaService.contabilizar_nomina):
   with self.assertRaises(PayrollReadinessUnavailable):method(self.planilla.pk,self.user.pk)
  self.planilla.refresh_from_db();self.assertEqual(self.planilla.estado,'BORRADOR')
 def test_draft_creation_and_correction_are_preserved(self):
  day=timezone.localdate().isoformat();r=self.call('create','post',{'periodo_inicio':day,'periodo_fin':day});self.assertEqual(r.status_code,201,r.data)
  r=self.call('partial_update','patch',{'periodo_inicio':day},pk=r.data['id']);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['estado'],'BORRADOR')
 def test_status_and_financial_reference_cannot_be_spoofed(self):
  for payload in ({'estado':'PAGADA'},{'asiento_contable_ref_id':str(uuid.uuid4())},{'orden_pago_ref_id':str(uuid.uuid4())},{'perfil':str(self.case.other.case.provider.pk)}):
   r=self.call('partial_update','patch',payload,pk=self.planilla.pk);self.assertEqual(r.status_code,400,r.data)
 def test_posted_historical_rows_cannot_be_edited_or_deleted(self):
  Planilla.objects.filter(pk=self.planilla.pk).update(estado='CONTABILIZADA',asiento_contable_ref_id=uuid.uuid4())
  self.assertEqual(self.call('partial_update','patch',{'periodo_fin':timezone.localdate().isoformat()},pk=self.planilla.pk).status_code,400)
  self.assertEqual(self.call('destroy','delete',pk=self.planilla.pk).status_code,400);self.assertTrue(Planilla.objects.filter(pk=self.planilla.pk).exists())
 def test_reversed_dates_rejected(self):
  r=self.call('create','post',{'periodo_inicio':'2026-12-31','periodo_fin':'2026-01-01'});self.assertEqual(r.status_code,400,r.data)
 def test_revocation_and_anonymous_are_denied_privately(self):
  r=self.call(user=False);self.assertIn(r.status_code,(401,403));self.assertIn('no-store',r['Cache-Control'])
  VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  r=self.call();self.assertEqual(r.status_code,403);self.assertIn('no-store',r['Cache-Control'])
if __name__=='__main__':unittest.main()
