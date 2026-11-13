"""Real private army HTTP: own rows, hierarchy, domain blocks and isolation."""
import runpy,unittest,uuid
from pathlib import Path
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='army_http_setup');base=f['CRMHTTPChecks']
class Checks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_neko_jarvi_soup_real_query_and_native_scope_isolation(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    s='' if system=='sga-cd' else '/';info=self.unwrap(c.get(p+'crm/army'+s,params=q));self.assertEqual(info['generals']['operational'],'Jarvi');self.assertEqual(info['generals']['optimizer'],'SOUP');body={'request_id':str(uuid.uuid4()),'operation':'prepare','job_id':None,'expected_revision':0,'data':{'question':'revisar contactos','tools':[],'modality':'TEXT','engine':'none'}};url=p+'crm/army-commands'+s;ref=self.unwrap(c.post(url,params=q,json=body))['job_id'];self.assertTrue(self.unwrap(c.post(url,params=q,json=body))['replayed'])
    for op,rev,data in [('review',1,{'confirmed_plan':True}),('queue',2,{'confirmed_scope':True}),('run',3,{})]:
     body={'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':rev,'data':data};self.unwrap(c.post(url,params=q,json=body))
    self.assertTrue(self.unwrap(c.post(url,params=q,json=body))['replayed']);d=self.unwrap(c.get(p+'crm/army/'+ref+s,params=q));self.assertEqual(d['status'],'SUCCEEDED');self.assertEqual(d['results'][0]['evidence']['source_tool'],'crm.contacts');self.assertEqual(len(d['results'][0]['chain']),6);self.assertFalse(self.unwrap(c.get(p+'crm/army/'+ref+'/soup'+s,params=q))['candidate_promoted']);self.assertEqual(len(self.unwrap(c.get(p+'crm/army/'+ref+'/history'+s,params=q))['events']),5)
    cred=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/army/'+ref+s,params=q,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/army'+s,params=q,headers={'Authorization':''}).status_code,(401,403))
 def test_unknown_tool_body_bounds_and_no_auto_approval_endpoint(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';url=p+'crm/army-commands'+s;self.assertEqual(c.post(url,params=q,content=' '*17000,headers={'Content-Type':'application/json'}).status_code,413);body={'request_id':str(uuid.uuid4()),'operation':'prepare','job_id':None,'expected_revision':0,'data':{'question':'','tools':['shell.exec'],'modality':'TEXT','engine':'none'}};response=c.post(url,params=q,json=body);self.assertIn(response.status_code,(400,422));error=response.json();self.assertEqual(error.get('code',error.get('detail',{}).get('code')),'ARMY_TOOL_NOT_ALLOWED');self.assertEqual(c.post(p+'crm/army-auto-approve'+s,params=q,json={}).status_code,404)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
