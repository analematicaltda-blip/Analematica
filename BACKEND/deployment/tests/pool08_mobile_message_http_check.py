"""Real mobile job HTTP, channel consent, signed opt-out and isolation. Network disabled."""
import runpy,unittest,uuid,os,hashlib,hmac
from pathlib import Path
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='mobile_http_setup');base=f['CRMHTTPChecks']
class Checks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  env=patch.dict(os.environ,{'GC017_MOBILE_FIXTURE':'1'});env.start();cls.addClassCleanup(env.stop);base.setUpClass.__func__(cls)
 tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_draft_review_queue_receipts_and_signed_opt_out_without_dispatch(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    s='' if system=='sga-cd' else '/';ctx=self.unwrap(c.get(p+'crm/context'+s,params=q));contact=self.unwrap(c.post(p+'crm/commands'+s,params=q,json={'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Persona sintética','email':uuid.uuid4().hex+'@example.test','phone':'+573'+str(uuid.uuid4().int%1000000000).zfill(9),'origin':'MOBILE_FIXTURE','responsible_ref':ctx['actor_ref']}}))['contact_id'];self.unwrap(c.post(p+'crm/commands'+s,params=q,json={'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':contact,'expected_revision':1,'data':{'channel':'SMS','purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}}))
    command={'request_id':str(uuid.uuid4()),'operation':'create','job_id':None,'expected_revision':0,'data':{'title':'SMS HTTP','channel':'SMS','contact_id':contact,'body':'Texto sin adjuntos','mode':'TEXT','media_ref':None,'confirmed_link':False}};url=p+'crm/mobile-message-commands'+s;ref=self.unwrap(c.post(url,params=q,json=command))['job_id'];self.assertTrue(self.unwrap(c.post(url,params=q,json=command))['replayed']);self.assertEqual(self.unwrap(c.get(p+'crm/mobile-message-receipts/'+command['request_id']+s,params=q))['job_id'],ref)
    for op,rev,data in [('review',1,{'confirmed_content':True,'confirmed_recipient':True}),('queue',2,{'confirmed_impact':True,'max_estimated_minor':10000})]:self.unwrap(c.post(url,params=q,json={'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':rev,'data':data}))
    d=self.unwrap(c.get(p+'crm/mobile-messages/'+ref+s,params=q));self.assertEqual(d['status'],'QUEUED');self.assertEqual(d['attempts'],0);self.assertIsNone(d['actual_cost_minor']);self.assertEqual(len(self.unwrap(c.get(p+'crm/mobile-messages/'+ref+'/history'+s,params=q))['events']),3)
    credentials=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/mobile-messages/'+ref+s,params=q,headers={'Authorization':'Bearer '+credentials['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/mobile-messages'+s,params=q,headers={'Authorization':''}).status_code,(401,403))
    report={'event_id':str(uuid.uuid4()),'job_id':ref,'provider_message_id':None,'status':'OPT_OUT','occurred_at':datetime.now(timezone.utc).isoformat()};canonical=__import__('json').dumps(report,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();fingerprint=hashlib.sha256(canonical).hexdigest();signature=hmac.new(b'synthetic-mobile-fixture-key-only-32',fingerprint.encode(),hashlib.sha256).hexdigest();response=c.post(p+'mobile-message-reports/'+ref+'/',json=report,headers={'Authorization':'','X-Mobile-Receipt-Signature':signature});self.assertEqual(response.status_code,200,response.text);self.assertEqual(self.unwrap(c.get(p+'crm/mobile-messages/'+ref+s,params=q))['status'],'SUPPRESSED')
 def test_body_limits_and_no_public_worker_execution(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';r=c.post(p+'crm/mobile-message-commands'+s,params=q,content=' '*17000,headers={'Content-Type':'application/json'});self.assertEqual(r.status_code,413,r.text);self.assertEqual(c.post(p+'crm/mobile-message-worker'+s,params=q,json={}).status_code,404)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
