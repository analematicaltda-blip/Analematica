"""Real authenticated route/database tests; no external providers or SOC services."""
import json
import os
import base64
import tempfile
import unittest
from unittest.mock import patch
import test_assistance as fixtures
from app.models.user import Usuario,RolesEnum
from app.services.assistance import control_crypto
from cryptography.hazmat.primitives.serialization import load_pem_public_key

class ResourcesTests(fixtures.AssistanceTests):
    def setUp(self):
        super().setUp();self.private=tempfile.TemporaryDirectory();self.keyenv=patch.dict(os.environ,{'ASSISTANCE_CONTROL_KEY_DIR':self.private.name});self.keyenv.start();control_crypto.initialize()
        from app.core.rate_limiter import limiter
        limiter._requests.clear()
    def tearDown(self):
        self.keyenv.stop();self.private.cleanup();super().tearDown()
    def resource(self,path):return self.client.get('/assistance/resources'+path)
    def record(self,purpose='Private content must never be exported'):
        pair=self.client.post('/assistance/control/pairings',json={'platforms':['meta']}).json()
        device=self.client.post('/assistance/control/claim',json={'pairing_code':pair['pairing_code'],'name':'Private device name','kind':'desktop'}).json()
        response=self.client.post('/assistance/control/jobs',json={'device_id':device['device_id'],'platform':'meta','operation':'browser_fill','arguments':{'ref':'e0','observation_id':'a'*32,'text':'Secret business message'},'purpose':purpose});self.assertEqual(response.status_code,201,response.text);job=response.json()
        result=self.client.post('/assistance/control/jobs/'+job['id']+'/authorize',json={'stage':1,'digest':job['digest'],'confirmation':job['confirmation_phrase']});self.assertEqual(result.status_code,200,result.text)
        return job
    def test_admin_catalog_is_offline_and_unverified(self):
        response=self.resource('/providers');self.assertEqual(response.status_code,200);data=response.json();self.assertEqual(data['total'],102);self.assertEqual(len(data['categories']),15);self.assertEqual(response.headers['cache-control'],'no-store')
        for item in data['entries']:
            self.assertFalse(item['provider_enabled']);self.assertFalse(item['terms_verified']);self.assertFalse(item['zero_cost_guaranteed']);self.assertIsNone(item['quota_verified_at'])
    def test_filters_keep_categories_separate_and_never_enable_providers(self):
        video=self.resource('/providers?category=video').json();self.assertGreater(video['count'],0);self.assertTrue(all(p['category']=='video' for p in video['entries']))
        local=self.resource('/providers?local_only=true').json();self.assertTrue(all(p['local_option'] for p in local['entries']));self.assertTrue(any(p['name']=='Ollama' for p in local['entries']))
        search=self.resource('/providers?q=replicate').json();self.assertGreater(search['count'],0);self.assertTrue(all('replicate' in (p['name']+' '+p['description']+' '+p['category_label']).lower() for p in search['entries']))
        self.assertEqual(self.resource('/providers?category=shell').status_code,422)
    def test_anonymous_and_nonstaff_cannot_access_any_resource(self):
        self.client.headers.clear()
        for path in ['/providers','/security/status','/security/control-audit-export']:self.assertEqual(self.resource(path).status_code,401)
        self.client.headers['X-Test-User']='1';self.db.get(Usuario,1).rol=RolesEnum.alumno;self.db.commit()
        for path in ['/providers','/security/status','/security/control-audit-export']:self.assertEqual(self.resource(path).status_code,403)
    def test_export_omits_message_device_name_and_plan_arguments(self):
        self.record();response=self.resource('/security/control-audit-export');self.assertEqual(response.status_code,200,response.text);bundle=response.json();payload=json.loads(bundle['payload']);self.assertEqual(payload['transport'],'manual_not_sent');self.assertEqual(len(payload['ingest_batch']['events']),1)
        for private in ['Secret business message','Private device name','Private content','observation_id','confirmation_phrase']:self.assertNotIn(private,json.dumps(bundle))
        event=payload['ingest_batch']['events'][0];self.assertEqual(event['severity'],'info');self.assertFalse(event['is_security_finding']);self.assertFalse(event['is_synthetic']);self.assertEqual(event['authorization_stage'],1)
    def test_signature_verifies_and_detects_modified_payload(self):
        self.record();first=self.resource('/security/control-audit-export').json();second=self.resource('/security/control-audit-export').json();self.assertEqual(first,second)
        public=load_pem_public_key(control_crypto.public_key().encode());signature=base64.b64decode(first['signature']);public.verify(signature,first['payload'].encode())
        from cryptography.exceptions import InvalidSignature
        with self.assertRaises(InvalidSignature):public.verify(signature,(first['payload']+' ').encode())
    def test_offline_extractor_requires_separately_trusted_key_and_expected_tenant(self):
        import importlib.util
        from pathlib import Path
        spec=importlib.util.spec_from_file_location('audit_bundle',Path(__file__).resolve().parents[3] / 'BACKEND/INTEGRACIONES/seguridad-ia/audit_bundle.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.record();bundle=self.resource('/security/control-audit-export').json();key=control_crypto.public_key().encode()
        self.assertEqual(len(module.extract(bundle,key,1)['events']),1)
        with self.assertRaises(ValueError):module.extract(bundle,key,2)
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        wrong=Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)
        from cryptography.exceptions import InvalidSignature
        bundle['public_key']=wrong.decode()
        with self.assertRaises(InvalidSignature):module.extract(bundle,wrong,1)
        # Embedded untrusted key does not override the independently pinned server key.
        self.assertEqual(len(module.extract(bundle,key,1)['events']),1)
    def test_export_never_crosses_requester_or_tenant(self):
        self.record()
        for user in ['2','3']:
            self.client.headers['X-Test-User']=user;result=self.resource('/security/control-audit-export?tenant_id=1&user_id=1');self.assertEqual(result.status_code,200);payload=json.loads(result.json()['payload']);self.assertEqual(payload['ingest_batch']['events'],[]);self.assertEqual(payload['source_user_id'],int(user))
    def test_export_pagination_is_bounded_and_stable(self):
        self.record();self.record('Another private purpose');one=json.loads(self.resource('/security/control-audit-export?limit=1').json()['payload']);self.assertTrue(one['has_more']);two=json.loads(self.resource('/security/control-audit-export?limit=1&after_id='+str(one['next_after_id'])).json()['payload']);self.assertFalse(two['has_more']);self.assertNotEqual(one['ingest_batch']['events'][0]['id'],two['ingest_batch']['events'][0]['id'])
        self.assertEqual(self.resource('/security/control-audit-export?limit=101').status_code,422);self.assertEqual(self.resource('/security/control-audit-export?after_id=-1').status_code,422)
    def test_status_is_honest_and_there_is_no_activation_route(self):
        data=self.resource('/security/status').json();self.assertEqual(data['deployment'],'not_verified');self.assertFalse(data['outbound_requests']);self.assertFalse(data['automatic_response_enabled']);self.assertIn('authentication_denials',data['not_covered'])
        self.assertEqual(self.client.post('/assistance/resources/providers',json={'token':'synthetic-not-a-key'}).status_code,405)

for name in vars(fixtures.AssistanceTests):
    if name.startswith('test_') and name not in vars(ResourcesTests):setattr(ResourcesTests,name,None)
if __name__=='__main__':unittest.main()
