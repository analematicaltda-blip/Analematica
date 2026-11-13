"""Real local HTTP persistence and isolation; no provider network."""
import runpy,unittest,uuid,os,io,json,base64
from pathlib import Path
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
from PIL import Image
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='publishing_http_setup');base=f['CRMHTTPChecks']
def seed(client,prefix,suffix,query):
 image=io.BytesIO();Image.new('RGB',(32,32),(17,48,75)).save(image,format='PNG');metadata={'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':{'title':'Activo publicación sintético','classification':'MARKETING','brand':{'name':'Empresa','tagline':'Prueba','template':'SQUARE'},'rights':{'holder':'Fixture','license':'OWNED','reference':'Creado en laboratorio','valid_until':None,'public_web':True}}};r=client.post(prefix+'library-upload'+suffix,params=query,content=image.getvalue(),headers={'Content-Type':'image/png','X-Library-Metadata':base64.b64encode(json.dumps(metadata).encode()).decode()});assert r.status_code==200,r.text;v=r.json();ref=v.get('data',v)['item_id']
 for op,revision,data in [('approve',1,{'rights_confirmed':True,'privacy_reviewed':True}),('publish',2,{'confirmed':True})]:
  r=client.post(prefix+'library-commands'+suffix,params=query,json={'request_id':str(uuid.uuid4()),'operation':op,'item_id':ref,'expected_revision':revision,'data':data});assert r.status_code==200,r.text
 r=client.get(prefix+'library/'+ref+suffix,params=query);assert r.status_code==200;r=r.json();d=r.get('data',r);version=d['versions'][0];return {'item_id':ref,'version':1,'sha256':version['delivery_sha256']}
class Checks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  env=patch.dict(os.environ,{'GC018_PUBLISH_FIXTURE':'1'});env.start();cls.addClassCleanup(env.stop);base.setUpClass.__func__(cls)
 tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_calendar_review_receipt_idempotency_and_company_isolation(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    s='' if system=='sga-cd' else '/';asset=seed(c,p+'crm/',s,q);body={'request_id':str(uuid.uuid4()),'operation':'create','job_id':None,'expected_revision':0,'data':{'title':'Calendario HTTP','caption':'Contenido sintético','format':'FACEBOOK_PHOTO','account_ref':'owned-page-fixture','visibility':'PUBLIC','disclosure':'NONE','media_ref':asset}};url=p+'crm/publication-commands'+s;ref=self.unwrap(c.post(url,params=q,json=body))['job_id'];self.assertTrue(self.unwrap(c.post(url,params=q,json=body))['replayed'])
    for op,rev,data in [('review',1,{'confirmed_content':True,'confirmed_account':True}),('schedule',2,{'confirmed_impact':True,'scheduled_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()})]:self.unwrap(c.post(url,params=q,json={'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':rev,'data':data}))
    d=self.unwrap(c.get(p+'crm/publications/'+ref+s,params=q));self.assertEqual(d['status'],'SCHEDULED');self.assertEqual(d['attempts'],0);self.assertIsNone(d['published_at']);self.assertEqual(len(self.unwrap(c.get(p+'crm/publications/'+ref+'/history'+s,params=q))['events']),3);self.assertEqual(self.unwrap(c.get(p+'crm/publication-receipts/'+body['request_id']+s,params=q))['job_id'],ref)
    cred=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/publications/'+ref+s,params=q,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/publications'+s,params=q,headers={'Authorization':''}).status_code,(401,403));self.assertEqual(c.post(p+'crm/publication-worker'+s,params=q,json={}).status_code,404)
 def test_body_limits(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';r=c.post(p+'crm/publication-commands'+s,params=q,content=' '*17000,headers={'Content-Type':'application/json'});self.assertEqual(r.status_code,413,r.text)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
