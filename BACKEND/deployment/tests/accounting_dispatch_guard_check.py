"""Actual generic operational API, ORM and internal transition boundaries.
Qualified dispatch remains unavailable; drafts and risk containment remain usable.
"""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
from django.utils import timezone
from rest_framework.exceptions import ValidationError,PermissionDenied
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_sst_check.py')),run_name='dispatch_guard_fixture')
from apps.prestadores.mi_negocio.gestion_operativa import models,views,state_service
from apps.prestadores.mi_negocio.gestion_operativa.sargentos import SargentoOperativo
from apps.audit.models import AuditLog
from apps.turismo.models import VerifiedCompanyLink
from rest_framework.test import APIRequestFactory,force_authenticate
for m in (models.OrdenOperativa,models.RegistroOperativo,models.EvidenciaOperativa,models.IncidenteOperativo,models.TareaOperativa):fixture['fixture']['create'](m)

class DispatchGuardChecks(unittest.TestCase):
 def setUp(self):
  self.sst=fixture['SSTChecks']();self.sst.setUp();self.user=self.sst.user;self.provider=self.sst.provider;self.other=self.sst.other.case.provider
  self.day=timezone.now();self.data={'contrato_ref_id':uuid.uuid4(),'descripcion_servicio':'Synthetic draft','fecha_inicio':self.day,'fecha_fin_estimada':self.day+timedelta(hours=1)}
  self.order=models.OrdenOperativa.objects.create(provider_id=self.provider.pk,**self.data)
  self.process=models.ProcesoOperativo.objects.create(provider_id=self.provider.pk,nombre='Synthetic process')
 def call(self,action,body=None,method='post',obj=None,provider=None,view=None,user=None):
  req=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(provider or self.provider.pk),body or {},format='json');force_authenticate(req,user=user or self.user)
  return (view or views.OrdenOperativaViewSet).as_view({method:action})(req,**({'pk':str((obj or self.order).pk)} if action not in ['list','create'] else {}))
 def transition(self,new='PREPARACION',expected='PENDIENTE',**extra):
  return state_service.transition(**{'usuario_id':self.user.pk,'provider_id':self.provider.pk,'kind':'OrdenOperativa','operation_id':self.order.pk,'expected_state':expected,'new_state':new,'reason':'Synthetic owner review','confirmed':True,**extra})
 def test_safe_planning_transition_is_authenticated_and_audited(self):
  r=self.transition();self.order.refresh_from_db();self.assertEqual(self.order.estado,'PREPARACION');self.assertTrue(r['state_changed']);self.assertFalse(r['read_only']);self.assertFalse(r['service_started']);audit=AuditLog.objects.get(pk=r['audit_id']);self.assertEqual(audit.user_id,self.user.pk);self.assertNotIn('Synthetic owner review',str(audit.details))
 def test_dispatch_blocked_for_all_direct_state_targets(self):
  self.transition()
  for target in ['EJECUCION','VALIDACION','COMPLETADA']:
   with self.assertRaises(ValidationError):self.transition(new=target,expected='PREPARACION')
  self.order.refresh_from_db();self.assertEqual(self.order.estado,'PREPARACION')
 def test_crud_create_patch_and_put_cannot_bypass_dispatch(self):
  body={k:(str(v) if k=='contrato_ref_id' else v.isoformat() if hasattr(v,'isoformat') else v) for k,v in self.data.items()};body['estado']='EJECUCION'
  self.assertEqual(self.call('create',body).status_code,400)
  for action,method in [('partial_update','patch'),('update','put')]:
   self.assertEqual(self.call(action,{**body,'estado':'EJECUCION'},method=method).status_code,400)
  self.order.refresh_from_db();self.assertEqual(self.order.estado,'PENDIENTE')
 def test_orm_create_save_update_and_bulk_cannot_bypass(self):
  with self.assertRaises(ValidationError):models.OrdenOperativa.objects.create(provider_id=self.provider.pk,estado='EJECUCION',**self.data)
  self.order.estado='EJECUCION'
  with self.assertRaises(ValidationError):self.order.save()
  with self.assertRaises(ValidationError):models.OrdenOperativa.objects.filter(pk=self.order.pk).update(estado='EJECUCION')
  with self.assertRaises(ValidationError):models.OrdenOperativa.objects.bulk_update([self.order],['estado'])
  with self.assertRaises(ValidationError):models.OrdenOperativa.objects.bulk_create([models.OrdenOperativa(provider_id=self.provider.pk,estado='EJECUCION',**self.data)])
 def test_orm_provider_and_times_cannot_be_reassigned(self):
  self.order.provider_id=self.other.pk
  with self.assertRaises(ValidationError):self.order.save()
  self.process.inicio_real=timezone.now()
  with self.assertRaises(ValidationError):self.process.save()
  with self.assertRaises(ValidationError):models.ProcesoOperativo.objects.filter(pk=self.process.pk).update(inicio_real=timezone.now())
 def test_bulk_conflict_rewrite_is_blocked(self):
  candidate=models.OrdenOperativa(pk=self.order.pk,provider_id=self.provider.pk,**self.data)
  with self.assertRaises(ValidationError):models.OrdenOperativa.objects.bulk_create([candidate],update_conflicts=True,update_fields=['estado'],unique_fields=['pk'])
  with self.assertRaises(ValidationError):models.OrdenOperativa.objects.bulk_create([candidate],None,False,True,['estado'],['pk'])
 def test_audit_failure_rolls_back_state(self):
  with patch.object(AuditLog.objects,'create',side_effect=RuntimeError('Synthetic audit fault')):
   with self.assertRaises(RuntimeError):self.transition()
  self.order.refresh_from_db();self.assertEqual(self.order.estado,'PENDIENTE')
  self.order.estado='PREPARACION'
  with self.assertRaises(ValidationError):self.order.save()
 def test_stale_state_false_confirmation_and_unknown_transition_denied(self):
  for changes in [{'expected_state':'PREPARACION'},{'confirmed':False},{'confirmed':1},{'new_state':'UNKNOWN'},{'reason':''}]:
   with self.assertRaises(ValidationError):self.transition(**changes)
 def test_foreign_company_inactive_actor_agent_and_revocation_denied(self):
  with self.assertRaises(PermissionDenied):self.transition(provider_id=self.other.pk)
  from django.contrib.auth import get_user_model
  get_user_model().objects.filter(pk=self.user.pk).update(is_agent=True)
  with self.assertRaises(PermissionDenied):self.transition()
  get_user_model().objects.filter(pk=self.user.pk).update(is_agent=False)
  VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  with self.assertRaises(PermissionDenied):self.transition()
 def test_owner_http_transition_truthful_no_agent_mission(self):
  body={'nuevo_estado':'PREPARACION','estado_esperado':'PENDIENTE','motivo':'Reviewed draft','confirmado':True}
  r=self.call('cambiar_estado',body);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['state'],'PREPARACION');self.assertFalse(r.data['service_started']);self.assertIn('no-store',r['Cache-Control'])
  body.update(nuevo_estado='EJECUCION',estado_esperado='PREPARACION');self.assertEqual(self.call('cambiar_estado',body).status_code,400)
 def test_http_draft_create_remains_possible_and_audit_failure_rolls_back(self):
  body={k:(str(v) if k=='contrato_ref_id' else v.isoformat() if hasattr(v,'isoformat') else v) for k,v in self.data.items()}
  r=self.call('create',body);self.assertEqual(r.status_code,201,r.data);self.assertEqual(r.data['estado'],'PENDIENTE');self.assertEqual(str(r.data['provider']),str(self.provider.pk))
  before=models.OrdenOperativa.objects.filter(provider_id=self.provider.pk).count()
  with patch.object(AuditLog.objects,'create',side_effect=RuntimeError('Synthetic audit fault')):
   with self.assertRaises(RuntimeError):self.call('create',body)
  self.assertEqual(before,models.OrdenOperativa.objects.filter(provider_id=self.provider.pk).count())
 def test_provider_override_and_foreign_detail_blocked(self):
  self.assertEqual(self.call('partial_update',{'provider':str(self.other.pk)},method='patch').status_code,400)
  self.assertEqual(self.call('retrieve',method='get',provider=self.other.pk).status_code,403)
 def test_risk_hold_preserved_and_terminal_state_does_not_reopen(self):
  r=state_service.transition(usuario_id=self.user.pk,provider_id=self.provider.pk,kind='ProcesoOperativo',operation_id=self.process.pk,expected_state='PLANIFICADO',new_state='SUSPENDIDO',reason='Risk hold',confirmed=True)
  self.assertTrue(r['state_changed']);self.assertTrue(state_service.transition(usuario_id=self.user.pk,provider_id=self.provider.pk,kind='ProcesoOperativo',operation_id=self.process.pk,expected_state='SUSPENDIDO',new_state='SUSPENDIDO',reason='Risk hold',confirmed=True)['replayed'])
  with self.assertRaises(ValidationError):state_service.transition(usuario_id=self.user.pk,provider_id=self.provider.pk,kind='ProcesoOperativo',operation_id=self.process.pk,expected_state='SUSPENDIDO',new_state='EN_EJECUCION',reason='Bypass attempt',confirmed=True)
 def test_diagnosis_contains_no_clinical_content_or_false_qualification(self):
  r=self.call('pre_dispatch',method='get');self.assertEqual(r.status_code,200,r.data);self.assertFalse(r.data['ready_to_dispatch']);self.assertEqual(len(r.data['blocking_codes']),3);self.assertNotIn('PRIVATE CLINICAL',str(r.data));self.assertFalse(r.data['clinical_content_returned'])
 def test_internal_executor_requires_actor_company_confirmation_and_state(self):
  with self.assertRaises(PermissionDenied):SargentoOperativo.actualizar_estado('OrdenOperativa',self.order.pk,'EJECUCION')
  with self.assertRaises(ValidationError):SargentoOperativo.actualizar_estado('OrdenOperativa',self.order.pk,'EJECUCION','Attempt',self.user.pk,provider_id=self.provider.pk,expected_state='PENDIENTE',confirmed=True)
  r=SargentoOperativo.actualizar_estado('OrdenOperativa',self.order.pk,'PREPARACION','Reviewed',self.user.pk,provider_id=self.provider.pk,expected_state='PENDIENTE',confirmed=True);self.assertFalse(r['service_started'])
 def test_no_fabricated_task_success_or_random_contract(self):
  with self.assertRaises(ValidationError):SargentoOperativo.registrar_ejecucion_tarea(str(uuid.uuid4()),str(uuid.uuid4()),{})
  with self.assertRaises(ValidationError):SargentoOperativo.crear_orden_servicio(self.provider.pk,'Draft',usuario_id=self.user.pk)
 def test_children_and_nested_legacy_inconsistency_cannot_cross_company(self):
  foreign_process=models.ProcesoOperativo.objects.create(provider_id=self.other.pk,nombre='Foreign')
  bad=models.TareaOperativa.objects.create(provider_id=self.provider.pk,proceso=foreign_process,nombre='Bad legacy link',fecha_limite=timezone.now())
  r=self.call('retrieve',method='get',obj=bad,view=views.TareaOperativaViewSet);self.assertEqual(r.status_code,404)
  models.TareaOperativa.objects.create(provider_id=self.other.pk,proceso=self.process,nombre='Foreign private task',fecha_limite=timezone.now())
  r=self.call('retrieve',method='get',obj=self.process,view=views.ProcesoOperativoViewSet);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['tareas'],[])
  body={'proceso':str(foreign_process.pk),'nombre':'Attempt','fecha_limite':timezone.now().isoformat()}
  self.assertEqual(self.call('create',body,view=views.TareaOperativaViewSet).status_code,400)
 def test_reused_primary_key_cannot_overwrite_existing_draft(self):
  with self.assertRaises(ValidationError):models.OrdenOperativa.objects.create(pk=self.order.pk,provider_id=self.provider.pk,**{**self.data,'descripcion_servicio':'Overwrite attempt'})
  self.order.refresh_from_db();self.assertEqual(self.order.descripcion_servicio,'Synthetic draft')
 def test_process_crud_cannot_invent_start_or_finish(self):
  self.assertEqual(self.call('create',{'nombre':'Attempt','estado':'EN_EJECUCION'},view=views.ProcesoOperativoViewSet).status_code,400)
  self.assertEqual(self.call('partial_update',{'inicio_real':timezone.now().isoformat()},method='patch',obj=self.process,view=views.ProcesoOperativoViewSet).status_code,400)
  with self.assertRaises(ValidationError):models.ProcesoOperativo.objects.create(provider_id=self.provider.pk,nombre='Attempt',estado='COMPLETADO')
 def test_internal_draft_creation_uses_owner_and_explicit_contract_window(self):
  contract=uuid.uuid4();r=SargentoOperativo.crear_orden_servicio(self.provider.pk,'Reviewed draft',{'contrato_id':str(contract),'fecha_inicio':self.day.isoformat(),'fecha_fin_estimada':(self.day+timedelta(hours=1)).isoformat()},usuario_id=self.user.pk)
  row=models.OrdenOperativa.objects.get(pk=r['id']);self.assertEqual(row.contrato_ref_id,contract);self.assertEqual(row.provider_id,self.provider.pk);self.assertFalse(r['service_started']);self.assertFalse(r['contract_independently_verified'])
 def test_transition_history_scoped_and_without_reason_or_clinical_content(self):
  self.transition();r=self.call('transition_history',method='get');self.assertEqual(r.status_code,200,r.data);self.assertEqual(len(r.data['history']),1);self.assertEqual(r.data['history'][0]['actor_id'],str(self.user.pk));self.assertEqual(r.data['history'][0]['new_state'],'PREPARACION');self.assertNotIn('Synthetic owner review',str(r.data));self.assertNotIn('PRIVATE CLINICAL',str(r.data));self.assertIn('no-store',r['Cache-Control'])
  self.assertEqual(self.call('transition_history',method='get',provider=self.other.pk).status_code,403)
 def test_hard_delete_does_not_erase_order_history(self):
  self.assertEqual(self.call('destroy',method='delete').status_code,400);self.assertTrue(models.OrdenOperativa.objects.filter(pk=self.order.pk).exists())
if __name__=='__main__':unittest.main()
