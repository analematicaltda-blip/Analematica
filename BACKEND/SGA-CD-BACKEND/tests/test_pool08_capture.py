"""SGA public capture owns its CRM transaction and checks the current publisher identity."""
import runpy,unittest,uuid,re,html
from pathlib import Path
from unittest.mock import patch
f=runpy.run_path(str(Path(__file__).with_name('test_pool08_landings.py')),run_name='capture_sga_setup')
from app.commercial.pool08.capture_models import LandingCapture,CaptureEvent
from app.commercial.pool08.crm_models import CRMContact
from app.models.user import Usuario
class Checks(unittest.TestCase):
 def setUp(self):
  f['Checks'].setUp(self)
  for m in (LandingCapture,CaptureEvent):m.__table__.create(self.db.get_bind(),checkfirst=True)
  self.b=f['Checks'].body(self);self.b['data']['content']['capture']={'notice':'Aviso sintético aceptable para la prueba','privacy_url':'https://example.test/privacy','offer_ref':None};r=self.post(self.b);self.assertEqual(r.status_code,200,r.text);self.ref=r.json()['landing_id'];self.url='/api/v1/commercial-unified/landing-pages/'+self.ref
  for op,rev in [('approve',1),('publish',2)]:self.assertEqual(self.post({**self.b,'request_id':str(uuid.uuid4()),'operation':op,'landing_id':self.ref,'expected_revision':rev,'data':{'confirmed':True}}).status_code,200)
  r=self.client.get(self.url);self.assertEqual(r.status_code,200,r.text);token=html.unescape(re.search('name="token" value="([^\"]+)"',r.text).group(1));self.data={'token':token,'name':'Visitante','email':uuid.uuid4().hex+'@example.test','phone':'','consent':'yes','company_website':''}
 tearDown=f['Checks'].tearDown;login=f['Checks'].login;post=f['Checks'].post;get=f['Checks'].get
 def submit(self):return self.client.post(self.url+'/capture',data=self.data,headers={'Origin':'http://testserver'})
 def test_capture_audit_failure_rolls_back_canonical_contact(self):
  from app.commercial.pool08.capture_store import Store
  with patch.object(Store,'append',side_effect=RuntimeError('synthetic audit unavailable')):
   with self.assertRaises(RuntimeError):self.submit()
  self.assertEqual(self.db.query(LandingCapture).count(),0);self.assertEqual(self.db.query(CRMContact).count(),0)
 def test_publisher_revocation_prevents_anonymous_write(self):
  user=self.db.get(Usuario,self.users['full-admin_empresa']);user.roles=[];user.rol='jefe_area';self.db.commit();self.assertEqual(self.submit().status_code,403);self.assertEqual(self.db.query(LandingCapture).count(),0)
 def test_wrong_browser_or_cross_origin_cannot_use_signed_form(self):
  self.client.cookies.clear();self.assertEqual(self.submit().status_code,403)
  self.assertEqual(self.client.post(self.url+'/capture',data=self.data,headers={'Origin':'https://evil.test'}).status_code,403)
 def test_committed_rate_limit_rejects_eleventh_submission(self):
  for n in range(10):
   page=self.client.get(self.url);self.data['token']=html.unescape(re.search('name="token" value="([^"]+)"',page.text).group(1));self.data['email']='limit-'+str(n)+'-'+uuid.uuid4().hex+'@example.test';self.assertEqual(self.submit().status_code,200)
  page=self.client.get(self.url);self.data['token']=html.unescape(re.search('name="token" value="([^"]+)"',page.text).group(1));self.data['email']=uuid.uuid4().hex+'@example.test';self.assertEqual(self.submit().status_code,429);self.assertEqual(self.db.query(LandingCapture).count(),10)
 def test_other_company_cannot_read_capture_metrics(self):
  self.assertEqual(self.submit().status_code,200);self.login('other-admin_empresa');self.assertEqual(self.get('landings/'+self.ref+'/captures').status_code,404)
if __name__=='__main__':unittest.main()
