"""Real HTTP durable composition commands, isolation and receipts; no worker HTTP bypass."""
import runpy,unittest,uuid,json,os
from pathlib import Path
from unittest.mock import patch
from pool08_video_cases import PLAN
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='video_http_setup');base=f['CRMHTTPChecks']
class Checks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  env=patch.dict(os.environ,{'GC014_VIDEO_FIXTURE':'1'});env.start();cls.addClassCleanup(env.stop);base.setUpClass.__func__(cls)
 tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_queue_replay_private_receipt_cancel_and_foreign_company(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    s='' if system=='sga-cd' else '/';profiles=self.unwrap(c.get(p+'crm/generation-profiles'+s,params=q));self.assertEqual(profiles['profiles'][0]['kinds'],['VIDEO'])
    body={'request_id':str(uuid.uuid4()),'operation':'create','job_id':None,'expected_revision':0,'data':{'title':'Vídeo HTTP','kind':'VIDEO','prompt':json.dumps(PLAN),'profile_id':'video','max_cost_units':100,'confirmed_input_rights':True}}
    url=p+'crm/generation-commands'+s;created=self.unwrap(c.post(url,params=q,json=body));ref=created['job_id'];self.assertTrue(self.unwrap(c.post(url,params=q,json=body))['replayed']);self.assertEqual(self.unwrap(c.get(p+'crm/generation-receipts/'+body['request_id']+s,params=q))['job_id'],ref)
    self.assertEqual(self.unwrap(c.get(p+'crm/generation/'+ref+s,params=q))['status'],'QUEUED');self.assertEqual(c.get(p+'crm/generation/'+ref+'/result'+s,params=q).status_code,409)
    cred=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/generation/'+ref+s,params=q,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,(403,404))
    cancel={'request_id':str(uuid.uuid4()),'operation':'cancel','job_id':ref,'expected_revision':1,'data':{}};self.assertEqual(self.unwrap(c.post(url,params=q,json=cancel))['status'],'CANCELLED');self.assertEqual(c.post(p+'crm/generation-worker'+s,params=q,json={}).status_code,404)
 def test_invalid_composition_is_not_queued(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';body={'request_id':str(uuid.uuid4()),'operation':'create','job_id':None,'expected_revision':0,'data':{'title':'Vídeo HTTP','kind':'VIDEO','prompt':'{"url":"https://example.test/private"}','profile_id':'video','max_cost_units':100,'confirmed_input_rights':True}};self.assertEqual(c.post(p+'crm/generation-commands'+s,params=q,json=body).status_code,422)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
