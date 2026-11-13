"""Owned administration boundary. References do not authenticate remote identities."""
from .access_protocol import AccessFault, fields, identifier, verify, NON_DELEGABLE, CHANNELS, PURPOSES, SYSTEMS, revision, expiry, utc, now

class AccessAdmin:
    def __init__(self, access, crm=None):
        self.access=access
        self.crm=crm
        if crm is not None:access.transaction_lock=crm.store.lock
        access.manager()
        access.installed()
    def read(self, section, key=None):
        access=self.access
        if section=='context':
            return {**access.session(), 'capabilities':sorted(access.ids-NON_DELEGABLE),
                    'non_delegable':sorted(NON_DELEGABLE), 'channels':sorted(CHANNELS),
                    'purposes':sorted(PURPOSES), 'external_systems':sorted(SYSTEMS-{access.system}),
                    'consent_evidence_authenticity_verified':False,
                    'consent_records_are_declarations':True, 'delivery_authorized':False}
        if section=='team':return access.team_view()
        if section in ('consents','aliases','history'):
            return access.records({'consents':'consent','aliases':'alias','history':'event'}[section])
        if section=='receipts':
            row=verify(access.store.get_by_id('event',identifier(key)))
            if not row or row['tenant_ref']!=access.tenant or row['actor_ref']!=access.actor:
                raise AccessFault('RECEIPT_NOT_FOUND',404)
            return {'request_id':row['id'],'operation':row['operation'],'result':row['result'],
                    'previous_receipt_only':True,'execution_authorized':False}
        raise AccessFault('UNKNOWN_SECTION',404)
    def command(self, body):
        fields(body,['request_id','operation','subject_ref','data'])
        identifier(body['request_id'])
        if not isinstance(body['data'],dict):raise AccessFault('INVALID_FIELDS')
        if 'request_id' in body['data']:raise AccessFault('INVALID_FIELDS')
        data={**body['data'],'request_id':body['request_id']}
        op=body['operation']; subject=body['subject_ref']; a=self.access
        if not isinstance(op,str):raise AccessFault('INVALID_OPERATION')
        targets={'grant':a.grant,'revoke_grant':a.revoke_grant,'revoke_alias':a.revoke_alias}
        if op=='revoke_consent':return a.revoke_consent(subject,data,self.revoke_source)
        if op in targets:
            if not isinstance(subject,str):raise AccessFault('INVALID_REFERENCE')
            return targets[op](subject,data)
        if subject is not None:raise AccessFault('INVALID_FIELDS')
        if op=='record_consent':return a.record_consent(data,self.check_source)
        if op=='link_identity':return a.alias(data)
        raise AccessFault('INVALID_OPERATION')

    def check_source(self, body):
        if self.crm is None:raise AccessFault('CRM_SOURCE_REQUIRED',503)
        self.crm.store.lock()
        item=self.crm.get(body['customer_ref'])
        if item['revision']!=revision(body['source_contact_revision']):raise AccessFault('SOURCE_REVISION_CONFLICT',409)
        purpose={'SERVICE_FULFILMENT':'SERVICE','MARKETING':'MARKETING','CROSS_SYSTEM_ATTRIBUTION':'CROSS_SYSTEM_ATTRIBUTION'}.get(body['purpose'])
        consent=item['consents'].get(body['channel']+':'+str(purpose))
        if item['status']=='WITHDRAWN' or not consent or not consent['granted']:
            raise AccessFault('CURRENT_CRM_CONSENT_REQUIRED',409)
        from datetime import datetime
        until=utc(datetime.fromisoformat(consent['expires_at'].replace('Z','+00:00')))
        if until<=now() or expiry(body['expires_at'])>until or consent['evidence_digest']!=body['evidence_digest']:
            raise AccessFault('CRM_CONSENT_SOURCE_MISMATCH',409)
        return {'bound_to_crm':True,'contact_ref':item['id'],'contact_revision':item['revision'],
                'evidence_authenticity_verified':False,'delivery_authorized':False}

    def revoke_source(self, row, request_id):
        """Restrictive CRM revocation joins the caller's policy transaction and receipt.

        A cloned store suppresses only its nested commit; all validation, history,
        tenant locks and CAS remain those of CRM.command. The outer policy unit
        of work rolls both domains back if either event cannot be persisted.
        """
        from copy import copy
        from contextlib import contextmanager
        from .crm import CRMError
        if self.crm is None:raise AccessFault('CRM_SOURCE_REQUIRED',503)
        try:item=self.crm.get(row['customer_ref'])
        except CRMError as exc:
            if exc.status==404:return {'state':'NO_LOCAL_SOURCE','delivery_authorized':False}
            raise
        purpose={'SERVICE_FULFILMENT':'SERVICE','MARKETING':'MARKETING','CROSS_SYSTEM_ATTRIBUTION':'CROSS_SYSTEM_ATTRIBUTION'}[row['purpose']]
        consent=item['consents'].get(row['channel']+':'+purpose)
        if not consent or not consent['granted']:return {'state':'ALREADY_REVOKED','delivery_authorized':False}
        @contextmanager
        def join():yield
        crm=copy(self.crm);crm.store=copy(self.crm.store);crm.store.transaction=join
        receipt=crm.command({'request_id':request_id,'operation':'consent','contact_id':item['id'],
            'expected_revision':item['revision'],'data':{'channel':row['channel'],'purpose':purpose,
            'granted':False,'evidence_digest':consent['evidence_digest'],'expires_at':consent['expires_at']}})
        return {'state':'REVOKED_IN_CRM','contact_ref':item['id'],'contact_revision':receipt['revision'],
                'delivery_authorized':False}
