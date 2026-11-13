"""Actual native CRM ORM/API, both owned implementations. Disposable SQLite only."""
import runpy,os,unittest,uuid,importlib
from pathlib import Path
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='crm_native_fixture')
from django.db import connection
from django.utils import timezone
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from api.models import BusinessUserProfile,CustomUser
from apps.turismo.models import VerifiedCompanyLink
from unittest.mock import patch
for path in ['apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08']:
 mod=importlib.import_module(path+'.crm_models')
 identity_models=importlib.import_module(path+'.identity_models')
 with connection.schema_editor() as editor:
  for model in (Cliente,BusinessUserProfile,mod.CRMContact,mod.CRMEvent,identity_models.CommercialGrant,identity_models.CommercialConsent,identity_models.CommercialIdentityAlias,identity_models.CommercialPolicyEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)


def cases(system,path):
 api=importlib.import_module(path+'.crm_api');models=importlib.import_module(path+'.crm_models')
 class Checks(unittest.TestCase):
  def setUp(self):
   self.base=fixture['AdapterTests']();self.base.setUp();self.env=patch.dict(os.environ,{'BACKEND_SERVICE':system});self.env.start();self.addCleanup(self.env.stop)
  def call(self,method='get',body=None,section='contacts',contact=None,user=None,provider=None,**query):
   from urllib.parse import urlencode
   url='/fixture/?'+urlencode({'provider_id':str(provider or self.base.provider.pk),**query})
   request=getattr(APIRequestFactory(),method)(url,body,format='json');force_authenticate(request,user=user or self.base.user)
   return api.CRMView.as_view()(request,section='commands' if method=='post' else section,**({'contact_id':contact} if contact else {}))
  def command(self,operation='create',contact=None,revision=0,**data):
   return dict(request_id=str(uuid.uuid4()),operation=operation,contact_id=contact,expected_revision=revision,data=data)
  def create(self,**extra):
   data=dict(name='Contacto nativo',email=uuid.uuid4().hex+'@example.test',phone='+573001234567',origin='MANUAL',responsible_ref=str(self.base.user.pk));data.update(extra)
   response=self.call('post',self.command(**data));self.assertEqual(response.status_code,200,response.data);return response.data['contact_id']
  def test_invalid_email_does_not_persist_contact_or_history(self):
   before=models.CRMContact.objects.count();events=models.CRMEvent.objects.count();r=self.call('post',self.command(name='Invalid contact',email='bad'+chr(0)+'@example.test',phone='',origin='MANUAL',responsible_ref=str(self.base.user.pk)))
   self.assertEqual(r.status_code,422,r.data);self.assertEqual(models.CRMContact.objects.count(),before);self.assertEqual(models.CRMEvent.objects.count(),events)
  def test_numeric_consent_hash_rejected_without_changing_revision(self):
   cid=self.create();r=self.call('post',self.command('consent',cid,1,channel='EMAIL',purpose='MARKETING',granted=False,evidence_digest=int('1'*64),expires_at=(timezone.now()+timedelta(days=1)).isoformat()))
   self.assertEqual(r.status_code,422,r.data);self.assertEqual(self.call(contact=cid).data['revision'],1);self.assertEqual(len(self.call(section='history',contact=cid).data['events']),1)
  def test_escaped_invalid_unicode_is_422_not_server_failure(self):
   import json
   raw=json.dumps(self.command(name='bad'+chr(0xD800),origin='MANUAL',responsible_ref=str(self.base.user.pk)),ensure_ascii=True).encode()
   request=APIRequestFactory().generic('POST','/fixture/?provider_id='+str(self.base.provider.pk),raw,content_type='application/json');force_authenticate(request,user=self.base.user)
   before=models.CRMContact.objects.count();response=api.CRMView.as_view()(request,section='commands');self.assertEqual(response.status_code,422,response.data);self.assertEqual(models.CRMContact.objects.count(),before)
  def test_full_flow_reuses_customer_and_keeps_history(self):
   cid=self.create();self.assertEqual(self.call(contact=cid).data['revision'],1)
   conversion=self.command('convert',cid,1);r=self.call('post',conversion);self.assertEqual(r.status_code,200,r.data)
   customer=r.data['customer_ref'];self.assertTrue(Cliente.objects.filter(pk=customer,perfil_id=self.base.provider.pk).exists())
   r=self.call('post',conversion);self.assertTrue(r.data['replayed']);self.assertEqual(Cliente.objects.filter(perfil_id=self.base.provider.pk).count(),1)
   r=self.call('post',self.command('task',cid,2,title='Llamar',due_at='2026-12-10T12:00:00+00:00',responsible_ref=str(self.base.user.pk)));self.assertEqual(r.status_code,200,r.data)
   events=self.call(section='history',contact=cid).data['events'];self.assertEqual(len(events),3)
   self.assertEqual(len(self.call().data['contacts']),1)
  def test_existing_customer_is_not_duplicated(self):
   row=Cliente.objects.create(perfil_id=self.base.provider.pk,nombre='Histórico',email=uuid.uuid4().hex+'@example.test')
   cid='customer:'+str(row.pk)
   r=self.call('post',self.command('update',cid,0,name='Nombre revisado'));self.assertEqual(r.status_code,200,r.data)
   row.refresh_from_db();self.assertEqual(row.nombre,'Nombre revisado');self.assertEqual(len(self.call().data['contacts']),1)
  def test_foreign_member_company_and_institutional_role_denied(self):
   cid=self.create()
   self.assertEqual(self.call(contact=cid,user=self.base.other).status_code,403)
   self.assertEqual(self.call('post',self.command(responsible_ref=str(self.base.other.pk),name='X',origin='MANUAL')).status_code,403)
   for role in ('ADMIN_NACIONAL','ADMIN_DEPARTAMENTAL','ADMIN_MUNICIPAL','ADMIN_ENTIDAD','DIRECTIVO_NACIONAL','DIRECTIVO_DEPARTAMENTAL','DIRECTIVO_MUNICIPAL','FUNCIONARIO_DIRECTIVO','FUNCIONARIO_PROFESIONAL','FUNCIONARIO_TECNICO','FUNCIONARIO_ASISTENCIAL'):
    CustomUser.objects.filter(pk=self.base.other.pk).update(role=role,is_staff=True,is_superuser=True)
    self.assertEqual(self.call(user=self.base.other).status_code,403)
  def test_explicit_staff_grant_live_revoke_and_institutional_separation(self):
   identity=importlib.import_module(path+'.identity')
   staff=CustomUser(username=uuid.uuid4().hex,role='BUSINESS_EMPLOYEE',is_active=True)
   CustomUser.objects.bulk_create([staff]);BusinessUserProfile.objects.create(user=staff,provider=self.base.provider,position='Equipo CRM',is_admin=True)
   self.assertEqual(self.call(user=staff).status_code,403)
   owner=identity.resolve_access(self.base.user,str(self.base.provider.pk));subject=owner.subject(str(staff.pk))
   grant=owner.grant(str(staff.pk),dict(request_id=str(uuid.uuid4()),capabilities=['crm.prospect.manage'],role_fingerprint=subject['role_fingerprint'],expected_revision=0,expires_at=(timezone.now()+timedelta(days=1)).isoformat(),evidence_digest='a'*64))
   self.assertEqual(self.call(user=staff).status_code,200)
   created=self.call('post',self.command(name='Contacto delegado',origin='STAFF',responsible_ref=str(staff.pk)),user=staff)
   self.assertEqual(created.status_code,200,created.data)
   CustomUser.objects.filter(pk=staff.pk).update(role='ADMIN_NACIONAL')
   self.assertEqual(self.call(user=staff).status_code,403)
   CustomUser.objects.filter(pk=staff.pk).update(role='BUSINESS_EMPLOYEE')
   owner=identity.resolve_access(self.base.user,str(self.base.provider.pk))
   owner.revoke_grant(str(staff.pk),dict(request_id=str(uuid.uuid4()),expected_revision=1))
   self.assertEqual(self.call(user=staff).status_code,403)
  def test_revoked_company_link_rejects_replay_and_reads(self):
   cid=self.create();VerifiedCompanyLink.objects.filter(pk=self.base.link.pk).update(revoked_at=timezone.now())
   self.assertEqual(self.call(contact=cid).status_code,403)
  def test_consent_withdrawal_and_optimistic_conflict(self):
   cid=self.create();data=dict(channel='EMAIL',purpose='MARKETING',granted=True,evidence_digest='a'*64,expires_at=(timezone.now()+timedelta(days=1)).isoformat())
   self.assertEqual(self.call('post',self.command('consent',cid,1,**data)).status_code,200)
   self.assertEqual(self.call('post',self.command('update',cid,1,name='stale')).status_code,409)
   self.assertEqual(self.call('post',self.command('withdraw',cid,2,reason='Solicitud')).status_code,200)
   item=self.call(contact=cid).data;self.assertFalse(item['consents']['EMAIL:MARKETING']['granted'])
   self.assertEqual(self.call('post',self.command('consent',cid,3,**data)).status_code,409)
  def test_duplicate_requires_review_and_no_pii_in_error(self):
   cid=self.create(email='dup@example.test')
   r=self.call('post',self.command(name='Otro',email='DUP@example.test',origin='MANUAL',responsible_ref=str(self.base.user.pk)))
   self.assertEqual(r.status_code,409,r.data);self.assertEqual(r.data['candidate_ids'],[cid]);self.assertNotIn('dup@example.test',str(r.data))
  def test_dedup_review_keeps_separate_contacts_and_no_consent(self):
   cid=self.create()
   other=self.create(duplicate_review={'candidate_ids':[cid],'reason':'Dos titulares con teléfono compartido'})
   self.assertNotEqual(cid,other);self.assertEqual(self.call(contact=other).data['consents'],{})
  def test_legacy_mutation_cannot_erase_managed_contact_history(self):
   from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.views import ClienteViewSet,ClientHistoryConflict
   cid=self.create();result=self.call('post',self.command('convert',cid,1))
   customer=Cliente.objects.get(pk=result.data['customer_ref'])
   with self.assertRaises(ClientHistoryConflict):ClienteViewSet().require_unmanaged_customer(customer)
  def test_phone_change_revokes_consent(self):
   cid=self.create();data=dict(channel='WHATSAPP',purpose='MARKETING',granted=True,evidence_digest='a'*64,expires_at=(timezone.now()+timedelta(days=1)).isoformat())
   self.call('post',self.command('consent',cid,1,**data))
   result=self.call('post',self.command('update',cid,2,phone='+573009876543'));self.assertEqual(result.status_code,200,result.data)
   self.assertFalse(self.call(contact=cid).data['consents']['WHATSAPP:MARKETING']['granted'])
  def test_rollback_if_audit_fails(self):
   before=models.CRMContact.objects.count()
   with patch.object(models.CRMEvent.objects,'create',side_effect=RuntimeError('audit unavailable')):
    with self.assertRaises(RuntimeError):self.call('post',self.command(name='Rollback',origin='MANUAL',responsible_ref=str(self.base.user.pk)))
   self.assertEqual(models.CRMContact.objects.count(),before)
  def test_tourism_service_cannot_expose_enterprise_crm(self):
   with patch.dict(os.environ,{'BACKEND_SERVICE':'turismo'}):self.assertEqual(self.call().status_code,404)
  def test_cache_headers_and_tenant_spoof(self):
   for response in [self.call(),self.call(tenant_id='foreign')]:self.assertEqual(response['Cache-Control'],'no-store')
   self.assertEqual(self.call(tenant_id='foreign').status_code,400)
 return Checks
suite=unittest.TestSuite()
for system,path in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cases(system,path)))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
