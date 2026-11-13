"""Real local planning API; no Ads credentials, provider campaign creation or spend."""
import runpy,unittest,os,uuid
from pathlib import Path
from unittest.mock import patch
seed=runpy.run_path(str(Path(__file__).with_name('pool08_publishing_http_check.py')),run_name='ads_asset_setup')['seed']
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='ads_http_setup');base=f['CRMHTTPChecks']
class Checks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  env=patch.dict(os.environ,{'GC020_ADS_FIXTURE':'1'});env.start();cls.addClassCleanup(env.stop);base.setUpClass.__func__(cls)
 tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_plan_review_and_reservation_have_no_provider_effect_and_are_isolated(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    s='' if system=='sga-cd' else '/';asset=seed(c,p+'crm/',s,q);body={'request_id':str(uuid.uuid4()),'operation':'create','job_id':None,'expected_revision':0,'data':{'title':'Plan pauta HTTP','platform':'META','account_ref':'META','currency':'COP','total_budget_minor':100000,'daily_budget_minor':20000,'duration_days':5,'variants':[{'label':label,'headline':'Variante '+label,'weight':50,'media_ref':asset} for label in ('A','B')]}};url=p+'crm/ads-commands'+s;ref=self.unwrap(c.post(url,params=q,json=body))['job_id'];self.assertTrue(self.unwrap(c.post(url,params=q,json=body))['replayed'])
    for op,rev,data in [('review',1,{'confirmed_creatives':True,'confirmed_budget':True}),('approve_plan',2,{'confirmed_impact':True,'maximum_minor':100000})]:self.unwrap(c.post(url,params=q,json={'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':rev,'data':data}))
    d=self.unwrap(c.get(p+'crm/ads/'+ref+s,params=q));self.assertEqual(d['status'],'LOCAL_APPROVED');self.assertIsNone(d['remote_campaign_id']);self.assertIsNone(d['real_spend_minor']);self.assertFalse(self.unwrap(c.get(p+'crm/ads'+s,params=q))['spending_enabled']);self.assertEqual(len(self.unwrap(c.get(p+'crm/ads/'+ref+'/history'+s,params=q))['events']),3)
    cred=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/ads/'+ref+s,params=q,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/ads'+s,params=q,headers={'Authorization':''}).status_code,(401,403));self.assertEqual(c.post(p+'crm/ads-execute'+s,params=q,json={}).status_code,404)
 def test_body_limits(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';self.assertEqual(c.post(p+'crm/ads-commands'+s,params=q,content=' '*17000,headers={'Content-Type':'application/json'}).status_code,413)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
