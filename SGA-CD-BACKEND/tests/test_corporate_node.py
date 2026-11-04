"""Corporate public intake, platform CRM isolation and owner publishing."""
import json,uuid,unittest
import test_institutional_panels as fixtures
from app.models.workspace import WorkspaceLead
from app.api.v1.endpoints import corporate
class CorporateTests(unittest.TestCase):
 setUp=fixtures.InstitutionalTests.setUp
 tearDown=fixtures.InstitutionalTests.tearDown
 login=fixtures.InstitutionalTests.login
 root='/api/v1/workspace/corporate'
 def test_public_content_and_owner_publication_conflict(self):
  self.client.headers.clear();self.assertEqual(self.client.get(self.root+'/config').json(),{'config':{},'revision':0})
  body={'config':{'hero':{'title':'Instituto <span onclick="x()">Seguro</span><img src=x onerror=x()>'}},'revision':0}
  self.assertEqual(self.client.put(self.root+'/config',json=body).status_code,401)
  self.login('full-admin_empresa');self.assertEqual(self.client.put(self.root+'/config',json=body).status_code,403)
  self.login('owner-admin_general');self.assertEqual(self.client.put(self.root+'/config',json=body).status_code,200)
  title=self.client.get(self.root+'/config').json()['config']['hero']['title'];self.assertNotIn('onclick',title);self.assertNotIn('<img',title)
  self.assertEqual(self.client.put(self.root+'/config',json=body).status_code,409)
 def test_public_request_retries_land_only_in_platform_crm(self):
  self.client.headers.clear();body={'request_id':str(uuid.uuid4()),'nombre':'Persona de prueba','entidad':'Entidad de prueba','correo':'test@example.org','telefono':'+57 3001234567','consent':True}
  for _ in range(2):self.assertEqual(self.client.post(self.root+'/inquiries',json=body).status_code,201)
  self.assertEqual(self.db.query(WorkspaceLead).count(),1)
  self.login('full-admin_empresa');self.assertEqual(self.client.get(self.root+'/inquiries').status_code,403);self.assertEqual(self.client.get('/api/v1/workspace/crm/leads').json()['leads'],[])
  self.login('owner-admin_general');self.assertEqual(len(self.client.get(self.root+'/inquiries').json()['leads']),1);self.assertEqual(len(self.client.get('/api/v1/workspace/crm/leads').json()['leads']),1)
 def test_consent_honeypot_and_input_validation(self):
  self.client.headers.clear();body={'request_id':str(uuid.uuid4()),'nombre':'Persona de prueba','entidad':'Entidad','correo':'test@example.org','telefono':'3001234567','consent':False}
  self.assertEqual(self.client.post(self.root+'/inquiries',json=body).status_code,422)
  body.update(consent=True,website='spam');self.assertEqual(self.client.post(self.root+'/inquiries',json=body).status_code,201);self.assertEqual(self.db.query(WorkspaceLead).count(),0)
  body.update(website='',tenant_id=1);self.assertEqual(self.client.post(self.root+'/inquiries',json=body).status_code,422)
 def test_unsafe_urls_and_secret_content_are_rejected(self):
  self.login('owner-admin_general')
  for config in [{'header':{'nav_cta_href':'javascript:alert(1)'}},{'verticales':{'sgacd':{'url':'javascript:alert(1)'}}},{'hero':{'api_key':'private'}},{'credentials':{'key':'private'}}]:
   self.assertEqual(self.client.put(self.root+'/config',json={'config':config,'revision':0}).status_code,422)
if __name__=='__main__':unittest.main()
