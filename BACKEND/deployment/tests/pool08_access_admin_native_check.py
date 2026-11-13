"""Both owned native ORM implementations; no dependency on the SGA runtime."""
import runpy,unittest,importlib,os,uuid
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from django.http import QueryDict
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_native_check.py')),run_name='access_native_setup')
from pool08_access_cases import AccessScenarios
from api.models import CustomUser,BusinessUserProfile

def cases(system,path):
 identity=importlib.import_module(path+'.identity');models=importlib.import_module(path+'.identity_models');api=importlib.import_module(path+'.crm_api');admin_module=importlib.import_module(path+'.access_admin');service_module=importlib.import_module(path+'.access_service');protocol=importlib.import_module(path+'.access_protocol')
 class Checks(AccessScenarios,unittest.TestCase):
  def setUp(self):
   base_fixture=fixture['fixture']['AdapterTests'].setUp.__globals__['fixture']['fixture']['fixture']['F']
   CustomUser.objects.filter(pk__in=[base_fixture.owner.pk,base_fixture.other.pk]).update(is_active=True)
   base_fixture.owner.is_active=True;base_fixture.other.is_active=True
   self.base=fixture['fixture']['AdapterTests']();self.base.setUp();self.env=patch.dict(os.environ,{'BACKEND_SERVICE':system});self.env.start();self.addCleanup(self.env.stop);self.service_module=service_module;self.protocol=protocol
   from apps.turismo.models import TourismProvider,BusinessProfile
   from apps.turismo.services.company_identity import review_link
   from django.utils import timezone
   from datetime import timedelta
   self.foreign_provider=TourismProvider.objects.create(owner=self.base.other,name='Foreign access fixture',provider_type='GUIDE')
   BusinessProfile.objects.create(provider=self.foreign_provider,legal_name='Foreign synthetic',tax_id=self.base.foreign.tax_id,business_address='fixture',phone='fixture',email='foreign@example.test')
   reviewer=CustomUser(username=uuid.uuid4().hex,is_superuser=True,is_staff=True,is_active=True);CustomUser.objects.bulk_create([reviewer])
   review_link(operator=reviewer,provider_id=self.foreign_provider.pk,tenant_id=self.base.foreign.pk,evidence_digest='b'*64,valid_until=timezone.now()+timedelta(days=1),apply=True)
   self.employee=CustomUser(username=uuid.uuid4().hex,role='BUSINESS_EMPLOYEE',is_active=True);CustomUser.objects.bulk_create([self.employee]);BusinessUserProfile.objects.create(user=self.employee,provider=self.base.provider,position='TEST',is_admin=False);self.staff_ref=str(self.employee.pk)
  def owner(self):return identity.resolve_access(self.base.user,str(self.base.provider.pk))
  def staff(self):return identity.resolve_access(CustomUser.objects.get(pk=self.employee.pk),str(self.base.provider.pk))
  def foreign(self):return identity.resolve_access(self.base.other,str(self.foreign_provider.pk))
  def crm(self,access=None):
   access=access or self.owner();other=access.tenant==str(self.base.foreign.pk)
   request=SimpleNamespace(method='POST',query_params=QueryDict('provider_id='+str(self.foreign_provider.pk if other else self.base.provider.pk)),user=self.base.other if other else self.base.user)
   return api.CRMView().service(request)
  def admin(self,access=None):return admin_module.AccessAdmin(access or self.owner(),self.crm(access))
  def change_staff_role(self):CustomUser.objects.filter(pk=self.employee.pk).update(role='BUSINESS_OPERATOR')
  def disable_staff(self):CustomUser.objects.filter(pk=self.employee.pk).update(is_active=False)
  def disable_owner(self):CustomUser.objects.filter(pk=self.base.user.pk).update(is_active=False)
  def counts(self):return tuple(m.objects.count() for m in (models.CommercialGrant,models.CommercialConsent,models.CommercialIdentityAlias,models.CommercialPolicyEvent))
  def corrupt(self,kind,key):models.CommercialGrant.objects.filter(pk=key).update(digest='0'*64)
  def fail_policy_event(self):
   cls=type(self.owner().store);original=cls.save
   def save(store,kind,row,expected):
    if kind=='event':raise protocol.AccessFault('INJECTED_EVENT_FAILURE',503)
    return original(store,kind,row,expected)
   return patch.object(cls,'save',save)
  def test_http_view_two_verified_companies_and_institutional_roles(self):
   from rest_framework.test import APIRequestFactory,force_authenticate
   view=importlib.import_module(path+'.access_api').AccessAdminView
   for user,provider,status in [(self.base.user,self.base.provider,200),(self.base.other,self.foreign_provider,200),(self.base.user,self.foreign_provider,403),(self.base.other,self.base.provider,403)]:
    request=APIRequestFactory().get('/access/team/',{'provider_id':str(provider.pk)});force_authenticate(request,user=user);response=view.as_view()(request,section='team');self.assertEqual(response.status_code,status,response.data)
    if status==200 and user.pk==self.base.other.pk:self.assertNotIn(self.staff_ref,[m['actor_ref'] for m in response.data['members']])
   for role in ('ADMIN_NACIONAL','ADMIN_DEPARTAMENTAL','ADMIN_MUNICIPAL'):
    CustomUser.objects.filter(pk=self.employee.pk).update(role=role,is_superuser=True,is_staff=True)
    request=APIRequestFactory().get('/access/context/',{'provider_id':str(self.base.provider.pk)});force_authenticate(request,user=CustomUser.objects.get(pk=self.employee.pk));response=view.as_view()(request,section='context');self.assertEqual(response.status_code,403,response.data)
  def race(self,body):
   from concurrent.futures import ThreadPoolExecutor
   from threading import Barrier
   from django.db import connections,connection
   import sqlite3,tempfile
   directory=tempfile.TemporaryDirectory(prefix='access-concurrent-');snapshot=Path(directory.name)/'database.sqlite3'
   with sqlite3.connect(snapshot) as target:connection.connection.backup(target)
   barrier=Barrier(2);owner_id=self.base.user.pk;provider=str(self.base.provider.pk)
   def writer(index):
    try:
     worker=connections['default'];worker.settings_dict={**worker.settings_dict,'NAME':str(snapshot)}
     user=CustomUser.objects.get(pk=owner_id);access=identity.resolve_access(user,provider);request=SimpleNamespace(method='POST',query_params=QueryDict('provider_id='+provider),user=user);admin=admin_module.AccessAdmin(access,api.CRMView().service(request))
     barrier.wait(timeout=10)
     try:admin.command({**body,'request_id':str(uuid.uuid4())});return 200
     except (protocol.AccessFault,api.CRMError) as exc:return exc.status
    finally:connections.close_all()
   try:
    with ThreadPoolExecutor(max_workers=2) as workers:results=list(workers.map(writer,range(2)))
    with sqlite3.connect(snapshot) as source:source.backup(connection.connection)
    return results
   finally:directory.cleanup()
 return Checks
suite=unittest.TestSuite()
for system,path in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cases(system,path)))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
