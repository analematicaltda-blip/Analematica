"""Structured professional/PPE/work/rest records and provisioned dispatch, synthetic data."""
import copy,runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
from django.utils import timezone
from django.test import override_settings
from django.db import connection,IntegrityError
from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework.exceptions import ValidationError,PermissionDenied
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_dispatch_guard_check.py')),run_name='worker_safety_fixture')
from apps.prestadores.mi_negocio.gestion_operativa import dispatch_authorization as engine,state_service
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst import worker_data_service as data
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data import ProfessionalAuthorization,PPEAssignment,WorkPeriod,WorkPeriodEnd,RestPeriod,SafetyRevocation
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data_guards import install,require
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data_views import WorkerSafetyDataViewSet
from apps.prestadores.mi_negocio.gestion_operativa.views import OrdenOperativaViewSet
from apps.core_erp.outbox_models import OutboxEvent
from apps.audit.models import AuditLog
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.models import SaludOcupacional
from rest_framework.test import APIRequestFactory,force_authenticate
create=fixture['fixture']['fixture']['create']
for model in (ProfessionalAuthorization,PPEAssignment,WorkPeriod,WorkPeriodEnd,RestPeriod,SafetyRevocation):create(model)
install(connection)

class WorkerSafetyChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['DispatchGuardChecks']();self.base.setUp();self.owner=self.base.user;self.provider=self.base.provider;self.order=self.base.order;self.worker=self.base.sst.employee;self.now=timezone.now()
  self.base.transition();self.order.refresh_from_db();self.order.fecha_inicio=self.now-timedelta(minutes=5);self.order.fecha_fin_estimada=self.now+timedelta(minutes=55);self.order.save(update_fields=['fecha_inicio','fecha_fin_estimada'])
  self.clinician=get_user_model()(username='clinical-fixture-'+uuid.uuid4().hex,is_active=True);get_user_model().objects.bulk_create([self.clinician]);self.grant(self.clinician,'add')
  self.terms={'enabled':True,'version':'synthetic-reviewed-v1','reviewer_ids':[str(self.clinician.pk)],'required_ppe':['HELMET'],'max_shift_minutes':120,'min_rest_minutes':480,'review_ttl_seconds':180,'valid_from':(self.now-timedelta(days=2)).isoformat(),'valid_until':(self.now+timedelta(days=2)).isoformat(),'evidence_digest':'a'*64}
  self.risk={'approved':True,'version':'synthetic-risk-v1','reviewer_id':str(self.clinician.pk),'valid_from':self.terms['valid_from'],'valid_until':self.terms['valid_until'],'evidence_digest':'c'*64,'hazards':[{'code':'FALL','controlled':True,'evidence_digest':'d'*64}],'required_ppe':['HELMET'],'worker_risk_classes':{str(self.worker.pk):2}}
  self.override=override_settings(OPERATIONAL_RISK_ASSESSMENTS={str(self.provider.pk):{str(self.order.pk):self.risk}},OPERATIONAL_DISPATCH_POLICIES={str(self.provider.pk):self.terms});self.override.enable();self.addCleanup(self.override.disable)
  self.scope={'provider_id':self.provider.pk,'employee_id':str(self.worker.pk),'request_id':str(uuid.uuid4()),'expected_revision':0,'evidence_digest':'b'*64,'confirmed':True}
 def grant(self,user,action):
  ct=ContentType.objects.get_for_model(SaludOcupacional);permission,_=Permission.objects.get_or_create(content_type=ct,codename=action+'_saludocupacional',defaults={'name':'Synthetic explicit grant'});user.user_permissions.add(permission)
 def fitness(self,**extra):
  return data.record_fitness(**{'actor_id':self.clinician.pk,**self.scope,'decision':'FIT','evaluated_at':(self.now-timedelta(days=1)).isoformat(),'valid_from':(self.now-timedelta(days=1)).isoformat(),'valid_until':(self.now+timedelta(days=1)).isoformat(),'document_reference':str(uuid.uuid4()),**extra})
 def ppe(self,**extra):
  return data.record_ppe(**{'actor_id':self.owner.pk,**self.scope,'equipment_code':'HELMET','equipment_reference':str(uuid.uuid4()),'quantity':1,'delivered_at':(self.now-timedelta(days=1)).isoformat(),'valid_until':(self.now+timedelta(days=1)).isoformat(),**extra})
 def rest(self,**extra):return data.record_rest(**{'actor_id':self.owner.pk,**self.scope,'started_at':(self.now-timedelta(hours=12)).isoformat(),'ended_at':self.now.isoformat(),**extra})
 def records(self,fitness=None,ppe=None,rest=None):
  fit=fitness or self.fitness();equipment=ppe or self.ppe();rest=rest or self.rest()
  return {'employee_id':str(self.worker.pk),'fitness_authorization_id':fit['record_id'],'ppe_assignment_ids':[equipment['record_id']],'rest_period_id':rest['record_id']}
 def attest(self,refs=None,**extra):return engine.attest(**{'actor_id':self.clinician.pk,'provider_id':self.provider.pk,'order_id':str(self.order.pk),'crew':[refs or self.records()],'expected_revision':0,'confirmed':True,**extra})
 def review(self):return engine.review_dispatch(actor_id=self.owner.pk,provider_id=self.provider.pk,order_id=str(self.order.pk),confirmed=True)
 def apply(self,review,**extra):return engine.apply_dispatch(**{'actor_id':self.owner.pk,'provider_id':self.provider.pk,'order_id':str(self.order.pk),'review_id':review['review_id'],'confirmed':True,**extra})
 def call_data(self,action,body,user=None):
  req=APIRequestFactory().post('/fixture/?provider_id='+str(self.provider.pk),body,format='json');force_authenticate(req,user=user or self.owner);return WorkerSafetyDataViewSet.as_view({'post':action})(req)
 def test_records_are_real_typed_rows_with_encrypted_decision(self):
  refs=self.records();self.assertEqual(ProfessionalAuthorization.objects.get(pk=refs['fitness_authorization_id']).decision,'FIT')
  with connection.cursor() as cur:
   cur.execute('SELECT decision FROM sg_sst_professionalauthorization WHERE id=%s',[uuid.UUID(refs['fitness_authorization_id']).hex]);cipher=cur.fetchone()[0]
  self.assertNotEqual(cipher,'FIT');self.assertTrue(cipher.startswith('gAAAA'));self.assertEqual(PPEAssignment.objects.get(pk=refs['ppe_assignment_ids'][0]).quantity,1);self.assertTrue(RestPeriod.objects.filter(pk=refs['rest_period_id']).exists())
 def test_positive_dispatch_uses_records_two_confirmations_and_one_receipt(self):
  att=self.attest();review=self.review();result=self.apply(review);self.order.refresh_from_db();self.assertEqual(self.order.estado,'EJECUCION');self.assertTrue(result['dispatch_recorded']);self.assertFalse(result['physical_service_state_verified']);self.assertFalse(result['ledger_written']);self.assertTrue(self.apply(review)['replayed']);self.assertEqual(OutboxEvent.objects.filter(event_type=engine.PREFIX+'started.v1',aggregate_root=str(self.order.pk)).count(),1)
  payload=OutboxEvent.objects.get(pk=att['attestation_id']).payload;self.assertNotIn('fitness_valid_until',str(payload));self.assertNotIn("'fitness':",str(payload))
 def test_missing_data_never_defaults_to_fit_or_rested(self):
  with self.assertRaises(ValidationError):self.attest(refs={'employee_id':str(self.worker.pk),'fitness_authorization_id':str(uuid.uuid4()),'ppe_assignment_ids':[],'rest_period_id':str(uuid.uuid4())})
  with self.assertRaises(ValidationError):self.review()
 def test_unfit_fitness_blocks_review(self):
  self.attest(self.records(fitness=self.fitness(decision='UNFIT')))
  with self.assertRaises(ValidationError):self.review()
 def test_restricted_fitness_not_assumed_unconditionally_fit(self):
  self.attest(self.records(fitness=self.fitness(decision='FIT_RESTRICTED')))
  with self.assertRaises(ValidationError):self.review()
 def test_expired_fitness_blocks_review(self):
  self.attest(self.records(fitness=self.fitness(valid_until=(self.now-timedelta(hours=1)).isoformat())))
  with self.assertRaises(ValidationError):self.review()
 def test_missing_or_expiring_ppe_blocks_review(self):
  self.attest(self.records(ppe=self.ppe(valid_until=(self.now+timedelta(minutes=1)).isoformat())))
  with self.assertRaises(ValidationError):self.review()
 def test_insufficient_rest_blocks_review(self):
  self.attest(self.records(rest=self.rest(started_at=(self.now-timedelta(hours=1)).isoformat())))
  with self.assertRaises(ValidationError):self.review()
 def test_open_work_or_rest_work_overlap_blocks(self):
  refs=self.records();data.record_work(actor_id=self.owner.pk,**self.scope,started_at=(self.now-timedelta(hours=2)).isoformat(),ended_at=None)
  with self.assertRaises(ValidationError):self.attest(refs)
 def test_close_open_work_preserves_original(self):
  work=data.record_work(actor_id=self.owner.pk,**self.scope,started_at=(self.now-timedelta(hours=14)).isoformat(),ended_at=None)
  end=data.close_work(actor_id=self.owner.pk,**self.scope,work_period_id=work['record_id'],ended_at=(self.now-timedelta(hours=13)).isoformat());self.assertIsNone(WorkPeriod.objects.get(pk=work['record_id']).ended_at);self.assertEqual(str(WorkPeriodEnd.objects.get(pk=end['record_id']).work_period_id),work['record_id'])
 def test_owner_or_superuser_without_explicit_grant_cannot_write_fitness(self):
  with self.assertRaises(PermissionDenied):self.fitness(actor_id=self.owner.pk)
  get_user_model().objects.filter(pk=self.owner.pk).update(is_superuser=True);self.terms['reviewer_ids']=[str(self.owner.pk)]
  with self.assertRaises(PermissionDenied):self.fitness(actor_id=self.owner.pk)
 def test_professional_role_revoked_between_confirmations_blocks(self):
  self.attest();review=self.review();self.clinician.user_permissions.clear()
  with self.assertRaises(PermissionDenied):self.apply(review)
 def test_new_fitness_revision_supersedes_old_reference(self):
  refs=self.records();self.fitness(request_id=str(uuid.uuid4()),expected_revision=1,decision='UNFIT')
  with self.assertRaises(ValidationError):self.attest(refs)
 def test_revoked_ppe_cannot_be_used(self):
  refs=self.records();data.revoke_record(actor_id=self.owner.pk,**self.scope,record_type='PPE',record_id=refs['ppe_assignment_ids'][0])
  with self.assertRaises(ValidationError):self.attest(refs)
 def test_operation_or_policy_change_invalidates_review(self):
  self.attest();review=self.review();self.order.costo_proyectado=1;self.order.save(update_fields=['costo_proyectado'])
  with self.assertRaises(ValidationError):self.apply(review)
 def test_missing_policy_or_expired_owner_review_blocks(self):
  self.attest();review=self.review()
  with override_settings(OPERATIONAL_DISPATCH_POLICIES={}):
   with self.assertRaises(ValidationError):self.apply(review)
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=4)):
   with self.assertRaises(ValidationError):self.apply(review)
 def test_second_confirmation_required_and_clinician_cannot_use_owners_review(self):
  self.attest();review=self.review()
  with self.assertRaises(ValidationError):self.apply(review,confirmed=False)
  with self.assertRaises(PermissionDenied):self.apply(review,actor_id=self.clinician.pk)
 def test_audit_failure_rolls_back_order_claims_and_receipt(self):
  self.attest();review=self.review()
  with patch.object(AuditLog.objects,'create',side_effect=RuntimeError('Synthetic audit failure')):
   with self.assertRaises(RuntimeError):self.apply(review)
  self.order.refresh_from_db();self.assertEqual(self.order.estado,'PREPARACION');self.assertIsNone(engine.find_start(self.provider,self.order));self.assertTrue(self.apply(review)['dispatch_recorded'])
 def test_end_two_reviews_releases_claims_and_records_actual_work(self):
  self.attest();review=self.review();dispatch=self.apply(review);actual=timezone.now().isoformat();end=engine.review_end(actor_id=self.owner.pk,provider_id=self.provider.pk,order_id=str(self.order.pk),actual_end=actual,evidence_digest='c'*64,confirmed=True)
  with self.assertRaises(ValidationError):engine.apply_end(actor_id=self.owner.pk,provider_id=self.provider.pk,order_id=str(self.order.pk),review_id=end['review_id'],confirmed=False)
  result=engine.apply_end(actor_id=self.owner.pk,provider_id=self.provider.pk,order_id=str(self.order.pk),review_id=end['review_id'],confirmed=True);self.assertEqual(result['state'],'VALIDACION');self.assertTrue(result['completion_accounting_pending']);self.assertFalse(result['ledger_written']);self.assertEqual(WorkPeriod.objects.filter(provider=self.provider,employee=self.worker,source_kind='DISPATCH').count(),1);self.assertTrue(engine.apply_end(actor_id=self.owner.pk,provider_id=self.provider.pk,order_id=str(self.order.pk),review_id=end['review_id'],confirmed=True)['replayed'])
 def test_same_worker_cannot_be_dispatched_twice_while_busy(self):
  refs=self.records();self.attest(refs);self.apply(self.review())
  from apps.prestadores.mi_negocio.gestion_operativa.models import OrdenOperativa
  other=OrdenOperativa.objects.create(provider=self.order.provider,contrato_ref_id=uuid.uuid4(),descripcion_servicio='Other synthetic job',fecha_inicio=self.order.fecha_inicio,fecha_fin_estimada=self.order.fecha_fin_estimada)
  state_service.transition(usuario_id=self.owner.pk,provider_id=self.provider.pk,kind='OrdenOperativa',operation_id=other.pk,expected_state='PENDIENTE',new_state='PREPARACION',reason='Planning',confirmed=True)
  from django.conf import settings
  settings.OPERATIONAL_RISK_ASSESSMENTS[str(self.provider.pk)][str(other.pk)]=copy.deepcopy(self.risk)
  engine.attest(actor_id=self.clinician.pk,provider_id=self.provider.pk,order_id=str(other.pk),crew=[refs],expected_revision=0,confirmed=True)
  with self.assertRaisesRegex(ValidationError,'ya asignado'):engine.review_dispatch(actor_id=self.owner.pk,provider_id=self.provider.pk,order_id=str(other.pk),confirmed=True)
 def test_old_freeform_fitness_and_rest_boolean_are_refused(self):
  with self.assertRaises(ValidationError):self.attest(refs={'employee_id':str(self.worker.pk),'fitness':'FIT','ppe':[],'last_work_ended_at':self.now.isoformat(),'evidence_digest':'b'*64})
 def test_other_company_record_reference_is_refused(self):
  refs=self.records();refs['employee_id']=str(self.base.sst.worker(self.base.other.pk).pk)
  with self.assertRaises(ValidationError):self.attest(refs)
 def test_no_plaintext_crypto_fallback_and_sql_guards(self):
  fit=self.fitness();table='sg_sst_professionalauthorization'
  with connection.cursor() as cur:
   with self.assertRaises(IntegrityError):cur.execute('UPDATE '+table+' SET decision=%s WHERE id=%s',['FIT',uuid.UUID(fit['record_id']).hex])
   name='safety_update_'+table;cur.execute('SELECT sql FROM sqlite_master WHERE name=%s',[name]);sql=cur.fetchone()[0];cur.execute('DROP TRIGGER '+name)
   try:
    cur.execute('UPDATE '+table+' SET decision=%s WHERE id=%s',['FIT',uuid.UUID(fit['record_id']).hex])
    with self.assertRaises(ModelValidationError):ProfessionalAuthorization.objects.get(pk=fit['record_id'])
    with self.assertRaises(ValidationError):require(connection)
   finally:cur.execute(sql)
 def test_orm_update_delete_and_duplicates_are_refused(self):
  fit=self.fitness();row=ProfessionalAuthorization.objects.get(pk=fit['record_id'])
  with self.assertRaises(ModelValidationError):row.delete()
  with self.assertRaises(ModelValidationError):ProfessionalAuthorization.objects.filter(pk=row.pk).update(valid_until=self.now)
  with self.assertRaises(ModelValidationError):row.save()
 def test_idempotent_request_cannot_change_evidence(self):
  ref=str(uuid.uuid4());first=self.fitness(document_reference=ref);again=self.fitness(document_reference=ref);self.assertTrue(again['replayed']);self.assertEqual(first['record_id'],again['record_id'])
  with self.assertRaises(ValidationError):self.fitness(document_reference=ref,evidence_digest='f'*64)
 def test_summary_has_no_decision_or_clinical_document(self):
  refs=self.records();r=self.call_data('summary',{'employee_id':str(self.worker.pk),'kind':'FITNESS','before_revision':None});self.assertEqual(r.status_code,200,r.data);self.assertFalse(r.data['decision_returned']);self.assertNotIn('decision',str(r.data['items']));self.assertNotIn('document_reference',str(r.data['items']));self.assertIn('no-store',r['Cache-Control'])
 def test_fitness_api_needs_professional_and_strict_fields(self):
  body={**self.scope,'decision':'FIT','evaluated_at':(self.now-timedelta(days=1)).isoformat(),'valid_from':(self.now-timedelta(days=1)).isoformat(),'valid_until':(self.now+timedelta(days=1)).isoformat(),'document_reference':str(uuid.uuid4())};body['provider_id']=str(self.provider.pk);body.pop('provider_id')
  r=self.call_data('fitness',body,user=self.clinician);self.assertEqual(r.status_code,200,r.data);self.assertFalse(r.data['clinical_content_returned']);self.assertEqual(self.call_data('fitness',{**body,'diagnosis':'Not accepted'},user=self.clinician).status_code,400)
 def test_dispatch_api_uses_owner_scope(self):
  self.attest();req=APIRequestFactory().post('/fixture/?provider_id='+str(self.provider.pk),{'confirmed':True},format='json');force_authenticate(req,user=self.owner);r=OrdenOperativaViewSet.as_view({'post':'review_dispatch'})(req,pk=str(self.order.pk));self.assertEqual(r.status_code,200,r.data)
  req=APIRequestFactory().post('/fixture/?provider_id='+str(self.provider.pk),{'review_id':r.data['review_id'],'confirmed':True},format='json');force_authenticate(req,user=self.owner);r=OrdenOperativaViewSet.as_view({'post':'apply_dispatch'})(req,pk=str(self.order.pk));self.assertEqual(r.status_code,200,r.data);self.assertTrue(r.data['dispatch_recorded'])
 def test_clinical_detail_requires_extra_view_permission(self):
  record=self.fitness();body={'record_id':record['record_id']}
  self.assertEqual(self.call_data('fitness_detail',body,user=self.clinician).status_code,403)
  self.grant(self.clinician,'view');r=self.call_data('fitness_detail',body,user=self.clinician);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['decision'],'FIT');self.assertTrue(r.data['clinical_content_returned']);self.assertFalse(r.data['medical_documents_returned'])
  self.assertEqual(self.call_data('fitness_detail',body).status_code,403)
 def test_summary_pagination_never_duplicates_or_exposes_decision(self):
  for revision in range(21):self.rest(request_id=str(uuid.uuid4()),expected_revision=revision)
  r=self.call_data('summary',{'employee_id':str(self.worker.pk),'kind':'REST','before_revision':None});self.assertEqual(r.status_code,200,r.data);self.assertEqual(len(r.data['items']),20);cursor=r.data['next_before_revision'];self.assertIsNotNone(cursor)
  nxt=self.call_data('summary',{'employee_id':str(self.worker.pk),'kind':'REST','before_revision':cursor});self.assertEqual(len(nxt.data['items']),1);self.assertNotIn(nxt.data['items'][0]['record_id'],{x['record_id'] for x in r.data['items']})
 def test_missing_storage_guards_never_auto_repair_or_write(self):
  with connection.cursor() as cur:
   name='safety_update_sg_sst_ppeassignment';cur.execute('SELECT sql FROM sqlite_master WHERE name=%s',[name]);sql=cur.fetchone()[0];cur.execute('DROP TRIGGER '+name)
   try:
    with self.assertRaises(ValidationError):self.ppe()
    self.assertFalse(PPEAssignment.objects.filter(provider=self.provider).exists())
   finally:cur.execute(sql)
 def test_future_work_and_rest_and_noninteger_ppe_are_rejected(self):
  with self.assertRaises(ValidationError):data.record_work(actor_id=self.owner.pk,**self.scope,started_at=self.now.isoformat(),ended_at=(self.now+timedelta(hours=1)).isoformat())
  with self.assertRaises(ValidationError):self.rest(ended_at=(self.now+timedelta(hours=1)).isoformat())
  for quantity in [True,0,-1,1.5,'1']:
   with self.assertRaises(ValidationError):self.ppe(quantity=quantity)
 def test_recorded_work_overlapping_rest_is_not_counted_as_rest(self):
  refs=self.records();data.record_work(actor_id=self.owner.pk,**self.scope,started_at=(self.now-timedelta(hours=2)).isoformat(),ended_at=(self.now-timedelta(hours=1)).isoformat())
  with self.assertRaises(ValidationError):self.attest(refs)
 def test_professional_authorization_can_be_revoked_without_deleting_it(self):
  refs=self.records();data.revoke_record(actor_id=self.owner.pk,**self.scope,record_type='FITNESS',record_id=refs['fitness_authorization_id'])
  with self.assertRaises(ValidationError):self.attest(refs)
  self.assertTrue(ProfessionalAuthorization.objects.filter(pk=refs['fitness_authorization_id']).exists())
 def test_basic_worker_list_is_scoped_and_contains_no_medical_data(self):
  r=self.call_data('employees',{'after_id':None});self.assertEqual(r.status_code,200,r.data);self.assertIn(str(self.worker.pk),{row['id'] for row in r.data['employees']});self.assertFalse(r.data['clinical_content_returned']);self.assertNotIn('decision',str(r.data));self.assertNotIn('document_reference',str(r.data))
 def test_server_policy_loader_is_private_and_never_accepts_duplicate_keys(self):
  import json,tempfile
  from worker_dispatch_policy import load
  from django.core.exceptions import ImproperlyConfigured
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'policy.json';path.write_text(json.dumps({str(self.provider.pk):self.terms}));path.chmod(0o600);self.assertTrue(load(str(path))[str(self.provider.pk)]['enabled'])
   path.chmod(0o644)
   with self.assertRaises(ImproperlyConfigured):load(str(path))
   path.chmod(0o600);path.write_text('{"duplicate":1,"duplicate":2}')
   with self.assertRaises(ImproperlyConfigured):load(str(path))
  self.assertEqual(load(None),{})
 def test_malformed_worker_summary_returns_validation_error(self):
  for identifier in ['not-a-uuid',None,{},'']:
   r=self.call_data('summary',{'employee_id':identifier,'kind':'REST','before_revision':None});self.assertEqual(r.status_code,400,r.data)
if __name__=='__main__':unittest.main()
