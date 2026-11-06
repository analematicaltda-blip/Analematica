"""Authorization/tenant isolation integration tests on disposable SQLite, no remote calls."""
import os
os.environ['SECRET_KEY']='workspace-tests-only-not-a-real-secret'
os.environ['DATABASE_URL']='sqlite://'
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'BACKEND/SGA-CD-BACKEND'))
from datetime import datetime,timedelta,timezone
import tempfile
import unittest
from unittest.mock import patch,Mock
from fastapi import FastAPI,Depends,HTTPException,Request
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import Usuario,Role,RolesEnum
from app.models.tenancy import Inquilino
from app.models.billing import Suscripcion,ConsumoInquilino
from app.models.workspace import WorkspaceAsset,WorkspaceGrant,WorkspaceChannel
from app.api import deps
from app.api.v1.endpoints import workspace,tenancy
from app.services import workspace_service as ws
from app.services.workspace_guard import WorkspaceLegacyGuard
from app.core.config import settings

class WorkspaceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.engine=create_engine('sqlite:///'+self.temp.name+'/test.db',connect_args={'check_same_thread':False})
  Base.metadata.create_all(self.engine);self.factory=sessionmaker(bind=self.engine);self.db=self.factory()
  self.users={}
  for role in RolesEnum:self.db.add(Role(nombre=role.value))
  self.db.commit()
  for name,plan in [('owner','basico'),('basic','basico'),('full','full'),('other','full')]:
   tenant=Inquilino(nombre_empresa=name,plan=plan,activo=True);self.db.add(tenant);self.db.flush()
   if plan=='full':self.db.add(Suscripcion(inquilino_id=tenant.id,plan='full',estado='activa',fecha_inicio=datetime.now(timezone.utc)-timedelta(days=1),fecha_fin=datetime.now(timezone.utc)+timedelta(days=30)))
   for role in (['admin_general'] if name=='owner' else ['admin_empresa','jefe_area','profesor']):
    user=Usuario(inquilino_id=tenant.id,nombre_usuario=name+'-'+role,password_hash='not-used',rol=RolesEnum(role),activo=True,correo=name+'-'+role+'@example.org',nombre_completo=name+' '+role)
    user.roles=[self.db.query(Role).filter_by(nombre=role).one()];self.db.add(user);self.db.flush();self.users[name+'-'+role]=user.id
  self.db.commit()
  # This regression fixture models explicit administrative restrictions, not default inheritance.
  member=self.users['full-jefe_area']
  for permission in ws.PERMISSIONS:self.db.add(WorkspaceGrant(tenant_id=self.db.get(Usuario,member).inquilino_id,user_id=member,permission=permission,enabled=False,granted_by=self.users['full-admin_empresa']))
  self.db.commit()
  app=FastAPI();app.include_router(workspace.router,prefix='/api/v1/workspace');app.include_router(tenancy.router,prefix='/api/v1/tenancy')
  def database():
   with self.factory() as db:yield db
  def identity(request:Request,db=Depends(deps.get_db)):
   try:claims=jwt.decode(request.headers.get('Authorization','')[7:],settings.SECRET_KEY,algorithms=[settings.ALGORITHM]);user=db.get(Usuario,int(claims['sub']))
   except Exception:raise HTTPException(401,'login')
   if not user:raise HTTPException(401,'login')
   return user
  app.dependency_overrides[deps.get_db]=database;app.dependency_overrides[deps.get_current_active_user]=identity
  app.add_middleware(WorkspaceLegacyGuard,session_factory=self.factory)
  @app.post('/api/v1/admin_general/crm/generate_predis_media')
  @app.post('/api/v1/video_distribution/publish')
  def old():return {'legacy_called':True}
  self.client=TestClient(app);self.login('full-admin_empresa')
 def tearDown(self):self.db.close();self.engine.dispose();self.temp.cleanup()
 def login(self,name,roles=None):
  value=jwt.encode({'sub':str(self.users[name]),'type':'access','exp':datetime.now(timezone.utc)+timedelta(hours=1),'role_codes':roles or ['admin_general']},settings.SECRET_KEY,algorithm=settings.ALGORITHM)
  self.client.headers['Authorization']='Bearer '+value
 def get(self,path):return self.client.get('/api/v1/workspace'+path)
 def post(self,path,body):return self.client.post('/api/v1/workspace'+path,json=body)
 def test_basic_denies_every_advanced_operation_even_with_forged_cached_roles(self):
  self.login('basic-admin_empresa')
  self.assertFalse(self.get('/session').json()['full_enabled'])
  with patch.object(ws,'worker') as worker:
   for path in ['/assets','/crm/leads','/studio/status','/inbox/status']:self.assertEqual(self.get(path).status_code,402,path)
   for path,body in [('/studio/script',{'prompt':'a'}),('/studio/reel',{'title':'a'}),('/studio/image',{'prompt':'a'}),('/youtube/upload-private',{'asset_id':'a','title':'a','made_for_kids':False,'confirm_private':True})]:self.assertEqual(self.post(path,body).status_code,402,path)
   worker.assert_not_called()
  self.assertEqual(self.db.query(ConsumoInquilino).count(),0)
 def test_full_delegation_and_revocation_are_checked_every_request(self):
  member=self.users['full-jefe_area'];self.login('full-jefe_area')
  self.assertEqual(self.get('/crm/leads').status_code,403)
  self.login('full-admin_empresa')
  result=self.client.put(f'/api/v1/workspace/team/{member}/permissions',json={'permissions':{'crm':True,'publish':True}})
  self.assertEqual(result.status_code,200,result.text)
  self.login('full-jefe_area');self.assertEqual(self.post('/crm/leads',{'name':'Own lead'}).status_code,201)
  self.assertEqual(self.get('/assets').status_code,200) # publishers need not also be creators
  self.assertEqual(self.post('/studio/reel',{'title':'denied'}).status_code,403)
  self.login('full-admin_empresa');self.client.put(f'/api/v1/workspace/team/{member}/permissions',json={'permissions':{'crm':False}})
  self.login('full-jefe_area');self.assertEqual(self.get('/crm/leads').status_code,403)
 def test_grants_cannot_cross_tenants_or_promote_non_administrative_accounts(self):
  for name,expected in [('other-jefe_area',404),('full-profesor',403),('full-admin_empresa',403)]:
   result=self.client.put(f'/api/v1/workspace/team/{self.users[name]}/permissions',json={'permissions':{'media':True}});self.assertEqual(result.status_code,expected)
 def test_crm_assets_and_owner_are_separate(self):
  lead=self.post('/crm/leads',{'name':'Company contact'}).json()['id']
  access=ws.access_for(self.db,self.db.get(Usuario,self.users['full-admin_empresa']))
  asset=ws.save_asset(self.db,access,{'filename':'a'*32+'.mp4'},'reel','company reel')
  self.login('other-admin_empresa');self.assertEqual(self.get('/crm/leads').json()['leads'],[])
  self.assertEqual(self.client.put('/api/v1/workspace/crm/leads/'+lead,json={'name':'stolen'}).status_code,404)
  self.assertEqual(self.get('/assets/'+asset['id']+'/download').status_code,404)
  self.login('owner-admin_general');session=self.get('/session').json();self.assertTrue(session['full_enabled']);self.assertEqual(session['scope'],'platform');self.assertEqual(self.get('/assets').json()['assets'],[])
 def test_invalid_subscription_and_inactive_company_fail_closed(self):
  user=self.db.get(Usuario,self.users['full-admin_empresa']);sub=self.db.query(Suscripcion).filter_by(inquilino_id=user.inquilino_id).one()
  for state in ['vencida','unknown']:
   sub.estado=state;self.db.commit();self.assertFalse(self.get('/session').json()['full_enabled'])
  sub.estado='cancelada';self.db.commit();self.assertTrue(self.get('/session').json()['full_enabled']) # paid period remains valid
  sub.estado='activa';sub.fecha_fin=datetime.now(timezone.utc)-timedelta(days=1);self.db.commit();self.assertFalse(self.get('/session').json()['full_enabled'])
  self.db.delete(sub);self.db.commit();self.assertFalse(self.get('/session').json()['full_enabled'])
  user.inquilino.activo=False;self.db.commit();self.assertEqual(self.get('/session').status_code,403)
 def test_failed_generation_refunds_quota_and_success_consumes(self):
  with patch.object(ws,'worker',side_effect=HTTPException(503,'offline')):self.assertEqual(self.post('/studio/script',{'prompt':'test'}).status_code,503)
  self.assertEqual(self.db.query(ConsumoInquilino).one().cantidad_usada,0)
  with patch.object(ws,'worker',return_value=Mock(json=lambda:{'text':'real mocked provider result'})):
   self.assertEqual(self.post('/studio/script',{'prompt':'test'}).status_code,200)
  self.db.expire_all();self.assertEqual(self.db.query(ConsumoInquilino).one().cantidad_usada,1)
 def test_atomic_quota_limit_and_invalid_asset_refund(self):
  access=ws.access_for(self.db,self.db.get(Usuario,self.users['full-admin_empresa']))
  limit=access.caps.monthly_limits['reels'];self.db.add(ConsumoInquilino(inquilino_id=access.tenant.id,periodo=datetime.now(timezone.utc).strftime('%Y-%m'),capacidad='reels',cantidad_usada=limit-1));self.db.commit()
  ws.reserve(self.db,access,'reels')
  with self.assertRaises(HTTPException) as error:ws.reserve(self.db,access,'reels')
  self.assertEqual(error.exception.status_code,429)
  with patch.object(ws,'worker',return_value=Mock(json=lambda:{'filename':'../../invalid.png'})):
   self.assertEqual(self.post('/studio/image',{'prompt':'test'}).status_code,502)
  self.db.expire_all();self.assertEqual(self.db.query(ConsumoInquilino).filter_by(capacidad='images').one().cantidad_usada,0)
 def test_future_subscription_is_not_yet_eligible(self):
  user=self.db.get(Usuario,self.users['full-admin_empresa']);sub=self.db.query(Suscripcion).filter_by(inquilino_id=user.inquilino_id).one();sub.fecha_inicio=datetime.now(timezone.utc)+timedelta(days=2);self.db.commit()
  self.assertFalse(self.get('/session').json()['full_enabled'])
 def test_private_publication_requires_own_encrypted_channel_and_is_idempotent(self):
  access=ws.access_for(self.db,self.db.get(Usuario,self.users['full-admin_empresa']));asset=ws.save_asset(self.db,access,{'filename':'b'*32+'.mp4'},'reel','reel')
  body={'asset_id':asset['id'],'title':'private test','made_for_kids':False,'confirm_private':True}
  with patch.object(ws,'worker') as worker:self.assertEqual(self.post('/youtube/upload-private',body).status_code,409);worker.assert_not_called()
  secrets={'client_id':'company-client','client_secret':'test-secret-not-real','refresh_token':'test-refresh-not-real'}
  result=self.client.put('/api/v1/workspace/channels/youtube',json={'label':'company',**secrets});self.assertEqual(result.status_code,200,result.text)
  for value in secrets.values():self.assertNotIn(value,self.get('/channels').text)
  self.assertNotIn(secrets['refresh_token'],self.db.query(WorkspaceChannel).one().encrypted_credentials)
  with patch.object(ws,'worker',return_value=Mock(json=lambda:{'privacy':'private','video_id':'test-video'})) as worker:
   self.assertEqual(self.post('/youtube/upload-private',body).status_code,200);self.assertTrue(self.post('/youtube/upload-private',body).json()['duplicate_prevented']);self.assertEqual(worker.call_count,1)
   self.assertEqual(worker.call_args.args[1]['workspace'],access.scope);self.assertEqual(worker.call_args.args[1]['youtube_refresh_token'],secrets['refresh_token'])
  self.assertEqual(self.db.query(ConsumoInquilino).filter_by(capacidad='social_posts').one().cantidad_usada,1)
  self.login('other-admin_empresa');self.assertEqual(self.get('/channels').json()['channels'],[])
 def test_legacy_endpoints_cannot_bypass_plan_or_company_channel(self):
  self.login('basic-admin_empresa');self.assertEqual(self.client.post('/api/v1/admin_general/crm/generate_predis_media').status_code,402)
  self.login('full-jefe_area');self.assertEqual(self.client.post('/api/v1/admin_general/crm/generate_predis_media').status_code,403)
  self.login('full-admin_empresa');self.assertEqual(self.client.post('/api/v1/video_distribution/publish').status_code,409)
  self.login('owner-admin_general');self.assertEqual(self.client.post('/api/v1/video_distribution/publish').status_code,200)
 def test_registration_commits_basic_company_and_returns_compatible_names(self):
  body={'nombre_empresa':'New company','admin_nombre_completo':'New admin','admin_email':'new@example.org','admin_password':'test-password-only-12345'}
  result=self.client.post('/api/v1/tenancy/register',json=body);self.assertEqual(result.status_code,200,result.text)
  data=result.json();self.assertEqual(data['tenant']['nombre'],data['tenant']['nombre_empresa']);self.assertEqual(data['admin']['nombre_usuario'],'new@example.org')
  with self.factory() as db:
   user=db.query(Usuario).filter_by(correo='new@example.org').one();self.assertFalse(ws.access_for(db,user).full);self.assertIn('admin_empresa',ws.roles_of(user))
  self.assertEqual(self.client.post('/api/v1/tenancy/register',json=body).status_code,400)

if __name__=='__main__':unittest.main()
