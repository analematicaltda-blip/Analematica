"""Run inside the backend image with its existing dependencies."""
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api import deps
from app.core.config import settings
from jose import jwt
from app.services import sso_service as broker

spec=importlib.util.spec_from_file_location('sso_routes',Path('/tmp/sso_routes.py'))
routes=importlib.util.module_from_spec(spec);spec.loader.exec_module(routes)

class RoutesTests(unittest.TestCase):
 def test_disabled_and_complete_flow(self):
  app=FastAPI();app.include_router(routes.router,prefix='/api/v1/sso')
  app.dependency_overrides[deps.get_db]=lambda:object()
  with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{'SSO_STATE_DB':folder+'/flows.sqlite3','SSO_PUBLIC_ORIGIN':'https://sga.example','SSO_GOOGLE_CLIENT_ID':'','SSO_GOOGLE_CLIENT_SECRET':''}):
   with TestClient(app,base_url='https://sga.example') as client:
    self.assertFalse(client.get('/api/v1/sso/providers').json()['google'])
    self.assertEqual(client.post('/api/v1/sso/google/start').status_code,503)
    with patch.dict(os.environ,{'SSO_GOOGLE_CLIENT_ID':'test-client','SSO_GOOGLE_CLIENT_SECRET':'test-secret','SSO_ACCOUNTS_JSON':json.dumps({'google':{'member@gmail.com':'member'}})}):
     flow=client.post('/api/v1/sso/google/start').json()
     redirect=client.get('/api/v1/sso/google/authorize',params={'flow_id':flow['flow_id']},follow_redirects=False)
     self.assertEqual(redirect.status_code,303)
     self.assertIn('HttpOnly',redirect.headers['set-cookie']);self.assertIn('Secure',redirect.headers['set-cookie'])
     with broker.db() as connection:data=broker.read_flow(connection,flow['flow_id'])
     with patch.object(broker.requests,'post',return_value=Mock(json=lambda:{'id_token':'test'})),patch.object(broker,'verify_identity',return_value='member@gmail.com'):
      callback=client.get('/api/v1/sso/google/callback',params={'state':flow['flow_id']+'.'+data['state'],'code':'test-code'})
      self.assertEqual(callback.status_code,200)
      self.assertNotIn('access_token',callback.text)
     bad=client.post('/api/v1/sso/result',json={'flow_id':flow['flow_id'],'proof':'x'*43,'password':'test-password'})
     self.assertEqual(bad.status_code,400)
     user=SimpleNamespace(id=77,activo=True,correo='member@gmail.com',nombre_completo='Member',inquilino_id=4,role_list=['profesor'],password_hash='test-hash')
     with patch.object(routes.crud.user,'get_user_by_username',return_value=user),patch.object(routes.security,'verify_password',return_value=True):
      result=client.post('/api/v1/sso/result',json={'flow_id':flow['flow_id'],'proof':flow['proof'],'password':'test-password'})
     self.assertEqual(result.status_code,200)
     self.assertEqual(result.headers['cache-control'],'no-store')
     claims=jwt.decode(result.json()['access_token'],settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
     self.assertEqual(claims['roles'],['profesor']);self.assertEqual(claims['inquilino_id'],4)
     self.assertEqual(client.post('/api/v1/sso/result',json={'flow_id':flow['flow_id'],'proof':flow['proof'],'password':'test-password'}).status_code,400)

if __name__=='__main__':unittest.main()
