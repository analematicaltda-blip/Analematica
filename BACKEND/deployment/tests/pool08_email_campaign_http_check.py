"""Real campaign HTTP and scanner-safe public unsubscribe, no message dispatch."""
import runpy,unittest,uuid,os,hmac,hashlib
from pathlib import Path
from unittest.mock import patch
from datetime import datetime,timedelta,timezone
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='email_http_setup');base=f['CRMHTTPChecks']
class Checks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  env=patch.dict(os.environ,{'GC016_EMAIL_FIXTURE':'1'});env.start();cls.addClassCleanup(env.stop);base.setUpClass.__func__(cls)
 tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_real_http_draft_preview_and_separate_review_schedule(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    s='' if system=='sga-cd' else '/';ctx=self.unwrap(c.get(p+'crm/context'+s,params=q));contact=self.unwrap(c.post(p+'crm/commands'+s,params=q,json={'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Persona prueba','email':uuid.uuid4().hex+'@example.test','origin':'CAMPAIGN_FIXTURE','responsible_ref':ctx['actor_ref']}}))['contact_id'];self.unwrap(c.post(p+'crm/commands'+s,params=q,json={'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':contact,'expected_revision':1,'data':{'channel':'EMAIL','purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}}))
    body={'request_id':str(uuid.uuid4()),'operation':'create','campaign_id':None,'expected_revision':0,'data':{'title':'Campaña HTTP','subject':'Hola {{name}}','body_text':'Texto {{company}} <script>escapado</script>','template':'LETTER','contact_ids':[contact],'exclude_contact_ids':[],'segment':'Fixture'}};url=p+'crm/email-campaign-commands'+s;ref=self.unwrap(c.post(url,params=q,json=body))['campaign_id'];self.assertTrue(self.unwrap(c.post(url,params=q,json=body))['replayed']);self.assertEqual(self.unwrap(c.get(p+'crm/email-campaign-receipts/'+body['request_id']+s,params=q))['campaign_id'],ref)
    draft=self.unwrap(c.get(p+'crm/email-campaigns/'+ref+s,params=q));self.assertEqual(draft['status'],'DRAFT');self.assertEqual(draft['recipients'][0]['attempts'],0);preview=self.unwrap(c.get(p+'crm/email-campaigns/'+ref+'/preview/'+contact+s,params=q));self.assertNotIn('<script>',preview['html']);self.assertIn('PREVIEW_NOT_A_LINK',preview['unsubscribe_url'])
    for op,rev,data in [('review',1,{'confirmed_content':True,'confirmed_audience':True}),('schedule',2,{'confirmed_impact':True,'scheduled_at':datetime.now(timezone.utc).isoformat()})]:self.unwrap(c.post(url,params=q,json={'request_id':str(uuid.uuid4()),'operation':op,'campaign_id':ref,'expected_revision':rev,'data':data}))
    d=self.unwrap(c.get(p+'crm/email-campaigns/'+ref+s,params=q));self.assertEqual(d['status'],'SCHEDULED');self.assertIsNone(d['recipients'][0]['delivered_at']);self.assertEqual(d['recipients'][0]['attempts'],0)
    system_key='analematica' if system=='gateway' else system;scope_key=system_key+':'+ctx['tenant_ref']+':'+(q.get('provider_id') or '-')
    proof=hmac.new(b'synthetic-email-fixture-key-only-32',(scope_key+':'+ref+':'+contact+':'+d['recipients'][0]['email']).encode(),hashlib.sha256).hexdigest();public=p+'email-unsubscribe/'+ref+'/'+contact+'/'+proof+'/'
    response=c.get(public,headers={'Authorization':''});self.assertEqual(response.status_code,200,response.text);self.assertNotIn(d['recipients'][0]['email'],response.text);self.assertEqual(self.unwrap(c.get(p+'crm/email-campaigns/'+ref+s,params=q))['recipients'][0]['status'],'PENDING')
    self.assertEqual(c.post(public,content='List-Unsubscribe=One-Click',headers={'Authorization':'','Content-Type':'application/x-www-form-urlencoded'}).status_code,200);self.assertEqual(self.unwrap(c.get(p+'crm/email-campaigns/'+ref+s,params=q))['recipients'][0]['status'],'SUPPRESSED')
    credentials=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/email-campaigns/'+ref+s,params=q,headers={'Authorization':'Bearer '+credentials['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/email-campaigns'+s,params=q,headers={'Authorization':''}).status_code,(401,403))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
