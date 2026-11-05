"""Direct owner entrance and real audited server commands; no provider calls."""
import json,uuid,unittest
from unittest.mock import patch
import test_institutional_panels as fixtures
from app.models.corporate import CorporateOwner,CorporatePage,CorporateCommand
from app.models.user import Usuario,Role,RolesEnum
from app.services import corporate_commands as commands
from app.services.corporate_policy import bootstrap_owner
class OwnerConsoleTests(unittest.TestCase):
 tearDown=fixtures.InstitutionalTests.tearDown
 login=fixtures.InstitutionalTests.login
 root='/api/v1/workspace/corporate'
 def setUp(self):
  fixtures.InstitutionalTests.setUp(self);commands.Setting.__table__.create(self.engine,checkfirst=True);bootstrap_owner(self.db);self.login('owner-admin_general')
 def order(self,command,target='sga',request_id=None):return self.client.post(self.root+'/commands',json={'command':command,'target':target,'request_id':request_id or str(uuid.uuid4())})
 def test_direct_login_uses_existing_owner_and_rejects_company(self):
  self.client.headers.clear()
  with patch('app.core.security.verify_password',return_value=True):
   response=self.client.post(self.root+'/login',data={'username':'owner-admin_general','password':'not-a-real-password'});self.assertEqual(response.status_code,200,response.text);self.assertIn('access_token',response.json());self.assertNotIn('refresh_token',response.json());self.assertEqual(response.json()['user']['id'],self.users['owner-admin_general'])
   response=self.client.post(self.root+'/login',data={'username':'full-admin_empresa','password':'not-a-real-password'});self.assertEqual(response.status_code,403);self.assertNotIn('access_token',response.json())
  with patch('app.core.security.verify_password',return_value=False):self.assertEqual(self.client.post(self.root+'/login',data={'username':'owner-admin_general','password':'bad'}).status_code,401)
 def test_direct_login_verifies_real_password_hash(self):
  from app.core.security import get_password_hash
  user=self.db.get(Usuario,self.users['owner-admin_general']);user.password_hash=get_password_hash('Test-Owner-Password-2026!');self.db.commit();self.client.headers.clear()
  response=self.client.post(self.root+'/login',data={'username':user.nombre_usuario,'password':'Test-Owner-Password-2026!'});self.assertEqual(response.status_code,200,response.text)
  token=response.json()['access_token'];self.client.headers['Authorization']='Bearer '+token;self.assertEqual(self.client.get(self.root+'/session').status_code,200)
  self.assertEqual(self.client.post(self.root+'/login',data={'username':user.nombre_usuario,'password':'Incorrect-password'}).status_code,401)
 def test_second_general_admin_cannot_enter_or_publish(self):
  user=self.db.get(Usuario,self.users['other-admin_empresa']);user.rol=RolesEnum.admin_general;user.roles=[self.db.query(Role).filter_by(nombre='admin_general').one()];self.db.commit();self.login('other-admin_empresa')
  self.assertEqual(self.client.get(self.root+'/session').status_code,403);self.assertEqual(self.order('Estado del sistema').status_code,403);self.assertEqual(self.client.put(self.root+'/config',json={'config':{},'revision':0}).status_code,403)
 def test_bootstrap_does_not_guess_between_multiple_owners(self):
  self.db.query(CorporateOwner).delete();user=self.db.get(Usuario,self.users['other-admin_empresa']);user.rol=RolesEnum.admin_general;user.roles=[self.db.query(Role).filter_by(nombre='admin_general').one()];self.db.commit();bootstrap_owner(self.db);self.assertIsNone(self.db.get(CorporateOwner,1));self.assertEqual(self.client.get(self.root+'/session').status_code,503)
 def test_sga_command_publishes_atomically_and_retries_once(self):
  self.db.add(commands.Setting(key='landing_hero_title',value='Original'));self.db.commit();key=str(uuid.uuid4())
  first=self.order('Cambia el título de SGA-CD a: Formación para todos',request_id=key);self.assertEqual(first.status_code,200,first.text);self.assertEqual(first.json()['status'],'executed');second=self.order('Cambia el título de SGA-CD a: Formación para todos',request_id=key);self.assertEqual(first.json(),second.json());self.assertEqual(self.db.query(CorporateCommand).count(),1);self.db.expire_all();self.assertEqual(self.db.get(commands.Setting,'landing_hero_title').value,'Formación para todos')
  self.assertEqual(self.order('Cambia el título de SGA-CD a: Otro título',request_id=key).status_code,409)
  undo=self.order('Deshacer '+key);self.assertEqual(undo.status_code,200,undo.text);self.db.expire_all();self.assertEqual(self.db.get(commands.Setting,'landing_hero_title').value,'Original');self.assertEqual(self.order('Deshacer '+key).status_code,409)
 def test_undo_refuses_to_overwrite_a_later_change(self):
  result=self.order('Cambia el título de SGA-CD a: Primera orden').json();self.db.expire_all();row=self.db.get(commands.Setting,'landing_hero_title');row.value='Edición posterior';self.db.commit();self.assertEqual(self.order('Deshacer '+result['id']).status_code,409);self.db.expire_all();self.assertEqual(self.db.get(commands.Setting,'landing_hero_title').value,'Edición posterior')
 def test_explicit_target_does_not_edit_the_wrong_landing(self):
  result=self.order('Cambia el título de SGA-CD a: Destino explícito',target='analematica');self.assertEqual(result.status_code,200,result.text);self.assertEqual(result.json()['target'],'sga');self.assertIsNone(self.db.get(CorporatePage,'analematica'))
 def test_corporate_command_publishes_and_can_be_reverted(self):
  result=self.order('Cambia la misión de Analemática a: Gestión confiable');self.assertEqual(result.status_code,200,result.text);self.assertEqual(self.client.get(self.root+'/config').json()['config']['mision']['text'],'Gestión confiable');self.assertEqual(self.order('Deshacer '+result.json()['id']).status_code,200);self.assertEqual(self.client.get(self.root+'/config').json()['config'],{})
 def test_spoken_content_order_does_not_require_colon(self):
  result=self.order('Cambia el título a Formación al alcance de todos');self.assertEqual(result.status_code,200,result.text);self.assertEqual(result.json()['data']['valor'],'Formación al alcance de todos');self.assertEqual(self.order('Estado del sistema.').json()['status'],'read')
 def test_carousel_command_clears_old_json_override_and_undo_restores_it(self):
  self.db.add(commands.Setting(key='landing_carousel_slides_json',value='[{"image":"old.jpg"}]'));self.db.commit();result=self.order('Cambia el carrusel de SGA-CD a: https://example.org/1.jpg, assets/images/2.jpg');self.assertEqual(result.status_code,200,result.text);self.db.expire_all();self.assertEqual(self.db.get(commands.Setting,'landing_carousel_slides_json').value,'');self.assertEqual(self.order('Deshacer '+result.json()['id']).status_code,200);self.db.expire_all();self.assertEqual(self.db.get(commands.Setting,'landing_carousel_slides_json').value,'[{"image":"old.jpg"}]')
 def test_unsupported_and_unsafe_orders_never_claim_success(self):
  for order in ['Borra toda la base de datos','Envía mensajes a todos','Cambia el video de SGA-CD a: javascript:alert(1)','Cambia el título de SGA-CD a: <script>bad</script>']:
   result=self.order(order);self.assertEqual(result.status_code,422,result.text)
  self.assertEqual(self.db.query(CorporateCommand).count(),0)
 def test_read_commands_and_public_content_do_not_expose_credentials(self):
  for order in ['Ayuda','Estado del sistema','Historial de órdenes','Listar empresas','Listar usuarios','Resumen CRM','Resumen catálogo','Consultar landing SGA-CD']:
   result=self.order(order);self.assertEqual(result.status_code,200,result.text);self.assertEqual(result.json()['status'],'read');self.assertNotIn('password_hash',result.text);self.assertNotIn('api_key',result.text)
  self.db.add(commands.Setting(key='private_api_key',value='DO-NOT-EXPOSE'));self.db.commit();self.client.headers.clear();self.assertNotIn('DO-NOT-EXPOSE',self.client.get(self.root+'/sga-content').text);self.assertEqual(self.order('Ayuda').status_code,401)
if __name__=='__main__':unittest.main()
