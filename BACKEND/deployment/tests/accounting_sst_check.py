"""Real scoped SST HTTP/ORM checks; synthetic records, no medical certification."""
import runpy, unittest, uuid
from datetime import date, timedelta
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='sst_fixture')
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst import models, views
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.services import SSTService
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Empleado
from apps.turismo.models import VerifiedCompanyLink
for model in (Permission,Group,models.MatrizRiesgo,models.ControlRiesgo,models.IncidenteLaboral,models.InvestigacionIncidente,models.SaludOcupacional,models.CapacitacionSST,models.PlanAnualSST,models.ActividadPlanSST,models.InspeccionSST,models.HallazgoInspeccion,models.IndicadorSST,models.AlertaSST,Empleado):fixture['create'](model)

from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.sargentos import SargentoSST
from apps.prestadores.mi_negocio.gestion_operativa.models import ProcesoOperativo
from apps.audit.models import AuditLog
from apps.companies.models import Company
for model in (Company, AuditLog, ProcesoOperativo):fixture['create'](model)

class SSTChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['RecognitionTests']();self.case.setUp();self.user=self.case.case.actor;self.provider=self.case.case.provider
  self.user.user_permissions.clear()
  self.other=fixture['RecognitionTests']();self.other.setUp()
  from api.models import CustomUser
  stranger=CustomUser(username='sst-stranger-'+uuid.uuid4().hex,is_active=True,role='BUSINESS_OWNER');CustomUser.objects.bulk_create([stranger]);type(self.provider).objects.filter(pk=self.other.case.provider.pk).update(owner=stranger)
  self.plan=models.PlanAnualSST.objects.create(provider_id=self.provider.pk,año=timezone.localdate().year,nombre='Own plan',objetivo='Synthetic',estado='ACTIVO')
  self.foreign_plan=models.PlanAnualSST.objects.create(provider_id=self.other.case.provider.pk,año=timezone.localdate().year,nombre='Foreign plan',objetivo='Synthetic')
  self.activity=models.ActividadPlanSST.objects.create(plan=self.plan,nombre='Own activity',fecha_programada=timezone.localdate())
  self.foreign_activity=models.ActividadPlanSST.objects.create(plan=self.foreign_plan,nombre='Foreign private activity',fecha_programada=timezone.localdate())
  self.employee=self.worker(self.provider.pk)
  self.clinical=models.SaludOcupacional.objects.create(provider_id=self.provider.pk,empleado_id=self.employee.pk,tipo_examen='Synthetic',fecha_examen=timezone.localdate(),resultado_concepto='NO CERTIFICADO',recomendaciones='PRIVATE CLINICAL TEXT')
 def worker(self,provider,state='ACTIVO'):
  identifier=uuid.uuid4().hex
  return Empleado.objects.create(perfil_id=provider,nombre='Synthetic',apellido='Worker',identificacion=identifier,fecha_nacimiento=date(1990,1,1),direccion='Private',telefono='Private',email=identifier+'@example.test',estado=state)
 def call(self,view,action='list',method='get',data=None,pk=None,user=None,provider=None):
  request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(provider or self.provider.pk),data or {},format='json')
  if user is not False:force_authenticate(request,user=user or self.user)
  return view.as_view({method:action})(request,**({'pk':str(pk)} if pk else {}))
 def grant(self,operation):
  content=ContentType.objects.get_for_model(models.SaludOcupacional)
  permission,_=Permission.objects.get_or_create(content_type=content,codename=operation+'_saludocupacional',defaults={'name':'Synthetic clinical grant'})
  self.user.user_permissions.add(permission)
 def test_activity_list_and_detail_are_scoped(self):
  r=self.call(views.ActividadPlanSSTViewSet);self.assertEqual(r.status_code,200,r.data);rows=r.data.get('results',[]) if isinstance(r.data,dict) else r.data
  self.assertEqual([row['id'] for row in rows],[self.activity.pk]);self.assertEqual(self.call(views.ActividadPlanSSTViewSet,'retrieve',pk=self.foreign_activity.pk).status_code,404)
 def test_cross_company_parent_on_create_and_update_is_rejected(self):
  for action,method,pk in [('create','post',None),('partial_update','patch',self.activity.pk)]:
   r=self.call(views.ActividadPlanSSTViewSet,action,method,{'plan':str(self.foreign_plan.pk),'nombre':'Attempt','fecha_programada':timezone.localdate().isoformat()},pk)
   self.assertEqual(r.status_code,400,r.data)
  self.activity.refresh_from_db();self.assertEqual(self.activity.plan_id,self.plan.pk)
 def test_own_activity_create_update_and_delete_remain_operational(self):
  r=self.call(views.ActividadPlanSSTViewSet,'create','post',{'plan':str(self.plan.pk),'nombre':'New task','fecha_programada':timezone.localdate().isoformat()});self.assertEqual(r.status_code,201,r.data)
  pk=r.data['id'];self.assertEqual(self.call(views.ActividadPlanSSTViewSet,'partial_update','patch',{'completada':True},pk).status_code,200)
  self.assertEqual(self.call(views.ActividadPlanSSTViewSet,'destroy','delete',pk=pk).status_code,204)
 def test_superuser_cannot_bypass_company_or_clinical_permission(self):
  type(self.user).objects.filter(pk=self.user.pk).update(is_superuser=True)
  self.assertEqual(self.call(views.ActividadPlanSSTViewSet,provider=self.other.case.provider.pk).status_code,403)
  r=self.call(views.SaludOcupacionalViewSet);self.assertEqual(r.status_code,403);self.assertNotIn('PRIVATE CLINICAL',str(r.data))
 def test_clinical_explicit_grant_is_action_specific_and_employee_scoped(self):
  self.grant('view');r=self.call(views.SaludOcupacionalViewSet);self.assertEqual(r.status_code,200,r.data);self.assertIn('PRIVATE CLINICAL',str(r.data))
  r=self.call(views.SaludOcupacionalViewSet,'partial_update','patch',{'recomendaciones':'changed'},self.clinical.pk);self.assertEqual(r.status_code,403)
  self.grant('change');foreign=self.worker(self.other.case.provider.pk)
  r=self.call(views.SaludOcupacionalViewSet,'partial_update','patch',{'empleado_id':str(foreign.pk)},self.clinical.pk);self.assertEqual(r.status_code,400,r.data)
 def test_revocation_and_anonymous_errors_are_private(self):
  for r in (self.call(views.ActividadPlanSSTViewSet,user=False),self.call(views.SaludOcupacionalViewSet)):
   self.assertIn(r.status_code,(401,403));self.assertIn('no-store',r['Cache-Control'])
  VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  for view in (views.ActividadPlanSSTViewSet,views.DashboardSSTViewSet):self.assertEqual(self.call(view).status_code,403)
 def incident(self,provider,when):
  return models.IncidenteLaboral.objects.create(provider_id=provider,tipo='ACCIDENTE',fecha_hora=when,lugar='Synthetic',descripcion_hechos='Synthetic',gravedad='LEVE')
 def test_observations_use_current_real_headcount_and_current_month_year(self):
  self.worker(self.provider.pk);self.worker(self.provider.pk,'RETIRADO');self.worker(self.other.case.provider.pk)
  now=timezone.now();self.incident(self.provider.pk,now-timedelta(seconds=1));self.incident(self.provider.pk,now.replace(year=now.year-1));self.incident(self.other.case.provider.pk,now)
  period=timezone.localdate().strftime('%Y-%m');before=models.IndicadorSST.objects.count();r=SSTService.calcular_indicadores(self.provider.pk,period)
  self.assertEqual(r['trabajadores_activos_observados'],2);self.assertEqual(r['accidentes_periodo'],1);self.assertEqual(r['accidentes_por_100_trabajadores_actuales'],'50.00');self.assertFalse(r['habilita_despacho']);self.assertEqual(models.IndicadorSST.objects.count(),before)
 def test_absent_denominator_is_unknown_and_past_period_not_fabricated(self):
  Empleado.objects.filter(perfil_id=self.provider.pk).update(estado='RETIRADO');r=SSTService.calcular_indicadores(self.provider.pk,timezone.localdate().strftime('%Y-%m'));self.assertIsNone(r['accidentes_por_100_trabajadores_actuales'])
  with self.assertRaises(ValueError):SSTService.calcular_indicadores(self.provider.pk,'2000-01')
 def test_dashboard_avoids_unverified_legacy_metrics(self):
  models.IndicadorSST.objects.create(provider_id=self.provider.pk,nombre='Old fabricated ratio',tipo='Accidentalidad',valor='10',meta='2',periodo='old')
  r=self.call(views.DashboardSSTViewSet);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['indicadores'],[]);self.assertEqual(r.data['indicadores_historicos_no_verificados'],1);self.assertFalse(r.data['metricas_observadas']['certificacion_regulatoria']);self.assertIn('no-store',r['Cache-Control'])
 def test_finding_cannot_target_another_company_inspection(self):
  inspection=models.InspeccionSST.objects.create(provider_id=self.other.case.provider.pk,tipo='Synthetic',fecha=timezone.localdate(),inspector_id=uuid.uuid4(),centro_trabajo='Private')
  with self.assertRaises(models.InspeccionSST.DoesNotExist):SSTService.registrar_hallazgo(inspection.pk,'Attempt','ALTA','None',timezone.localdate(),provider_id=self.provider.pk)
 def test_internal_incident_rejects_cross_company_and_does_not_fake_archive(self):
  from rest_framework.exceptions import APIException
  data={'perfil_id':str(self.provider.pk),'tipo':'ACCIDENTE','fecha_hora':timezone.now().isoformat(),'lugar':'Synthetic','descripcion':'PRIVATE HEALTH DESCRIPTION','gravedad':'LEVE'}
  result=SargentoSST.registrar_incidente(data,self.user.pk,provider_id=self.provider.pk)
  self.assertFalse(result['archive_created']);self.assertFalse(result['operational_containment_applied'])
  event=AuditLog.objects.filter(action='SST_INCIDENT_REGISTERED').latest('timestamp');self.assertNotIn('PRIVATE HEALTH',str(event.details))
  with self.assertRaises(APIException):SargentoSST.registrar_incidente(data,self.user.pk,provider_id=self.other.case.provider.pk)
 def test_internal_hold_is_scoped_atomic_and_preserves_description(self):
  from rest_framework.exceptions import APIException
  from unittest.mock import patch
  process=ProcesoOperativo.objects.create(provider_id=self.provider.pk,nombre='Synthetic',descripcion='Original')
  with patch.object(AuditLog.objects,'create',side_effect=RuntimeError('Audit failed')):
   with self.assertRaises(RuntimeError):SargentoSST.bloquear_operacion_por_riesgo(str(process.pk),'PRIVATE SAFETY REASON',self.user.pk,provider_id=self.provider.pk)
  process.refresh_from_db();self.assertEqual(process.estado,'PLANIFICADO')
  result=SargentoSST.bloquear_operacion_por_riesgo(str(process.pk),'PRIVATE SAFETY REASON',self.user.pk,provider_id=self.provider.pk)
  self.assertFalse(result['replayed']);self.assertTrue(SargentoSST.bloquear_operacion_por_riesgo(str(process.pk),'PRIVATE SAFETY REASON',self.user.pk,provider_id=self.provider.pk)['replayed'])
  process.refresh_from_db();self.assertEqual(process.estado,'SUSPENDIDO');self.assertEqual(process.descripcion,'Original')
  with self.assertRaises(APIException):SargentoSST.bloquear_operacion_por_riesgo(str(process.pk),'Attempt',self.user.pk,provider_id=self.other.case.provider.pk)
 def test_risk_range_and_provider_payload_are_validated(self):
  payload={'provider':str(self.provider.pk),'peligro_descripcion':'Synthetic','clasificacion':'FISICO','efectos_posibles':'Synthetic','probabilidad':5,'consecuencia':2,'aceptabilidad':'No Aceptable'}
  r=self.call(views.MatrizRiesgoViewSet,'create','post',payload);self.assertEqual(r.status_code,400,r.data)
  payload['probabilidad']=2;payload['provider']=str(self.other.case.provider.pk)
  r=self.call(views.MatrizRiesgoViewSet,'create','post',payload);self.assertEqual(r.status_code,400,r.data)
  payload['provider']=str(self.provider.pk);r=self.call(views.MatrizRiesgoViewSet,'create','post',payload);self.assertEqual(r.status_code,201,r.data);self.assertEqual(r.data['nivel_riesgo'],4)
 def test_clinical_permission_revocation_is_effective_without_user_cache(self):
  self.grant('view');self.assertEqual(self.call(views.SaludOcupacionalViewSet).status_code,200)
  self.user.user_permissions.clear();self.assertEqual(self.call(views.SaludOcupacionalViewSet).status_code,403)
if __name__=='__main__':unittest.main()
