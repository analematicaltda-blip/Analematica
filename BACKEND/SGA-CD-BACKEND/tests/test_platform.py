import unittest
import test_assistance as fixtures
from app.api.v1.endpoints import platform
from app.models.user import Usuario,RolesEnum
from app.services.platform import registry

class PlatformTests(fixtures.AssistanceTests):
 def setUp(self):super().setUp();self.app.include_router(platform.router,prefix='/platform')
 def test_no_anonymous_or_nonstaff_access(self):
  self.client.headers.clear();self.assertEqual(self.client.get('/platform/manifest').status_code,401)
  self.client.headers['X-Test-User']='1';self.db.get(Usuario,1).rol=RolesEnum.alumno;self.db.commit();self.assertEqual(self.client.get('/platform/manifest').status_code,403)
 def test_identity_is_request_scoped_and_no_sso_or_production_claim(self):
  for uid,tenant in [(1,1),(2,1),(3,2)]:
   self.client.headers['X-Test-User']=str(uid);r=self.client.get('/platform/manifest');self.assertEqual(r.status_code,200);self.assertEqual(r.headers['cache-control'],'no-store');d=r.json();self.assertEqual(d['viewer'],{'user_id':uid,'tenant_id':tenant});self.assertEqual(len(d['systems']),3);self.assertFalse(d['identity']['domain_sso_enabled']);self.assertFalse(d['production_ready']);self.assertEqual(d['control']['minimum_authorizations'],2)
 def test_manifest_never_exposes_write_api(self):
  self.assertEqual(self.client.post('/platform/manifest',json={'sso':True}).status_code,405)
  result=self.client.get('/platform/manifest?tenant_id=99').json();self.assertEqual(result['viewer']['tenant_id'],1);self.assertEqual(len(result['pending_modules']),4)
for name in vars(fixtures.AssistanceTests):
 if name.startswith('test_') and name not in vars(PlatformTests):setattr(PlatformTests,name,None)
if __name__=='__main__':unittest.main()
