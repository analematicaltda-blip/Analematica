import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch, Mock
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jose import jwt, jwk

root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('broker',root/'SGA-CD-BACKEND/app/services/sso_service.py')
sso=importlib.util.module_from_spec(spec);spec.loader.exec_module(sso)

class BrokerTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.env=patch.dict(os.environ,{'SSO_STATE_DB':self.temp.name+'/flows.sqlite3','SSO_PUBLIC_ORIGIN':'https://sga.example','SSO_GOOGLE_CLIENT_ID':'google-client','SSO_GOOGLE_CLIENT_SECRET':'test-only','SSO_MICROSOFT_CLIENT_ID':'ms-client','SSO_MICROSOFT_CLIENT_SECRET':'test-only','SSO_ACCOUNTS_JSON':json.dumps({'google':{'member@gmail.com':'member'},'microsoft':{'member@outlook.com':'member'}})})
  self.env.start()
  self.key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
  self.private=self.key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  public=self.key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)
  self.public=jwk.construct(public,algorithm='RS256').to_dict();self.public['kid']='test-key'
 def tearDown(self):self.env.stop();self.temp.cleanup()
 def token(self,provider='google',**changes):
  claims=dict(iss=sso.PROVIDERS[provider]['issuers'][0],sub='immutable-provider-id',aud='google-client' if provider=='google' else 'ms-client',exp=int(time.time())+300,iat=int(time.time()),nonce='test-nonce',email='member@gmail.com',email_verified=True)
  if provider=='microsoft':claims.update(tid=sso.MICROSOFT_TENANT,email='member@outlook.com')
  claims.update(changes)
  return jwt.encode(claims,self.private,algorithm='RS256',headers={'kid':'test-key'})
 def verify(self,provider,token,nonce='test-nonce'):
  with patch.object(sso.requests,'get',return_value=Mock(json=lambda:{'keys':[self.public]})):
   return sso.verify_identity(provider,token,nonce)
 def test_signed_identities_and_rejections(self):
  self.assertEqual(self.verify('google',self.token()),'member@gmail.com')
  self.assertEqual(self.verify('microsoft',self.token('microsoft')),'member@outlook.com')
  for changes in [{'iss':'https://attacker.example'},{'aud':'other-app'},{'nonce':'wrong'},{'exp':int(time.time())-1},{'email_verified':False}]:
   with self.assertRaises(Exception):self.verify('google',self.token(**changes))
  with self.assertRaises(Exception):self.verify('microsoft',self.token('microsoft',tid='untrusted-tenant'))
 def test_pkce_cookie_single_use_proof_and_roles(self):
  flow=sso.start('google');url,cookie=sso.authorize('google',flow['flow_id'])
  self.assertIn('code_challenge_method=S256',url)
  with sso.db() as connection:data=sso.read_flow(connection,flow['flow_id'])
  state=flow['flow_id']+'.'+data['state']
  with self.assertRaises(sso.SSOError):sso.callback('google',state,'code','wrong-cookie')
  with patch.object(sso.requests,'post',return_value=Mock(json=lambda:{'id_token':'mock-id-token','access_token':'mock-provider-token'})),patch.object(sso,'verify_identity',return_value='member@gmail.com'):
   sso.callback('google',state,'code',cookie)
  with self.assertRaises(sso.SSOError):sso.callback('google',state,'code',cookie)
  with self.assertRaises(sso.SSOError):sso.consume(flow['flow_id'],'wrong-proof',lambda *args:None)
  calls=[]
  def resolve(username,email):calls.append((username,email));return {'status':'authenticated','roles':['profesor']}
  self.assertEqual(sso.consume(flow['flow_id'],flow['proof'],resolve)['roles'],['profesor'])
  self.assertEqual(calls,[('member','member@gmail.com')])
  with self.assertRaises(sso.SSOError):sso.consume(flow['flow_id'],flow['proof'],resolve)
 def test_unknown_email_and_expiry_fail_closed(self):
  flow=sso.start('google');_,cookie=sso.authorize('google',flow['flow_id'])
  with sso.db() as connection:data=sso.read_flow(connection,flow['flow_id'])
  with patch.object(sso.requests,'post',return_value=Mock(json=lambda:{'id_token':'mock'})),patch.object(sso,'verify_identity',return_value='other@gmail.com'):
   with self.assertRaises(sso.SSOError):sso.callback('google',flow['flow_id']+'.'+data['state'],'code',cookie)
  with self.assertRaises(sso.SSOError):sso.consume(flow['flow_id'],flow['proof'],lambda *args:None)
  with sso.db() as connection:
   data=sso.read_flow(connection,flow['flow_id']);data['expires']=time.time()-1;sso.save(connection,flow['flow_id'],data)
  with self.assertRaises(sso.SSOError):sso.authorize('google',flow['flow_id'])
 def test_failed_account_check_invalidates_flow(self):
  flow=sso.start('google')
  with sso.db() as connection:
   data=sso.read_flow(connection,flow['flow_id']);data.update(status='ready',username='member',email='member@gmail.com');sso.save(connection,flow['flow_id'],data)
  def reject(*args):raise sso.SSOError('Wrong password or inactive account')
  with self.assertRaises(sso.SSOError):sso.consume(flow['flow_id'],flow['proof'],reject)
  with self.assertRaises(sso.SSOError):sso.consume(flow['flow_id'],flow['proof'],lambda *args:{'status':'authenticated'})
 def test_unconfigured_provider(self):
  with patch.dict(os.environ,{'SSO_GOOGLE_CLIENT_SECRET':''}):
   with self.assertRaises(sso.SSOError):sso.start('google')

if __name__=='__main__':unittest.main()
