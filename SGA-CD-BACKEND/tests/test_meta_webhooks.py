import hashlib,hmac,json,unittest
from test_instagram_login import InstagramTests
from app.models.advertising import MetaWebhookEvent
from app.services import meta_ads_service as meta

class WebhookTests(unittest.TestCase):
 setUp=InstagramTests.setUp
 tearDown=InstagramTests.tearDown
 login=InstagramTests.login
 root='/api/v1/workspace/meta/webhooks'
 def configure(self):
  response=self.client.put(self.root+'/config',json={'verify_token':'test-verifier-'+'a'*32,'accepted_ids':['1414458975087720']})
  self.assertEqual(response.status_code,200,response.text)
 def send(self,body,signature=True):
  raw=json.dumps(body).encode();headers={'Content-Type':'application/json'}
  if signature:headers['x-hub-signature-256']='sha256='+hmac.new(b'test-secret',raw,hashlib.sha256).hexdigest()
  return self.client.post(self.root+'/receive',content=raw,headers=headers)
 def test_challenge_and_wrong_verifier(self):
  self.configure();self.client.headers.clear()
  self.assertEqual(self.client.get(self.root+'/receive',params={'hub.mode':'subscribe','hub.verify_token':'wrong','hub.challenge':'123'}).status_code,403)
  response=self.client.get(self.root+'/receive',params={'hub.mode':'subscribe','hub.verify_token':'test-verifier-'+'a'*32,'hub.challenge':'123'})
  self.assertEqual(response.text,'123');self.assertEqual(response.headers['cache-control'],'no-store')
 def test_signed_encrypted_deduplicated_inbox(self):
  self.configure();body={'object':'page','entry':[{'id':'1414458975087720','messaging':[{'message':{'text':'private-test-message'}}]}]}
  self.assertEqual(self.send(body,False).status_code,403)
  self.assertEqual(self.send(body).status_code,200);self.assertEqual(self.send(body).status_code,200)
  events=self.db.query(MetaWebhookEvent).all();self.assertEqual(len(events),1);self.assertNotIn('private-test-message',events[0].encrypted_payload);self.assertIn('private-test-message',meta.decrypted(events[0].encrypted_payload));self.assertEqual(events[0].status,'received')
 def test_unknown_asset_never_stored(self):
  self.configure();self.assertFalse(self.send({'object':'page','entry':[{'id':'999'}]}).json()['stored']);self.assertEqual(self.db.query(MetaWebhookEvent).count(),0)
 def test_tenant_cannot_reconfigure_platform_inbox(self):
  self.login('full-admin_empresa');self.assertEqual(self.client.put(self.root+'/config',json={'verify_token':'x'*40,'accepted_ids':['123']}).status_code,403)

if __name__=='__main__':unittest.main()
