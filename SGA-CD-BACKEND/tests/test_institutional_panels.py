"""Real ORM/API role, plan, company and BI tests; no providers or fabricated measurements."""
import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ['SECRET_KEY']='institutional-test-only-not-real'
os.environ['DATABASE_URL']='sqlite://'
from datetime import datetime,timedelta,timezone
import tempfile,unittest
from unittest.mock import patch
from fastapi import FastAPI,Depends,Request,HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt
import app.models
from app.models.base import Base
from app.models.user import Usuario,Role,RolesEnum,Alumno,Profesor
from app.models.tenancy import Inquilino
from app.models.billing import Suscripcion,ConsumoInquilino
from app.models.area import Area
from app.models.catalog import CatalogoEspecialidad,EmpresaEspecialidad
from app.models.academic import ProcesoFormacion,Clase,Inscripcion
from app.models.institutional import InstitutionalProcess,EnrollmentEvent
from app.models.workspace import WorkspaceGrant
from app.api import deps
from app.api.v1.endpoints import workspace,institutional
from app.services import workspace_service as ws,institutional_service as bi
from app.services.role_contracts import NAMES,MANAGEMENT
from app.core.config import settings

class InstitutionalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.engine=create_engine('sqlite:///'+self.tmp.name+'/db.sqlite',connect_args={'check_same_thread':False});Base.metadata.create_all(self.engine);self.factory=sessionmaker(bind=self.engine);self.db=self.factory();self.users={};self.tenants={}
  for role in RolesEnum:self.db.add(Role(nombre=role.value))
  self.sport=Area(nombre='Deportes');self.culture=Area(nombre='Cultura');self.db.add_all([self.sport,self.culture]);self.db.flush()
  for label,plan in [('owner','basico'),('basic','basico'),('full','full'),('other','full')]:
   tenant=Inquilino(nombre_empresa=label+' entidad',plan=plan,activo=True);self.db.add(tenant);self.db.flush();self.tenants[label]=tenant.id
   if plan=='full':self.db.add(Suscripcion(inquilino_id=tenant.id,plan='full',estado='activa',fecha_inicio=datetime.now(timezone.utc)-timedelta(days=80),fecha_fin=datetime.now(timezone.utc)+timedelta(days=30)))
   for role in (['admin_general'] if label=='owner' else list(NAMES)):
    user=Usuario(inquilino_id=tenant.id,nombre_usuario=label+'-'+role,correo=label+'-'+role+'@example.org',nombre_completo=label+' '+role,rol=RolesEnum(role),password_hash='test-no-login',activo=True);user.roles=[self.db.query(Role).filter_by(nombre=role).one()];self.db.add(user);self.db.flush();self.users[label+'-'+role]=user.id
  self.db.commit()
  app=FastAPI();app.include_router(workspace.router,prefix='/api/v1/workspace')
  def database():
   with self.factory() as db:yield db
  def identity(request:Request,db=Depends(deps.get_db)):
   try:claims=jwt.decode(request.headers.get('Authorization','')[7:],settings.SECRET_KEY,algorithms=[settings.ALGORITHM]);user=db.get(Usuario,int(claims['sub']))
   except Exception:raise HTTPException(401,'session')
   if not user:raise HTTPException(401,'session')
   user.role_codes=['admin_general'] # untrusted/stale claims must never affect new policy
   return user
  app.dependency_overrides[deps.get_db]=database;app.dependency_overrides[deps.get_current_active_user]=identity;self.client=TestClient(app);self.login('full-admin_empresa')
 def tearDown(self):self.db.close();self.engine.dispose();self.tmp.cleanup()
 def login(self,name):
  self.client.headers['Authorization']='Bearer '+jwt.encode({'sub':str(self.users[name]),'exp':datetime.now(timezone.utc)+timedelta(hours=1),'type':'access'},settings.SECRET_KEY,algorithm=settings.ALGORITHM)
 def get(self,path):return self.client.get('/api/v1/workspace/institutional'+path)
 def post(self,path,body,method='POST'):return self.client.request(method,'/api/v1/workspace/institutional'+path,json=body)
 def fixtures(self,label='full'):
  tenant=self.tenants[label];now=datetime.now(timezone.utc);joined=now-timedelta(days=60)
  spec1=CatalogoEspecialidad(vertical='deporte',categoria='Prueba',codigo_canonico=label+'sport',nombre=label+' Deporte',es_estandar=True,activo=True);spec2=CatalogoEspecialidad(vertical='cultura',categoria='Prueba',codigo_canonico=label+'culture',nombre=label+' Cultura',es_estandar=True,activo=True);self.db.add_all([spec1,spec2]);self.db.flush()
  for spec in [spec1,spec2]:self.db.add(EmpresaEspecialidad(inquilino_id=tenant,especialidad_id=spec.id,activa=True))
  sport=ProcesoFormacion(inquilino_id=tenant,nombre_proceso=label+' proceso deportivo',tipo_proceso='deporte');culture=ProcesoFormacion(inquilino_id=tenant,nombre_proceso=label+' proceso cultural',tipo_proceso='cultura');self.db.add_all([sport,culture]);self.db.flush()
  for process,spec in [(sport,spec1),(culture,spec2)]:self.db.add(InstitutionalProcess(tenant_id=tenant,process_id=process.id,specialty_id=spec.id,recorded_by=self.users[label+'-admin_empresa']))
  classes=[]
  for process,area in [(sport,'Deportes'),(sport,'Deportes'),(culture,'Cultura')]:
   lesson=Clase(inquilino_id=tenant,nombre_clase='Clase',area=area,proceso_id=process.id,grupo='Grupo A');self.db.add(lesson);self.db.flush();classes.append(lesson)
  students=[]
  for i in range(3):
   user=Usuario(inquilino_id=tenant,nombre_usuario=label+'student'+str(i),nombre_completo='Alumno real de prueba',rol=RolesEnum.alumno,password_hash='not-real',activo=i!=0);self.db.add(user);self.db.flush();student=Alumno(inquilino_id=tenant,usuario_id=user.id,genero='F' if i==2 else 'M',grupo_etario='Juvenil',barrio='Zona '+str(i));self.db.add(student);self.db.flush();students.append(student)
  enrollments=[]
  for student,lesson in [(students[0],classes[0]),(students[0],classes[1]),(students[1],classes[0]),(students[2],classes[2])]:
   row=Inscripcion(inquilino_id=tenant,alumno_id=student.id,clase_id=lesson.id,fecha_inscripcion=joined,area=lesson.area);self.db.add(row);self.db.flush();enrollments.append(row)
  for row in enrollments[:3]:self.db.add(EnrollmentEvent(tenant_id=tenant,enrollment_id=row.id,status='activa',reason='no_aplica',effective_at=joined+timedelta(days=1),recorded_by=self.users[label+'-admin_empresa']))
  self.db.add(EnrollmentEvent(tenant_id=tenant,enrollment_id=enrollments[2].id,status='retirada',reason='desercion',effective_at=now-timedelta(days=10),recorded_by=self.users[label+'-admin_empresa']))
  self.db.commit();return spec1,spec2,sport,culture,enrollments
 def test_all_company_roles_inherit_basic_or_full_without_url_upgrades(self):
  for label in ['basic','full']:
   for role in NAMES:
    self.login(label+'-'+role);response=self.get('/context?role='+role+'&plan=full');self.assertEqual(response.status_code,200,response.text);value=response.json();self.assertEqual(value['plan'],'basico' if label=='basic' else 'full');self.assertEqual(any(value['permissions'].values()),label=='full' and role in MANAGEMENT)
 def test_owner_has_no_subscription_gate_or_commercial_quota(self):
  self.login('owner-admin_general');response=self.client.get('/api/v1/workspace/session');self.assertTrue(response.json()['full_enabled']);self.assertEqual(response.json()['plan'],'platform')
  actor=ws.access_for(self.db,self.db.get(Usuario,self.users['owner-admin_general']))
  for _ in range(55):ws.reserve(self.db,actor,'social_posts')
  self.assertEqual(self.db.query(ConsumoInquilino).filter_by(capacidad='platform_social_posts').one().cantidad_usada,55)
 def test_only_owner_can_review_22_panel_variants_and_not_change_tenant_license(self):
  self.assertEqual(self.get('/context?review=true&role=admin_empresa&plan=full').status_code,403)
  self.login('owner-admin_general')
  for role in NAMES:
   for plan in ['basico','full']:
    value=self.get(f'/context?review=true&role={role}&plan={plan}&tenant_id={self.tenants["basic"]}').json();self.assertTrue(value['review']);self.assertEqual(value['plan'],plan)
  self.db.expire_all();self.assertEqual(self.db.get(Inquilino,self.tenants['basic']).plan,'basico')
 def test_role_urls_and_tenant_parameters_cannot_impersonate(self):
  self.login('basic-alumno');self.assertEqual(self.get('/context?role=admin_empresa').status_code,403);self.assertEqual(self.get('/dashboard?role=alumno').status_code,403)
  self.login('full-admin_empresa');self.assertEqual(self.get('/context?tenant_id='+str(self.tenants['other'])).status_code,403)
 def test_bi_counts_people_separately_from_enrollments_and_explicit_dropouts(self):
  spec1,spec2,_,_,_=self.fixtures();response=self.get('/dashboard?role=admin_empresa');self.assertEqual(response.status_code,200,response.text);value=response.json();self.assertEqual(value['kpis']['students'],3);self.assertEqual(value['kpis']['enrollments'],4);self.assertEqual(value['kpis']['active_enrollments'],2);self.assertEqual(value['kpis']['dropouts'],1);self.assertEqual(value['quality']['without_status'],1)
  sport=next(row for row in value['specialties'] if row['id']==spec1.id);self.assertEqual((sport['students'],sport['enrollments'],sport['dropouts']),(2,3,1))
 def test_slicers_filter_all_metrics_and_as_of_status_is_historical(self):
  spec1,_,_,_,_=self.fixtures();value=self.get('/dashboard?role=admin_empresa&vertical=cultura').json();self.assertEqual(value['kpis']['students'],1);self.assertEqual(value['kpis']['sports'],0);self.assertEqual(value['kpis']['cultural'],1)
  end=(datetime.now(timezone.utc)-timedelta(days=20)).date();value=self.get('/dashboard?role=admin_empresa&end='+str(end)).json();self.assertEqual(value['kpis']['dropouts'],0);self.assertEqual(value['kpis']['active_enrollments'],3)
  self.assertEqual(self.get('/dashboard?role=admin_empresa&start=2030-01-01&end=2020-01-01').status_code,422)
 def test_basic_administrators_get_real_analytics_without_crm(self):
  self.fixtures('basic');self.login('basic-admin_empresa');value=self.get('/dashboard?role=admin_empresa').json();self.assertEqual(value['kpis']['students'],3);self.assertFalse(self.get('/context?role=admin_empresa').json()['full_enabled'])
 def test_area_scopes_apply_and_absent_area_never_grants_whole_company(self):
  self.fixtures();self.login('full-jefe_area');self.assertEqual(self.get('/dashboard?role=jefe_area').json()['kpis']['students'],0)
  self.login('full-admin_empresa');member=self.users['full-jefe_area'];self.assertEqual(self.post(f'/team/{member}/assignment',{'area_ids':[self.sport.id]},'PUT').status_code,200)
  self.login('full-jefe_area');value=self.get('/dashboard?role=jefe_area').json();self.assertEqual(value['kpis']['students'],2);self.assertEqual(value['kpis']['cultural'],0)
 def test_explicit_full_permission_restriction_and_restore_inheritance(self):
  member=self.users['full-coordinador'];self.db.add(WorkspaceGrant(tenant_id=self.tenants['full'],user_id=member,permission='media',enabled=False,granted_by=self.users['full-admin_empresa']));self.db.commit()
  self.login('full-coordinador');self.assertFalse(self.get('/context?role=coordinador').json()['permissions']['media'])
  self.login('full-admin_empresa');self.assertEqual(self.client.delete(f'/api/v1/workspace/institutional/team/{member}/permissions-overrides').status_code,200)
  self.login('full-coordinador');self.assertTrue(self.get('/context?role=coordinador').json()['permissions']['media'])
 def test_classification_does_not_infer_dropout_from_inactive_account(self):
  _,_,_,_,rows=self.fixtures();row=rows[-1];self.assertEqual(self.post('/enrollments/'+str(row.id)+'/status',{'status':'retirada','reason':'no_aplica'}).status_code,422)
  self.assertEqual(self.post('/enrollments/'+str(row.id)+'/status',{'status':'retirada','reason':'traslado'}).status_code,200)
  value=self.get('/dashboard?role=admin_empresa').json();self.assertEqual(value['kpis']['dropouts'],1);self.assertEqual(value['states']['retirada'],2)
 def test_profile_name_persists_and_company_cross_access_is_denied(self):
  self.assertEqual(self.post('/profile',{'nombre_empresa':'Instituto Deportivo y Cultural','municipio':'Bogotá','pais':'Colombia','direccion':'Sede central'},'PUT').status_code,200)
  self.login('full-profesor');value=self.get('/context?role=profesor').json();self.assertEqual(value['company']['name'],'Instituto Deportivo y Cultural');self.assertEqual(self.post('/profile',{'nombre_empresa':'Wrong'},'PUT').status_code,403)
 def test_team_creation_respects_contracts_and_never_returns_password(self):
  secret='Secure-test-password-123';value=self.post('/team',{'name':'Nuevo coordinador','email':'new-coordinator@example.org','password':secret,'role':'coordinador','area_ids':[self.sport.id]});self.assertEqual(value.status_code,201,value.text);self.assertNotIn(secret,value.text)
  user=self.db.get(Usuario,value.json()['id']);self.assertTrue(ws.access_for(self.db,user).permissions['media'])
  self.assertEqual(self.post('/team',{'name':'Wrong','email':'wrong@example.org','password':secret,'role':'admin_general'}).status_code,403)
  self.login('full-profesor');self.assertEqual(self.get('/team').status_code,403)
 def test_billing_downgrade_blocks_full_for_the_whole_administrative_team(self):
  tenant=self.db.get(Inquilino,self.tenants['full']);tenant.plan='basico';sub=self.db.query(Suscripcion).filter_by(inquilino_id=tenant.id).one();sub.plan='basico';self.db.commit()
  for role in MANAGEMENT:
   self.login('full-'+role);self.assertFalse(self.get('/context?role='+role).json()['full_enabled'])
 def test_original_1000_entry_catalog_is_exact_and_mutations_are_scoped(self):
  from app.core.catalogo_data import CATALOGO_OFICIAL
  self.assertEqual({kind:sum(item['vertical']==kind for item in CATALOGO_OFICIAL) for kind in ['deporte','cultura']},{'deporte':500,'cultura':500})
  self.fixtures();self.login('full-profesor');self.assertEqual(self.post('/catalog/adopt',{'ids':[1]}).status_code,403)
 def test_unmapped_processes_remain_visible_without_invented_specialties(self):
  _,_,sport,_,_=self.fixtures();self.db.query(InstitutionalProcess).filter_by(process_id=sport.id).delete();self.db.commit();value=self.get('/dashboard?role=admin_empresa').json();self.assertEqual(value['kpis']['enrollments'],4);self.assertEqual(value['quality']['without_specialty'],3);self.assertTrue(any(row['name']=='Sin especialidad vinculada' for row in value['specialties']))
 def test_effective_date_and_tenant_boundaries_preserve_status_history(self):
  *_,rows=self.fixtures('other');self.assertEqual(self.post('/enrollments/'+str(rows[0].id)+'/status',{'status':'activa'}).status_code,404)
  *_,own=self.fixtures();before=self.db.query(EnrollmentEvent).count();self.assertEqual(self.post('/enrollments/'+str(own[0].id)+'/status',{'status':'pausada'}).status_code,200);self.assertEqual(self.db.query(EnrollmentEvent).count(),before+1)

if __name__=='__main__':unittest.main()
