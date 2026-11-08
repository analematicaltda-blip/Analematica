"""Editorial contract tests; provider responses are explicitly simulated."""
import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import httpx
from fastapi import HTTPException
import test_assistance as fixtures
from app.api.v1.endpoints import assistance_content
from app.models.assistance import ContentDraft
from app.services.assistance import content, control_crypto

class ContentTests(unittest.TestCase):
    def setUp(self):
        fixtures.AssistanceTests.setUp(self)
        self.keys = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'ASSISTANCE_CONTENT_ENABLED':'1',
            'ASSISTANCE_CONTROL_KEY_DIR':self.keys.name})
        self.env.start();control_crypto.initialize()
        self.app.include_router(assistance_content.router, prefix='/assistance/content')
        self.body={'platform':'meta','brief':'Promocionar servicio confirmado','text':'Contenido privado para revisión'}
    def tearDown(self):
        self.env.stop();self.keys.cleanup();fixtures.AssistanceTests.tearDown(self)
    def draft(self):
        r=self.client.post('/assistance/content/drafts',json=self.body)
        self.assertEqual(r.status_code,201,r.text);return r.json()
    def test_review_export_and_edit_invalidates_review(self):
        d=self.draft();url='/assistance/content/drafts/'+d['id']
        self.assertEqual(self.client.get(url+'/export').status_code,409)
        body={'revision':d['revision'],'digest':d['digest'],'accuracy_rights_privacy_checked':True}
        r=self.client.post(url+'/review',json=body);self.assertEqual(r.status_code,200,r.text)
        self.assertFalse(self.client.get(url+'/export').json()['publication_enabled'])
        self.assertEqual(self.client.post(url+'/review',json=body).status_code,409)
        r=self.client.put(url,json={**self.body,'revision':2,'text':'Contenido cambiado'})
        self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['status'],'draft')
        self.assertEqual(self.client.get(url+'/export').status_code,409)
        self.assertEqual(self.client.put(url,json={**self.body,'revision':2}).status_code,409)
    def test_isolation_encryption_and_no_publication_route(self):
        d=self.draft();url='/assistance/content/drafts/'+d['id']
        self.assertNotIn(self.body['text'],self.db.get(ContentDraft,d['id']).content)
        for uid in ['2','3']:
            self.client.headers['X-Test-User']=uid
            self.assertEqual(self.client.get(url).status_code,404)
        self.client.headers['X-Test-User']='1'
        self.assertEqual(self.client.post(url+'/publish').status_code,404)
    def test_invalid_review_and_disabled_feature(self):
        d=self.draft();url='/assistance/content/drafts/'+d['id']+'/review'
        body={'revision':1,'digest':'0'*64,'accuracy_rights_privacy_checked':True}
        self.assertEqual(self.client.post(url,json=body).status_code,409)
        self.assertEqual(self.client.post(url,json={**body,'digest':d['digest'],'accuracy_rights_privacy_checked':False}).status_code,422)
        with patch.dict(os.environ,{'ASSISTANCE_CONTENT_ENABLED':'0'}):
            self.assertEqual(self.client.get('/assistance/content/drafts/'+d['id']).status_code,503)
    def test_generation_persists_unreviewed_provenance_and_requires_authentication(self):
        with patch('app.services.assistance.content.generate', new=unittest.mock.AsyncMock(return_value=('Borrador simulado', {'provider':'test_fixture','model':'fixture'}))):
            r=self.client.post('/assistance/content/generate',json={'platform':'youtube','brief':'Guion confirmado','model':'fixture','share_with_local_model':True})
        self.assertEqual(r.status_code,201,r.text)
        self.assertEqual(r.json()['status'],'draft');self.assertEqual(r.json()['source']['provider'],'test_fixture')
        self.assertEqual(self.client.get('/assistance/content/drafts').json()['drafts'][0]['id'],r.json()['id'])
        self.client.headers.pop('X-Test-User',None)
        self.assertEqual(self.client.post('/assistance/content/drafts',json=self.body).status_code,401)

    def test_failed_generation_does_not_create_draft(self):
        with patch.dict(os.environ,{'ASSISTANCE_CONTENT_OLLAMA_ENABLED':'0'}):
            r=self.client.post('/assistance/content/generate',json={'platform':'meta','brief':'Crear anuncio','model':'test','share_with_local_model':True})
        self.assertEqual(r.status_code,503);self.assertEqual(self.db.query(ContentDraft).count(),0)

class OllamaTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'ASSISTANCE_CONTENT_OLLAMA_ENABLED':'1',
            'ASSISTANCE_CONTENT_OLLAMA_MODELS':'test-local','ASSISTANCE_CONTENT_OLLAMA_URL':'http://127.0.0.1:11434'})
        self.env.start()
    def tearDown(self):self.env.stop()
    def run_model(self,handler,consent=True):
        return asyncio.run(content.generate('Oferta api_key=secret-value','test-local',consent,httpx.MockTransport(handler)))
    def test_valid_response_redacts_credentials_and_disables_tools(self):
        def handler(request):
            body=json.loads(request.content)
            self.assertNotIn('secret-value',request.content.decode());self.assertNotIn('tools',body)
            self.assertFalse(body['stream']);self.assertEqual(body['options']['num_predict'],768)
            return httpx.Response(200,json={'model':'test-local','done':True,'message':{'content':'Guion pendiente de verificar'}})
        text,source=self.run_model(handler)
        self.assertEqual(text,'Guion pendiente de verificar');self.assertFalse(source['quality_verified'])
    def test_consent_and_model_allowlist(self):
        with self.assertRaises(HTTPException) as caught:self.run_model(lambda r:None,False)
        self.assertEqual(caught.exception.status_code,422)
        with patch.dict(os.environ,{'ASSISTANCE_CONTENT_OLLAMA_MODELS':'other'}):
            with self.assertRaises(HTTPException):self.run_model(lambda r:None)
    def test_origin_rejection(self):
        for origin in ['https://example.com','http://localhost@evil.test','http://127.0.0.1/path','http://127.0.0.1:bad','http://[malformed']:
            with self.subTest(origin=origin),patch.dict(os.environ,{'ASSISTANCE_CONTENT_OLLAMA_URL':origin}):
                with self.assertRaises(HTTPException) as caught:self.run_model(lambda r:None)
                self.assertEqual(caught.exception.status_code,503)
    def test_unavailable_invalid_redirect_and_oversized(self):
        responses=[httpx.Response(503,text='private traceback'),httpx.Response(302,headers={'location':'https://evil.test'}),
            httpx.Response(200,text='not json'),httpx.Response(200,content=b'x'*131073),
            httpx.Response(200,json={'model':'test-local','done':False,'message':{'content':'partial'}}),
            httpx.Response(200,json={'model':'test-local','done':True,'message':{'content':'hello','tool_calls':[{}]}})]
        for response in responses:
            with self.subTest(status=response.status_code),self.assertRaises(HTTPException) as caught:
                self.run_model(lambda request:response)
            self.assertEqual(caught.exception.status_code,502)
            self.assertNotIn('traceback',caught.exception.detail)
