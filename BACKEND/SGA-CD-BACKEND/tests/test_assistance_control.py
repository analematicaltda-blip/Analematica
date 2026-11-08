"""Isolated control protocol tests: never connect to provider accounts or devices."""
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import test_assistance as fixtures
from app.models.assistance import ControlJob,ControlApproval,ControlPairing
from app.services.assistance import control,control_crypto

class ControlTests(fixtures.AssistanceTests):
    # Reuse only setup/teardown, not the guidance test methods.
    def setUp(self):
        super().setUp();from app.core.rate_limiter import limiter
        limiter._requests.clear();self.keys=tempfile.TemporaryDirectory();self.keyenv=patch.dict(os.environ,{'ASSISTANCE_CONTROL_KEY_DIR':self.keys.name});self.keyenv.start();control_crypto.initialize()
    def tearDown(self):
        self.keyenv.stop();self.keys.cleanup();super().tearDown()
    def call(self,route,body=None):return self.client.post('/assistance/control'+route,json=body or {})
    def device(self,kind='desktop',platforms=None):
        response=self.call('/pairings',{'platforms':platforms or ['meta','gmail']});self.assertEqual(response.status_code,201,response.text)
        code=response.json()['pairing_code'];response=self.call('/claim',{'pairing_code':code,'name':'isolated-test','kind':kind});self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(self.call('/claim',{'pairing_code':code,'name':'replay'}).status_code,401)
        return response.json()
    def job(self,device,operation='browser_snapshot',arguments=None):
        response=self.call('/jobs',{'device_id':device['device_id'],'platform':'meta','operation':operation,'arguments':arguments or {},'purpose':'Prueba aislada del protocolo'})
        self.assertEqual(response.status_code,201,response.text);return response.json()
    def approval(self,job):
        response=self.call('/jobs/'+job['id']+'/authorize',{'stage':job['authorizations']+1,'digest':job['digest'],'confirmation':job['confirmation_phrase']});self.assertEqual(response.status_code,200,response.text);return response.json()
    def begin(self,device,job):return self.client.post('/assistance/control/device/jobs/'+job['id']+'/begin',headers={'Authorization':'Bearer '+device['device_token']})
    def test_two_separate_approvals_and_one_use_signed_grant(self):
        d=self.device();j=self.job(d);self.assertEqual(self.begin(d,j).status_code,409)
        first=self.approval(j);self.assertEqual(self.begin(d,j).status_code,409)
        self.assertEqual(self.call('/jobs/'+j['id']+'/authorize',{'stage':1,'digest':j['digest'],'confirmation':j['confirmation_phrase']}).status_code,409)
        ready=self.approval(first);self.assertEqual(ready['status'],'approved')
        result=self.begin(d,j);self.assertEqual(result.status_code,200,result.text)
        grant=json.loads(result.json()['payload']);self.assertEqual([a['stage'] for a in grant['approvals']],[1,2]);self.assertEqual({a['user_id'] for a in grant['approvals']},{1})
        self.assertEqual(self.begin(d,j).status_code,409)
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        import base64
        load_pem_public_key(d['server_public_key'].encode()).verify(base64.b64decode(result.json()['signature']),result.json()['payload'].encode())
        self.assertNotIn('Prueba aislada',self.db.get(ControlJob,j['id']).intent)
    def test_mutations_require_third_impact_confirmation(self):
        d=self.device();j=self.job(d,'browser_click',{'ref':'e0','observation_id':'a'*32})
        j=self.approval(self.approval(j));self.assertEqual(j['status'],'awaiting_impact');self.assertEqual(self.begin(d,j).status_code,409)
        j=self.approval(j);self.assertEqual(self.begin(d,j).status_code,200)
    def test_other_administrator_and_other_tenant_cannot_approve(self):
        d=self.device();j=self.job(d)
        for uid in ['2','3']:
            self.client.headers['X-Test-User']=uid
            self.assertEqual(self.call('/jobs/'+j['id']+'/authorize',{'stage':1,'digest':j['digest'],'confirmation':j['confirmation_phrase']}).status_code,404)
            self.assertEqual(self.client.get('/assistance/control/jobs/'+j['id']).status_code,404)
    def test_stop_and_revoke_prevent_dispatch(self):
        d=self.device();j=self.approval(self.approval(self.job(d)));self.call('/jobs/'+j['id']+'/stop');self.assertEqual(self.begin(d,j).status_code,409)
        j=self.approval(self.approval(self.job(d)));self.call('/devices/'+d['device_id']+'/revoke');self.assertEqual(self.begin(d,j).status_code,401)
    def test_expiry_digest_and_stage_are_enforced(self):
        d=self.device();j=self.job(d)
        self.assertEqual(self.call('/jobs/'+j['id']+'/authorize',{'stage':2,'digest':j['digest'],'confirmation':j['confirmation_phrase']}).status_code,409)
        self.assertEqual(self.call('/jobs/'+j['id']+'/authorize',{'stage':1,'digest':'0'*64,'confirmation':j['confirmation_phrase']}).status_code,409)
        with patch.object(control,'now',return_value=control.now()+1000):self.assertEqual(self.call('/jobs/'+j['id']+'/authorize',{'stage':1,'digest':j['digest'],'confirmation':j['confirmation_phrase']}).status_code,409)
    def test_native_apps_and_device_kind_are_scoped(self):
        for kind in ['android','ios']:
            d=self.device(kind);app=control.POLICY_DATA['native_apps'][kind]['meta'][0];j=self.job(d,'mobile_snapshot',{'app_id':app});self.assertEqual(j['intent']['target_kind'],kind)
            response=self.call('/jobs',{'device_id':d['device_id'],'platform':'meta','operation':'mobile_launch','arguments':{'app_id':'com.attacker.shell'},'purpose':'Prueba de alcance'});self.assertEqual(response.status_code,422)
            response=self.call('/jobs',{'device_id':d['device_id'],'platform':'meta','operation':'desktop_status','purpose':'Prueba de alcance'});self.assertEqual(response.status_code,422)
    def test_official_domain_and_pairing_scope_cannot_expand(self):
        d=self.device(platforms=['meta'])
        for url in ['https://facebook.com.evil.example/','https://facebook.com@evil.example','http://facebook.com','https://facebook.com/?access_token=secret']:
            r=self.call('/jobs',{'device_id':d['device_id'],'platform':'meta','operation':'browser_open','arguments':{'url':url},'purpose':'Prueba de dominio'});self.assertEqual(r.status_code,422,r.text)
        r=self.call('/jobs',{'device_id':d['device_id'],'platform':'gmail','operation':'browser_snapshot','purpose':'Prueba de alcance'});self.assertEqual(r.status_code,403)
    def test_device_token_cannot_authorize_and_result_is_not_provider_proof(self):
        d=self.device();j=self.job(d);self.client.headers.pop('X-Test-User')
        r=self.call('/jobs/'+j['id']+'/authorize',{'stage':1,'digest':j['digest'],'confirmation':j['confirmation_phrase']});self.assertEqual(r.status_code,401)
        self.client.headers['X-Test-User']='1';j=self.approval(self.approval(j));grant=json.loads(self.begin(d,j).json()['payload']);headers={'Authorization':'Bearer '+d['device_token']}
        url='/assistance/control/device/jobs/'+j['id']+'/result';r=self.client.post(url,headers=headers,json={'lease_id':grant['lease_id'],'outcome':'delivered','data':{'test':True}});self.assertEqual(r.status_code,200);self.assertFalse(r.json()['provider_success_verified'])
        self.assertEqual(self.client.post(url,headers=headers,json={'lease_id':grant['lease_id'],'outcome':'delivered'}).status_code,409)

    def test_checkpoint_rechecks_stop_expiry_and_never_extends_permission(self):
        d=self.device();j=self.approval(self.approval(self.job(d)));grant=json.loads(self.begin(d,j).json()['payload'])
        url='/assistance/control/device/jobs/'+j['id']+'/checkpoint';headers={'Authorization':'Bearer '+d['device_token']}
        response=self.client.post(url,headers=headers,json={'lease_id':grant['lease_id']});self.assertEqual(response.status_code,200,response.text);self.assertEqual(response.json()['lease_expires_at'],grant['expires_at']);self.assertFalse(response.json()['new_authorization'])
        self.assertEqual(self.client.post(url,headers=headers,json={'lease_id':'b'*48}).status_code,409)
        with patch.object(control,'now',return_value=grant['expires_at']):self.assertEqual(self.client.post(url,headers=headers,json={'lease_id':grant['lease_id']}).status_code,409)
        self.call('/jobs/'+j['id']+'/stop');self.assertEqual(self.client.post(url,headers=headers,json={'lease_id':grant['lease_id']}).status_code,409)
    def test_stale_device_object_cannot_dispatch_after_revocation(self):
        from app.models.assistance import ControlDevice
        from app.services.assistance.engine import Actor
        from fastapi import HTTPException
        from sqlalchemy import update
        d=self.device();j=self.approval(self.approval(self.job(d)));stale=self.db.get(ControlDevice,d['device_id'])
        self.db.execute(update(ControlDevice).where(ControlDevice.id==stale.id).values(revoked=1),execution_options={'synchronize_session':False});self.db.commit()
        with self.assertRaises(HTTPException) as error:control.begin(self.db,stale,j['id'])
        self.assertEqual(error.exception.status_code,409)
    def test_live_device_scope_changes_block_dispatch(self):
        from app.models.assistance import ControlDevice
        d=self.device();j=self.approval(self.approval(self.job(d)))
        row=self.db.get(ControlDevice,d['device_id']);row.scopes='["gmail"]';self.db.commit()
        self.assertEqual(self.begin(d,j).status_code,409)
    def test_plan_bindings_are_checked_even_if_storage_digest_was_changed(self):
        d=self.device();j=self.approval(self.approval(self.job(d)));row=self.db.get(ControlJob,j['id'])
        intent=json.loads(control_crypto.decrypt(row.intent));intent['job_id']='other-job';text=control.canonical(intent);row.intent=control_crypto.encrypt(text);row.digest=control.digest(text)
        for approval in self.db.query(ControlApproval).filter_by(job_id=row.id):approval.digest=row.digest
        self.db.commit();self.assertEqual(self.begin(d,j).status_code,409)
    def test_exact_expiry_rejects_review_and_execution(self):
        d=self.device();j=self.job(d)
        with patch.object(control,'now',return_value=j['expires_at']):
            response=self.call('/jobs/'+j['id']+'/authorize',{'stage':1,'digest':j['digest'],'confirmation':j['confirmation_phrase']});self.assertEqual(response.status_code,409)
        j=self.approval(self.approval(self.job(d)))
        with patch.object(control,'now',return_value=j['expires_at']):self.assertEqual(self.begin(d,j).status_code,409)
    def test_role_revocation_is_rechecked_at_service_boundary(self):
        from app.models.user import Usuario,RolesEnum
        from app.models.assistance import ControlDevice
        from fastapi import HTTPException
        d=self.device();j=self.approval(self.approval(self.job(d)));device=self.db.get(ControlDevice,d['device_id'])
        from sqlalchemy import update
        self.db.get(Usuario,1)  # Keep an old object in the session identity map.
        self.db.execute(update(Usuario).where(Usuario.id==1).values(rol=RolesEnum.alumno),execution_options={'synchronize_session':False});self.db.commit()
        with self.assertRaises(HTTPException) as error:control.begin(self.db,device,j['id'])
        self.assertEqual(error.exception.status_code,403)

    def test_old_policy_has_no_approval_phrase_and_is_not_queued(self):
        d=self.device();j=self.approval(self.approval(self.job(d)));row=self.db.get(ControlJob,j['id'])
        intent=json.loads(control_crypto.decrypt(row.intent));intent['policy']='sgacd-control-v1';row.intent=control_crypto.encrypt(control.canonical(intent));self.db.commit()
        response=self.client.get('/assistance/control/jobs/'+j['id']);self.assertEqual(response.status_code,200);self.assertFalse(response.json()['policy_current']);self.assertIsNone(response.json()['confirmation_phrase'])
        queue=self.client.get('/assistance/control/device/queue',headers={'Authorization':'Bearer '+d['device_token']});self.assertEqual(queue.status_code,200);self.assertEqual(queue.json()['jobs'],[])
        self.assertEqual(self.begin(d,j).status_code,409)

# Avoid executing inherited guide cases a second time in this class.
for name in list(vars(fixtures.AssistanceTests)):
    if name.startswith('test_') and name not in vars(ControlTests):setattr(ControlTests,name,None)
if __name__=='__main__':unittest.main()
