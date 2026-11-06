import os
os.environ.setdefault('SECRET_KEY','isolated-assistance-test-not-a-real-key')
os.environ.setdefault('DATABASE_URL','sqlite://')
import asyncio
import json
from pathlib import Path
import unittest
import uuid
from unittest.mock import patch
import httpx
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.models.user import Usuario, RolesEnum
from app.models.tenancy import Inquilino
from app.models.assistance import AssistanceSession, AssistanceEvent, AssistanceAdvice
from app.api import deps
from app.api.v1.endpoints import assistance as api
from app.services.assistance import engine, duet

class AssistanceTests(unittest.TestCase):
    def setUp(self):
        self.bind=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
        Base.metadata.create_all(self.bind)
        self.db=sessionmaker(bind=self.bind,expire_on_commit=False)()
        for number in [1,2]:self.db.add(Inquilino(id=number,nombre_empresa='Tenant '+str(number),activo=True))
        for number,tenant in [(1,1),(2,1),(3,2)]:self.db.add(Usuario(id=number,inquilino_id=tenant,nombre_usuario='test-'+str(number),password_hash='not-a-password-hash',rol=RolesEnum.admin_empresa,activo=True))
        self.db.commit()
        self.app=FastAPI();self.app.include_router(api.router,prefix='/assistance')
        def current(request:Request):
            number=request.headers.get('X-Test-User')
            if number is None:raise HTTPException(401,'not authenticated')
            return self.db.get(Usuario,int(number))
        self.app.dependency_overrides[deps.get_db]=lambda:self.db
        self.app.dependency_overrides[deps.get_current_active_user]=current
        self.client=TestClient(self.app);self.client.headers['X-Test-User']='1'
        self.env=patch.dict(os.environ,{'ASSISTANCE_DUET_ENABLED':'0','ASSISTANCE_DUET_USER_ID':'1','ASSISTANCE_DUET_TENANT_ID':'1'})
        self.env.start()
    def tearDown(self):
        self.env.stop();self.client.close();self.db.close();self.bind.dispose()
    def start(self,workflow='meta.campaign'):
        response=self.client.post('/assistance/sessions',json={'workflow_id':workflow});self.assertEqual(response.status_code,201,response.text);return response.json()
    def advance(self,state,**extra):
        return self.client.post('/assistance/sessions/'+state['id']+'/advance',json={'revision':state['revision'],'step_id':state['current_step']['id'],'checklist_checked':True,**extra})
    def test_catalog_requires_authentication(self):
        self.client.headers.clear();self.assertEqual(self.client.get('/assistance/catalog').status_code,401)
    def test_inactive_tenant_cannot_use_assistance(self):
        self.db.get(Inquilino,1).activo=False;self.db.commit();self.assertEqual(self.client.get('/assistance/catalog').status_code,403)
    def test_catalog_has_distinct_guides_and_real_official_origins(self):
        from urllib.parse import urlsplit
        catalog=self.client.get('/assistance/catalog').json();flows=catalog['workflows'];self.assertEqual(len(flows),42);self.assertEqual(len({g['id'] for g in flows}),42)
        allowed={'business.facebook.com','ads.tiktok.com','mail.google.com','studio.youtube.com','ads.google.com'}
        for flow in flows:
            self.assertEqual(len(flow['steps']),6);self.assertIn(urlsplit(flow['entry_url']).hostname,allowed)
            if flow['steps'][4]['risk']!='read':self.assertTrue(flow['steps'][4]['requires_confirmation'])
        self.assertEqual(catalog['mode'],'guidance_only')
    def test_sessions_are_private_even_between_users_in_same_tenant(self):
        state=self.start()
        for number in ['2','3']:
            self.client.headers['X-Test-User']=number
            self.assertEqual(self.client.get('/assistance/sessions/'+state['id']).status_code,404)
            self.assertEqual(self.client.get('/assistance/sessions').json(),{'sessions':[]})
            self.assertEqual(self.advance(state).status_code,404)
    def test_step_skip_and_replay_are_rejected(self):
        state=self.start();body={'revision':1,'step_id':'manual_action','checklist_checked':True,'confirmed':True}
        self.assertEqual(self.client.post('/assistance/sessions/'+state['id']+'/advance',json=body).status_code,409)
        response=self.advance(state);self.assertEqual(response.status_code,200)
        self.assertEqual(self.advance(state).status_code,409)
        self.assertEqual(self.db.query(AssistanceEvent).count(),1)
    def test_checklist_and_manual_confirmation_are_mandatory(self):
        state=self.start();self.assertEqual(self.advance(state,checklist_checked=False).status_code,422)
        for _ in range(4):state=self.advance(state).json()
        self.assertEqual(state['current_step']['id'],'manual_action')
        self.assertEqual(self.advance(state).status_code,409)
        state=self.advance(state,confirmed=True).json();state=self.advance(state).json()
        self.assertEqual(state['status'],'completed');self.assertFalse(state['external_execution']);self.assertEqual(state['verification'],'user_reported')
        self.assertEqual(self.db.query(AssistanceEvent).filter_by(event='manual_action_reported').count(),1)
    def test_guide_snapshot_is_stable_when_catalog_changes(self):
        state=self.start();original=engine._catalog();edited=json.loads(json.dumps(original));edited['workflows'][2]['steps'][0]['title']='Changed'
        with patch.object(engine,'_catalog',return_value=edited):
            current=self.client.get('/assistance/sessions/'+state['id']).json()
        self.assertEqual(current['current_step'],state['current_step'])
    def test_close_only_closes_guide_and_blocks_progress(self):
        state=self.start();response=self.client.post('/assistance/sessions/'+state['id']+'/close',json={'revision':1})
        self.assertEqual(response.json()['status'],'closed');self.assertEqual(self.advance(state).status_code,409)
        self.assertEqual(self.db.query(AssistanceEvent).one().event,'guide_closed_only')
    def test_unknown_workflows_and_unexpected_arguments_are_refused(self):
        self.assertEqual(self.client.post('/assistance/sessions',json={'workflow_id':'shell.exec'}).status_code,404)
        self.assertEqual(self.client.post('/assistance/sessions',json={'workflow_id':'meta.campaign','publish':True}).status_code,422)
    def test_no_ai_connection_is_needed_to_advance_guides(self):
        with patch.object(duet.DuetClient,'configured',side_effect=AssertionError('must not connect')):
            state=self.start('gmail.search');self.assertEqual(self.advance(state).status_code,200)
    def test_question_requires_explicit_sharing_and_configured_connection(self):
        state=self.start();url='/assistance/sessions/'+state['id']+'/advice';body={'request_id':str(uuid.uuid4()),'question':'¿Dónde reviso el presupuesto?'}
        self.assertEqual(self.client.post(url,json=body).status_code,409)
        self.assertEqual(self.client.post(url,json={**body,'share_with_open_duet':True}).status_code,503)
        self.assertEqual(self.db.query(AssistanceAdvice).count(),0)
    def test_personal_duet_cannot_be_shared_across_users(self):
        self.client.headers['X-Test-User']='2';state=self.start();response=self.client.post('/assistance/sessions/'+state['id']+'/advice',json={'request_id':str(uuid.uuid4()),'question':'Ayúdame con el paso actual','share_with_open_duet':True})
        self.assertEqual(response.status_code,403)
    def test_duet_contract_is_plan_only_redacted_and_idempotent(self):
        calls=[]
        def transport(request):
            calls.append((request.method,request.url.path,json.loads(request.content) if request.content else None))
            if request.url.path=='/api/v1/agents':
                payload=calls[-1][2];self.assertEqual(payload['approval_mode'],'plan');self.assertFalse(payload['make_lead']);self.assertFalse(payload['memory_enabled']);return httpx.Response(201,json={'id':11,'approval_mode':'plan','memory_enabled':False})
            if request.url.path=='/api/v1/threads':return httpx.Response(201,json={'id':22})
            if request.url.path.endswith('/turns'):
                self.assertNotIn('secret-example',calls[-1][2]['prompt_text']);return httpx.Response(202,json={'id':33})
            return httpx.Response(200,json={'turns':[{'id':33,'status':'succeeded','result':'Revisa el presupuesto antes de continuar.'}]})
        def client():return duet.DuetClient('http://127.0.0.1:8099','test-only-local-credential',transport=httpx.MockTransport(transport))
        state=self.start();url='/assistance/sessions/'+state['id']+'/advice';body={'request_id':str(uuid.uuid4()),'question':'Mi clave=secret-example; ¿dónde reviso el presupuesto?','share_with_open_duet':True}
        with patch.object(duet.DuetClient,'configured',side_effect=client):
            response=self.client.post(url,json=body);self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(self.client.post(url,json=body).json(),response.json());self.assertEqual(len(calls),3)
            result=self.client.get(url+'/'+body['request_id']);self.assertEqual(result.json()['status'],'succeeded');self.assertIn('Revisa',result.json()['answer'])
        self.assertEqual(self.db.query(AssistanceSession).one().position,0)
    def test_failed_or_uncertain_request_is_not_automatically_retried(self):
        calls=[]
        def transport(request):calls.append(request);raise httpx.ReadTimeout('test',request=request)
        factory=lambda:duet.DuetClient('http://localhost:8099','test-only-local-credential',transport=httpx.MockTransport(transport))
        state=self.start();url='/assistance/sessions/'+state['id']+'/advice';body={'request_id':str(uuid.uuid4()),'question':'Ayúdame con el presupuesto','share_with_open_duet':True}
        with patch.object(duet.DuetClient,'configured',side_effect=factory):
            self.assertEqual(self.client.post(url,json=body).status_code,502)
            self.assertEqual(self.client.post(url,json=body).json()['status'],'uncertain');self.assertEqual(len(calls),1)
    def test_unsafe_duet_origins_are_rejected_before_network(self):
        for origin in ['https://external.example','http://127.0.0.1@evil.example','http://localhost/a','http://localhost/?token=x']:
            with self.subTest(origin=origin),self.assertRaises(HTTPException):duet.DuetClient(origin,'test-only-local-credential')
    def test_duet_cannot_silently_raise_permissions(self):
        async def check():
            calls=[]
            def transport(request):
                calls.append(request)
                return httpx.Response(201,json={'id':1,'approval_mode':'ask','memory_enabled':True})
            client=duet.DuetClient('http://localhost:8099','test-only-local-credential',transport=httpx.MockTransport(transport))
            try:
                with self.assertRaises(HTTPException):await client.advise({'id':'test-session'},'Ayuda con este paso')
                self.assertEqual(len(calls),1)
            finally:await client.close()
        asyncio.run(check())
    def test_oversized_duet_response_is_rejected(self):
        async def check():
            client=duet.DuetClient('http://localhost:8099','test-only-local-credential',transport=httpx.MockTransport(lambda request:httpx.Response(200,content=b'x'*1_000_001)))
            try:
                with self.assertRaises(HTTPException) as failure:await client.request('GET','/threads/1')
                self.assertEqual(failure.exception.status_code,502)
            finally:await client.close()
        asyncio.run(check())
    def test_credentials_are_redacted(self):
        text=duet.redact('clave=secret-example Bearer abc123 eyJabc.abc.def api_key=private-value')
        for secret in ['secret-example','abc123','eyJabc.abc.def','private-value']:self.assertNotIn(secret,text)

if __name__=='__main__':unittest.main()
