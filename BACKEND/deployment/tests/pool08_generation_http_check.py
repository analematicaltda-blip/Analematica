"""Real HTTP boundaries with no configured inference provider or external calls."""
import runpy,unittest,uuid
from pathlib import Path
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='generation_http_setup');base=f['CRMHTTPChecks']
class Checks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_inventory_no_model_fallback_and_private_routes(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    s='' if system=='sga-cd' else '/';profiles=self.unwrap(c.get(p+'crm/generation-profiles'+s,params=q));self.assertFalse(profiles['runtime_qualified']);self.assertTrue(profiles['worker_required']);self.assertEqual(len(profiles['catalog']['engines']),5)
    self.assertEqual(self.unwrap(c.get(p+'crm/generation'+s,params=q))['jobs'],[])
    body=dict(request_id=str(uuid.uuid4()),operation='create',job_id=None,expected_revision=0,data=dict(title='Sin modelo configurado',kind='COPY',prompt='Texto privado',profile_id='missing',max_cost_units=100,confirmed_input_rights=True))
    r=c.post(p+'crm/generation-commands'+s,params=q,json=body);self.assertEqual(r.status_code,503,r.text);self.assertNotIn('Texto privado',r.text);self.assertEqual(self.unwrap(c.get(p+'crm/generation'+s,params=q))['jobs'],[])
    self.assertIn(c.get(p+'crm/generation-profiles'+s,params=q,headers={'Authorization':''}).status_code,(401,403))
    r=c.get(p+'crm/generation/'+str(uuid.uuid4())+'/result'+s,params=q);self.assertEqual(r.status_code,404,r.text);self.assertEqual(r.headers['cache-control'],'no-store')
 def test_command_body_limits_and_no_public_worker(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/'
   for raw,status in [('{"a":1,"a":2}',400),(' '*17000,413)]:
    r=c.post(p+'crm/generation-commands'+s,params=q,content=raw,headers={'Content-Type':'application/json'});self.assertEqual(r.status_code,status,r.text)
   self.assertEqual(c.post(p+'crm/generation-worker'+s,params=q,json={}).status_code,404)
if __name__=='__main__':unittest.main()
