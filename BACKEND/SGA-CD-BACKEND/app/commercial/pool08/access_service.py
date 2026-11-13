"""Company-scoped controls: permission grants never rename roles or grant wallet rights."""
from uuid import uuid4
from .access_protocol import (AccessFault, NON_DELEGABLE, CHANNELS, PURPOSES, SYSTEMS,
    canonical, digest, evidence, expiry, fields, identifier, now, person, reference, revision, seal, utc, verify)

class AccessService:
    def __init__(self,store,principal,subject,team,grantor_valid,system,capability_ids):
        self.store=store;self.principal=principal;self.subject=subject;self.team=team
        self.grantor_valid=grantor_valid;self.system=system;self.ids=set(capability_ids)
        self.tenant=principal['tenant_ref'];self.actor=principal['actor_ref']
    def manager(self):
        if not self.principal['is_manager']:raise AccessFault('LOCAL_ADMINISTRATOR_REQUIRED',403)
    def installed(self):
        if not self.store.ready():raise AccessFault('ACCESS_SCHEMA_INSTALL_REQUIRED',503)
    def session(self):
        p=self.principal;allowed=set(p['capability_floor']);state='LOCAL_AUTHORITY';current=None
        if not p['is_manager']:
            row=verify(self.store.get('grant',self.tenant,subject_ref=self.actor))
            if row:
                current={'id':row['id'],'revision':row['revision'],'digest':row['digest']}
                if row['revoked_at'] is not None:allowed=set();state='REVOKED'
                elif utc(row['expires_at'])<=now():allowed=set();state='EXPIRED'
                elif row['role_fingerprint']!=p['role_fingerprint'] or not self.grantor_valid(row['granted_by_ref']):allowed=set();state='LOCAL_ROLE_REVIEW_REQUIRED'
                else:allowed &= set(row['capabilities']);state='EXPLICIT_SCOPED_GRANT'
            elif not p['legacy_permissions_authoritative']:allowed=set();state='EXPLICIT_GRANT_REQUIRED'
            allowed -= NON_DELEGABLE
        return {'system':self.system,'context':{'tenant_ref':self.tenant,'actor_ref':self.actor},
            'identity_namespace':p['identity_namespace'],'local_roles':p['local_roles'],
            'local_role_fingerprint':p['role_fingerprint'],'local_role_scope':p['local_role_scope'],
            'capability_permissions':{key:key in allowed for key in sorted(self.ids)},
            'can_manage_commercial_access':p['is_manager'],'registry_ready':self.store.ready(),
            'grant_state':state,'grant_receipt':current,'roles_preserved':True,
            'common_role_assignment_supported':False,'cross_system_access_granted':False,
            'wallet_permissions_granted':False,'personal_wallet_eligibility':'REGISTERED_PERSON',
            'company_name':p['company_name'],'policy_scope':'LOCAL_ROLES_AND_EXPLICIT_COMPANY_CAPABILITIES'}
    def authorize_plan(self,body):
        allowed={key for key,value in self.session()['capability_permissions'].items() if value}
        if isinstance(body,dict) and isinstance(body.get('task_graph'),list):
            for node in body['task_graph']:
                if isinstance(node,dict) and isinstance(node.get('capability'),str) and node['capability'] in self.ids and node['capability'] not in allowed:
                    raise AccessFault('CAPABILITY_NOT_GRANTED',403)
    def _event(self,request_id,operation,body,action):
        self.manager();self.installed();key=identifier(request_id)
        signature=digest({'system':self.system,'tenant_ref':self.tenant,'actor_ref':self.actor,'operation':operation,'body':body})
        with self.store.transaction():
            lock=getattr(self,'transaction_lock',None)
            if lock:lock()
            if not self.grantor_valid(self.actor):raise AccessFault('LOCAL_ADMINISTRATOR_REQUIRED',403)
            old=verify(self.store.get_by_id('event',key))
            if old:
                if old['tenant_ref']!=self.tenant or old['actor_ref']!=self.actor or old['operation']!=operation or old['request_digest']!=signature:raise AccessFault('REQUEST_CONFLICT',409)
                return {**old['result'],'replayed':True,'previous_receipt_only':True,'execution_authorized':False}
            result=action()
            timestamp=now();row=seal({'id':key,'tenant_ref':self.tenant,'revision':1,'created_at':timestamp,'updated_at':timestamp,'actor_ref':self.actor,'operation':operation,'request_digest':signature,'result':result})
            self.store.save('event',row,0)
            return {**result,'replayed':False,'execution_authorized':False}
    def _base(self,old):
        timestamp=now()
        return {'id':old['id'] if old else str(uuid4()),'tenant_ref':self.tenant,'revision':old['revision']+1 if old else 1,'created_at':old['created_at'] if old else timestamp,'updated_at':timestamp}
    def _expected(self,old,expected):
        if revision(expected)!=(old['revision'] if old else 0):raise AccessFault('REVISION_CONFLICT',409)
    def team_view(self):
        self.manager();members,truncated=self.team();result=[]
        for member in members:
            row=verify(self.store.get('grant',self.tenant,subject_ref=member['actor_ref']))
            result.append({**member,'grant':self.grant_view(row) if row else None})
        return {'system':self.system,'members':result,'truncated':truncated,'roles_can_be_changed_here':False,'wallet_permissions_granted':False}
    def grant_view(self,row):
        state='REVOKED' if row['revoked_at'] else 'EXPIRED' if utc(row['expires_at'])<=now() else 'RECORDED'
        return {'id':row['id'],'subject_ref':row['subject_ref'],'revision':row['revision'],'digest':row['digest'],'capabilities':row['capabilities'],'role_fingerprint':row['role_fingerprint'],'expires_at':utc(row['expires_at']).isoformat(),'state':state}
    def grant(self,member_ref,body):
        fields(body,['request_id','capabilities','role_fingerprint','expected_revision','expires_at','evidence_digest'])
        member_ref=person(member_ref);self.manager();target=self.subject(member_ref)
        if target['is_manager'] or member_ref==self.actor:raise AccessFault('LOCAL_ADMINISTRATOR_ROLE_IS_NOT_DELEGABLE',403)
        capabilities=body['capabilities']
        if not isinstance(capabilities,list) or not 1<=len(capabilities)<=len(self.ids) or any(not isinstance(x,str) for x in capabilities) or len(set(capabilities))!=len(capabilities) or not set(capabilities)<=self.ids-NON_DELEGABLE:raise AccessFault('INVALID_OR_NONDELEGABLE_CAPABILITY')
        if not set(capabilities)<=set(target['capability_floor']):raise AccessFault('EXCEEDS_EXISTING_LOCAL_PERMISSIONS',403)
        if body['role_fingerprint']!=target['role_fingerprint']:raise AccessFault('LOCAL_ROLE_CHANGED',409)
        expires=expiry(body['expires_at']);evidence(body['evidence_digest'])
        def action():
            # Fresh role/account relationship immediately before the atomic grant.
            fresh=self.subject(member_ref)
            if fresh['role_fingerprint']!=target['role_fingerprint']:raise AccessFault('LOCAL_ROLE_CHANGED',409)
            old=verify(self.store.get('grant',self.tenant,subject_ref=member_ref));self._expected(old,body['expected_revision'])
            row=seal({**self._base(old),'subject_ref':member_ref,'role_fingerprint':fresh['role_fingerprint'],'capabilities':sorted(capabilities),'granted_by_ref':self.actor,'expires_at':expires,'revoked_at':None})
            self.store.save('grant',row,old['revision'] if old else 0)
            return {'kind':'CAPABILITY_GRANT','evidence_digest':body['evidence_digest'],'grant':self.grant_view(row),'local_roles_changed':False,'wallet_permissions_granted':False}
        return self._event(body['request_id'],'CAPABILITY_GRANT',{'member_ref':member_ref,**body},action)
    def revoke_grant(self,member_ref,body):
        fields(body,['request_id','expected_revision']);member_ref=person(member_ref)
        def action():
            old=verify(self.store.get('grant',self.tenant,subject_ref=member_ref))
            if old is None:raise AccessFault('GRANT_NOT_FOUND',404)
            self._expected(old,body['expected_revision']);row=seal({**old,**self._base(old),'capabilities':[],'revoked_at':now()})
            self.store.save('grant',row,old['revision'])
            return {'kind':'CAPABILITY_REVOKED','grant':self.grant_view(row),'wallet_permissions_granted':False}
        return self._event(body['request_id'],'CAPABILITY_REVOKE',{'member_ref':member_ref,**body},action)
    def record_consent(self,body,source_check=None):
        fields(body,['request_id','customer_ref','channel','purpose','expires_at','expected_revision','evidence_digest']+(['source_contact_revision'] if source_check else []))
        customer=reference(body['customer_ref'])
        if not isinstance(body['channel'],str) or not isinstance(body['purpose'],str) or body['channel'] not in CHANNELS or body['purpose'] not in PURPOSES:raise AccessFault('INVALID_CONSENT_SCOPE')
        expires=expiry(body['expires_at']);evidence(body['evidence_digest'])
        def action():
            source=source_check(body) if source_check else {'bound_to_crm':False}
            old=verify(self.store.get('consent',self.tenant,customer_ref=customer,channel=body['channel'],purpose=body['purpose']));self._expected(old,body['expected_revision'])
            row=seal({**self._base(old),'customer_ref':customer,'channel':body['channel'],'purpose':body['purpose'],'expires_at':expires,'evidence_digest':body['evidence_digest'],'recorded_by_ref':self.actor,'revoked_at':None})
            self.store.save('consent',row,old['revision'] if old else 0)
            return {'kind':'CONSENT_RECORDED','source':source,'consent':self.consent_view(row),'authenticity_of_evidence_verified':False,'delivery_authorized':False}
        return self._event(body['request_id'],'CONSENT_RECORD',body,action)
    def consent_view(self,row):
        return {'id':row['id'],'customer_ref':row['customer_ref'],'channel':row['channel'],'purpose':row['purpose'],'revision':row['revision'],'digest':row['digest'],'state':'REVOKED' if row['revoked_at'] else 'EXPIRED' if utc(row['expires_at'])<=now() else 'RECORDED','expires_at':utc(row['expires_at']).isoformat(),'evidence_digest':row['evidence_digest']}
    def consent_status(self,body):
        fields(body,['customer_ref','channel','purpose']);self.installed()
        if not any(self.session()['capability_permissions'].values()):raise AccessFault('CONSENT_LOOKUP_NOT_ALLOWED',403)
        customer=reference(body['customer_ref'])
        if not isinstance(body['channel'],str) or not isinstance(body['purpose'],str) or body['channel'] not in CHANNELS or body['purpose'] not in PURPOSES:raise AccessFault('INVALID_CONSENT_SCOPE')
        row=verify(self.store.get('consent',self.tenant,customer_ref=customer,channel=body['channel'],purpose=body['purpose']))
        return {'consent':self.consent_view(row) if row else None,'local_record_current':bool(row and not row['revoked_at'] and utc(row['expires_at'])>now()),'delivery_authorized':False,'cross_system_consent_assumed':False}
    def revoke_consent(self,record_id,body,source_revoke=None):
        fields(body,['request_id','expected_revision']);record_id=identifier(record_id)
        def action():
            old=verify(self.store.get('consent',self.tenant,id=record_id))
            if old is None:raise AccessFault('CONSENT_NOT_FOUND',404)
            self._expected(old,body['expected_revision'])
            source=source_revoke(old,body['request_id']) if source_revoke else {'state':'NOT_REQUESTED'}
            row=seal({**old,**self._base(old),'revoked_at':now()})
            self.store.save('consent',row,old['revision'])
            return {'kind':'CONSENT_REVOKED','crm_revocation':source,'consent':self.consent_view(row),'delivery_authorized':False}
        return self._event(body['request_id'],'CONSENT_REVOKE',{'record_id':record_id,**body},action)
    def alias(self,body):
        fields(body,['request_id','local_actor_ref','external_system','external_tenant_ref','external_actor_ref','expires_at','expected_revision','evidence_digest'])
        self.manager();local=person(body['local_actor_ref']);self.subject(local)
        if not isinstance(body['external_system'],str) or body['external_system'] not in SYSTEMS-{self.system}:raise AccessFault('EXPLICIT_DISTINCT_REALM_REQUIRED')
        external_tenant=reference(body['external_tenant_ref']);external_actor=reference(body['external_actor_ref']);expires=expiry(body['expires_at']);evidence(body['evidence_digest'])
        def action():
            self.subject(local)
            old=verify(self.store.get('alias',self.tenant,local_actor_ref=local,external_system=body['external_system'],external_tenant_ref=external_tenant,external_actor_ref=external_actor));self._expected(old,body['expected_revision'])
            row=seal({**self._base(old),'local_actor_ref':local,'external_system':body['external_system'],'external_tenant_ref':external_tenant,'external_actor_ref':external_actor,'expires_at':expires,'evidence_digest':body['evidence_digest'],'recorded_by_ref':self.actor,'revoked_at':None})
            self.store.save('alias',row,old['revision'] if old else 0)
            return {'kind':'IDENTITY_REFERENCE_RECORDED','alias':self.alias_view(row),'cross_system_access_granted':False,'local_roles_changed':False}
        return self._event(body['request_id'],'IDENTITY_ALIAS',body,action)
    def alias_view(self,row):
        return {key:row[key] for key in ('id','local_actor_ref','external_system','external_tenant_ref','external_actor_ref','revision','digest')}|{'state':'REVOKED' if row['revoked_at'] else 'EXPIRED' if utc(row['expires_at'])<=now() else 'EXTERNAL_REVIEW_REQUIRED','remote_identity_verified':False,'cross_system_access_granted':False}
    def revoke_alias(self,record_id,body):
        fields(body,['request_id','expected_revision']);record_id=identifier(record_id)
        def action():
            old=verify(self.store.get('alias',self.tenant,id=record_id))
            if old is None:raise AccessFault('IDENTITY_REFERENCE_NOT_FOUND',404)
            self._expected(old,body['expected_revision']);row=seal({**old,**self._base(old),'revoked_at':now()});self.store.save('alias',row,old['revision'])
            return {'kind':'IDENTITY_REFERENCE_REVOKED','alias':self.alias_view(row),'cross_system_access_granted':False}
        return self._event(body['request_id'],'IDENTITY_ALIAS_REVOKE',{'record_id':record_id,**body},action)
    def records(self,kind):
        self.manager();self.installed();rows=self.store.list(kind,self.tenant,101)
        for row in rows:verify(row)
        presenter=self.consent_view if kind=='consent' else self.alias_view if kind=='alias' else lambda row:{key:row[key] for key in ('id','revision','digest','actor_ref','operation','result')}
        return {'items':[presenter(row) for row in rows[:100]],'truncated':len(rows)>100,'cross_system_access_granted':False}
