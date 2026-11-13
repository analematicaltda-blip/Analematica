"""Private normalized connector HTTP and real owned conversations; no vendor sends."""
import runpy,unittest,uuid,os,json,hashlib,hmac
from pathlib import Path
from datetime import datetime,timezone
from unittest.mock import patch
from inbox_fixture import KEY,CHANNELS
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='inbox_http_setup');base=f['CRMHTTPChecks']
def unwrap(response):
 assert response.status_code==200,response.text
 d=response.json();return d['data'] if d.get('success') else d
def seed(client,prefix,suffix,query,system,channel='FB_DM'):
 ctx=unwrap(client.get(prefix+'context'+suffix,params=query));key=system+':'+ctx['tenant_ref']+':'+(str(query.get('provider_id')) if query.get('provider_id') else '-')
 event={'event_id':str(uuid.uuid4()),'account_ref':channel,'channel':channel,'thread_ref':'789' if channel in ('FB_DM','IG_DM') else '573123456789' if channel=='WHATSAPP' else 'thread-123' if channel=='EMAIL' else '987','message_ref':'incoming-'+uuid.uuid4().hex,'sender_ref':'person@example.test' if channel=='EMAIL' else '573123456789' if channel=='WHATSAPP' else '789','body':'Consulta sintética <img src=x onerror="window.bad=1">','occurred_at':datetime.now(timezone.utc).isoformat(),'reply_to_ref':'<original@example.test>' if channel=='EMAIL' else None,'subject':'Consulta '+channel}
 fingerprint=hashlib.sha256(json.dumps({'key':key,'event':event},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest();signature=hmac.new(KEY.encode(),fingerprint.encode(),hashlib.sha256).hexdigest();r=client.post(prefix+'inbox-ingress'+suffix,params=query,json=event,headers={'X-Inbox-Connector-Signature':signature});ref=unwrap(r)['job_id'];return ctx,event,signature,ref
class Checks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  env=patch.dict(os.environ,{'GC019_INBOX_FIXTURE':'1'});env.start();cls.addClassCleanup(env.stop);base.setUpClass.__func__(cls)
 tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def test_ingress_review_queue_and_tenant_isolation(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    native='analematica' if system=='gateway' else system;s='' if system=='sga-cd' else '/';ctx,event,signature,ref=seed(c,p+'crm/',s,q,native);self.assertTrue(unwrap(c.post(p+'crm/inbox-ingress'+s,params=q,json=event,headers={'X-Inbox-Connector-Signature':signature}))['replayed']);self.assertEqual(c.post(p+'crm/inbox-ingress'+s,params=q,json={**event,'body':'tampered'},headers={'X-Inbox-Connector-Signature':signature}).status_code,403)
    start=unwrap(c.get(p+'crm/inbox/'+ref+s,params=q))['revision'];contact=unwrap(c.post(p+'crm/commands'+s,params=q,json={'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Cliente '+system,'email':uuid.uuid4().hex+'@example.test','origin':'INBOX_FIXTURE','phone':'+573'+str(uuid.uuid4().int%1000000000).zfill(9),'responsible_ref':ctx['actor_ref']}}))['contact_id'];last=None
    for op,rev,data in [('link',1,{'contact_id':contact,'confirmed_identity':True}),('assign',2,{'actor_ref':ctx['actor_ref']}),('draft',3,{'text':'Borrador sin enviar'}),('review',4,{'confirmed_content':True,'confirmed_thread':True}),('queue',5,{'confirmed_impact':True})]:
     body={'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':start+rev-1,'data':data};last=unwrap(c.post(p+'crm/inbox-commands'+s,params=q,json=body));self.assertTrue(unwrap(c.post(p+'crm/inbox-commands'+s,params=q,json=body))['replayed'])
    self.assertEqual(last['status'],'QUEUED');d=unwrap(c.get(p+'crm/inbox/'+ref+s,params=q));self.assertIsNone(d['reply']['remote_id']);self.assertEqual(len(unwrap(c.get(p+'crm/inbox/'+ref+'/history'+s,params=q))['events']),start+5);self.assertEqual(unwrap(c.get(p+'crm/inbox-receipts/'+body['request_id']+s,params=q))['job_id'],ref)
    cred=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.get(p+'crm/inbox/'+ref+s,params=q,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/inbox'+s,params=q,headers={'Authorization':''}).status_code,(401,403))
 def test_bounded_private_ingress_and_no_public_worker(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/'
   for endpoint in ['inbox-commands','inbox-ingress']:self.assertEqual(c.post(p+'crm/'+endpoint+s,params=q,content=' '*17000,headers={'Content-Type':'application/json'}).status_code,413)
   self.assertEqual(c.post(p+'crm/inbox-worker'+s,params=q,json={}).status_code,404)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
