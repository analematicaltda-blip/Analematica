"""Consent boundary tests: provider calls mocked, no messages or live ads."""
import json
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit,parse_qs
import test_institutional_panels as fixtures
from app.models.advertising import MetaAdsApp, InstagramAuthorization, InstagramOAuthState
from app.models.corporate import CorporateOwner
from app.services import meta_ads_service as meta, instagram_service as ig
from app.services.meta_ads_graph import MetaGraphError

class InstagramTests(unittest.TestCase):
 def setUp(self):
  fixtures.InstitutionalTests.setUp(self)
  self.db.add(CorporateOwner(id=1,user_id=self.users['owner-admin_general']));self.db.commit()
  self.login('owner-admin_general')
  self.actor=meta.actor_for(self.db,self.db.get(__import__('app.models.user',fromlist=['Usuario']).Usuario,self.users['owner-admin_general']))
  self.callback='https://console.example.org'+ig.CALLBACK
  self.db.add(MetaAdsApp(id=1,app_id='123',api_version='v27.0',redirect_uris=json.dumps([self.callback]),encrypted_secret=meta.encrypted('test-secret'),configured_by=self.actor.user.id,revision=1));self.db.commit()
  ig.configure(self.db,self.actor,'1119082880751653')
 tearDown=fixtures.InstitutionalTests.tearDown
 login=fixtures.InstitutionalTests.login
 def begin(self):return ig.start(self.db,self.actor,self.callback)
 def debug(self,scopes=None):return {'data':{'is_valid':True,'app_id':'123','scopes':list(ig.REQUIRED) if scopes is None else scopes,'expires_at':0}}
 def test_config_id_callback_and_no_credentials_in_url(self):
  result=self.begin();query=parse_qs(urlsplit(result['authorization_url']).query)
  self.assertEqual(query['config_id'],['1119082880751653']);self.assertNotIn('client_secret',query)
  self.assertNotIn('test-secret',result['authorization_url'])
  self.assertNotEqual(self.db.query(InstagramOAuthState).one().state_hash,result['state'])
 def test_wrong_browser_and_redirect_never_call_provider(self):
  result=self.begin()
  with patch.object(ig.MetaGraph,'exchange_system') as exchange:
   with self.assertRaises(Exception):ig.finish(self.db,result['state'],'wrong','code')
   exchange.assert_not_called()
  with self.assertRaises(Exception):ig.start(self.db,self.actor,'https://evil.example'+ig.CALLBACK)
 def test_success_encrypted_isolated_and_no_long_lived_exchange(self):
  result=self.begin()
  with patch.object(ig.MetaGraph,'exchange_system',return_value={'access_token':'fake-system-token'}),patch.object(ig.MetaGraph,'get',return_value=self.debug()),patch.object(ig.MetaGraph,'exchange') as user_exchange:
   self.assertTrue(ig.finish(self.db,result['state'],result['browser'],'fake-code'));user_exchange.assert_not_called()
   with self.assertRaises(Exception):ig.finish(self.db,result['state'],result['browser'],'fake-code')
  auth=self.db.get(InstagramAuthorization,'platform');self.assertNotEqual(auth.encrypted_token,'fake-system-token');self.assertEqual(meta.decrypted(auth.encrypted_token),'fake-system-token')
  self.assertEqual(json.loads(auth.account),{})
 def test_missing_scope_or_wrong_app_cannot_save_authorization(self):
  for debug in [self.debug([]),{'data':{'is_valid':True,'app_id':'other','scopes':list(ig.REQUIRED),'expires_at':0}}]:
   result=self.begin()
   with patch.object(ig.MetaGraph,'exchange_system',return_value={'access_token':'fake'}),patch.object(ig.MetaGraph,'get',return_value=debug):
    self.assertFalse(ig.finish(self.db,result['state'],result['browser'],'code'))
   self.assertIsNone(self.db.get(InstagramAuthorization,'platform'))
 def test_config_change_invalidates_pending_consent(self):
  result=self.begin();ig.configure(self.db,self.actor,'456')
  with patch.object(ig.MetaGraph,'exchange_system') as exchange:
   with self.assertRaises(Exception):ig.finish(self.db,result['state'],result['browser'],'code')
   exchange.assert_not_called()
 def test_basic_and_other_roles_denied_owner_routes(self):
  for actor in ['basic-admin_empresa','full-admin_empresa']:
   self.login(actor);response=self.client.get('/api/v1/workspace/instagram/status');self.assertEqual(response.status_code,402 if actor.startswith('basic-') else 403)
 def test_callback_cookie_headers_and_no_token_returned(self):
  response=self.client.post('/api/v1/workspace/instagram/oauth/start',json={'redirect_uri':self.callback})
  self.assertEqual(response.status_code,200,response.text);self.assertIn('HttpOnly',response.headers['set-cookie']);self.assertIn('Secure',response.headers['set-cookie']);self.assertIn('SameSite=lax',response.headers['set-cookie'])
  self.assertNotIn('browser',response.json());self.assertNotIn('test-secret',response.text)
 def test_revoked_provider_token_is_safe_failure(self):
  result=self.begin()
  with patch.object(ig.MetaGraph,'exchange_system',side_effect=MetaGraphError('authorization_expired',401)):
   self.assertFalse(ig.finish(self.db,result['state'],result['browser'],'code'))
  self.assertIsNone(self.db.get(InstagramAuthorization,'platform'))

if __name__=='__main__':unittest.main()
