"""Owned SGA authority, SQLite ORM, rollback and live role transitions."""
import runpy,unittest,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'BACKEND/deployment/tests'))
fixture=runpy.run_path(str(ROOT/'BACKEND/tests/workspace/test_workspace.py'),run_name='access_sga_fixture')
from pool08_access_cases import AccessScenarios
from app.commercial.pool08 import identity,access_service,access_protocol,identity_models
from app.commercial.pool08.access_admin import AccessAdmin
from app.commercial.pool08.crm_api import service
from app.commercial.pool08.install_crm import install
from app.models.user import Usuario,RolesEnum,Role
from app.models.workspace import WorkspaceGrant
from starlette.datastructures import QueryParams
from types import SimpleNamespace
class AccessChecks(AccessScenarios,unittest.TestCase):
 def setUp(self):
  fixture['WorkspaceTests'].setUp(self);install(self.engine,apply=True);self.staff_ref=str(self.users['full-jefe_area']);self.db.query(WorkspaceGrant).filter_by(user_id=int(self.staff_ref),permission='crm').update({'enabled':True});self.db.commit();self.service_module=access_service;self.protocol=access_protocol
 tearDown=fixture['WorkspaceTests'].tearDown
 login=fixture['WorkspaceTests'].login
 def owner(self):return identity.resolve_access(self.db,self.db.get(Usuario,self.users['full-admin_empresa']))
 def staff(self):return identity.resolve_access(self.db,self.db.get(Usuario,int(self.staff_ref)))
 def foreign(self):return identity.resolve_access(self.db,self.db.get(Usuario,self.users['other-admin_empresa']))
 def crm(self,access=None):return service(SimpleNamespace(method='POST',query_params=QueryParams()),self.db,self.db.get(Usuario,int((access or self.owner()).actor)))
 def admin(self,access=None):
  access=access or self.owner();return AccessAdmin(access,self.crm(access))
 def change_staff_role(self):
  user=self.db.get(Usuario,int(self.staff_ref));user.rol=RolesEnum.profesor;user.roles=[self.db.query(Role).filter_by(nombre='profesor').one()];self.db.commit()
 def disable_staff(self):self.db.query(Usuario).filter_by(id=int(self.staff_ref)).update({'activo':False});self.db.commit()
 def disable_owner(self):self.db.query(Usuario).filter_by(id=self.users['full-admin_empresa']).update({'activo':False});self.db.commit()
 def counts(self):return tuple(self.db.query(m).count() for m in (identity_models.CommercialGrant,identity_models.CommercialConsent,identity_models.CommercialIdentityAlias,identity_models.CommercialPolicyEvent))
 def corrupt(self,kind,key):
  model=self.owner().store.__class__.__module__;self.db.query(identity_models.CommercialGrant).filter_by(id=key).update({'digest':'0'*64});self.db.commit()
 def fail_policy_event(self):
  cls=type(self.owner().store);original=cls.save
  def save(store,kind,row,expected):
   if kind=='event':raise access_protocol.AccessFault('INJECTED_EVENT_FAILURE',503)
   return original(store,kind,row,expected)
  return patch.object(cls,'save',save)
 def test_http_view_two_companies_and_forged_role_claim(self):
  from app.commercial.pool08.api import router
  self.client.app.include_router(router,prefix='/api/v1/commercial-unified')
  route='/api/v1/commercial-unified/crm/access/'
  for role in ('full-admin_empresa','other-admin_empresa'):
   self.login(role);response=self.client.get(route+'team');self.assertEqual(response.status_code,200,response.text)
   if role.startswith('other-'):self.assertNotIn(self.staff_ref,[m['actor_ref'] for m in response.json()['members']])
  self.login('full-jefe_area',roles=['admin_general']);self.assertEqual(self.client.get(route+'context').status_code,403)
 def race(self,body):
  from concurrent.futures import ThreadPoolExecutor
  from threading import Barrier
  barrier=Barrier(2);owner_id=self.users['full-admin_empresa']
  def writer(index):
   with self.factory() as db:
    owner=db.get(Usuario,owner_id);access=identity.resolve_access(db,owner);crm=service(SimpleNamespace(method='POST',query_params=QueryParams()),db,owner);admin=AccessAdmin(access,crm)
    barrier.wait(timeout=10)
    try:admin.command({**body,'request_id':str(__import__('uuid').uuid4())});return 200
    except access_protocol.AccessFault as exc:return exc.status
  with ThreadPoolExecutor(max_workers=2) as workers:return list(workers.map(writer,range(2)))
if __name__=='__main__':unittest.main(verbosity=2)
