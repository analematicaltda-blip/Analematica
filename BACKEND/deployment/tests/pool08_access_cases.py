"""Shared test scenarios; applications retain their own implementations and ORMs."""
import uuid
from datetime import datetime,timedelta,timezone
from unittest.mock import patch

class AccessScenarios:
 def command(self,operation,subject=None,**data):
  return {'request_id':str(uuid.uuid4()),'operation':operation,'subject_ref':subject,'data':data}
 def due(self):return (datetime.now(timezone.utc)+timedelta(days=2)).isoformat()
 def grant_body(self,**changes):
  target=self.owner().subject(self.staff_ref)
  data=dict(capabilities=['crm.prospect.manage'],role_fingerprint=target['role_fingerprint'],expected_revision=0,expires_at=self.due(),evidence_digest='a'*64);data.update(changes)
  return self.command('grant',self.staff_ref,**data)
 def consent(self,channel='EMAIL',purpose='MARKETING'):
  crm=self.crm();cid=crm.command(dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=dict(name='Synthetic access verification',email=uuid.uuid4().hex+'@example.test',origin='TEST',responsible_ref=self.owner().actor)))['contact_id']
  crm.command(dict(request_id=str(uuid.uuid4()),operation='consent',contact_id=cid,expected_revision=1,data=dict(channel=channel,purpose='SERVICE' if purpose=='SERVICE_FULFILMENT' else purpose,granted=True,expires_at=self.due(),evidence_digest='a'*64)))
  body=self.command('record_consent',customer_ref=cid,source_contact_revision=2,channel=channel,purpose=purpose,expires_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),expected_revision=0,evidence_digest='a'*64)
  return cid,body,self.admin().command(body)
 def alias_body(self,**changes):
  data=dict(local_actor_ref=self.staff_ref,external_system=next(s for s in self.protocol.SYSTEMS if s!=self.owner().system),external_tenant_ref='company-external',external_actor_ref=self.staff_ref,expires_at=self.due(),expected_revision=0,evidence_digest='a'*64);data.update(changes)
  return self.command('link_identity',**data)
 def fault(self,code,action):
  with self.assertRaises(self.protocol.AccessFault) as caught:action()
  self.assertEqual(caught.exception.code,code)
 def test_grant_expiry_removes_current_permissions(self):
  self.admin().command(self.grant_body())
  self.assertTrue(self.staff().session()['capability_permissions']['crm.prospect.manage'])
  with patch.object(self.service_module,'now',return_value=datetime.now(timezone.utc)+timedelta(days=3)):
   session=self.staff().session();self.assertEqual(session['grant_state'],'EXPIRED');self.assertFalse(any(session['capability_permissions'].values()))
 def test_grant_role_change_invalidates_previous_fingerprint(self):
  self.admin().command(self.grant_body());self.change_staff_role()
  session=self.staff().session();self.assertFalse(any(session['capability_permissions'].values()))
 def test_inactive_staff_cannot_read_or_be_granted(self):
  self.admin().command(self.grant_body());self.disable_staff()
  with self.assertRaises(self.protocol.AccessFault):self.staff()
  with self.assertRaises(self.protocol.AccessFault):self.admin().command(self.grant_body())
 def test_owner_revocation_blocks_stale_admin_object_and_replay(self):
  admin=self.admin();body=self.grant_body();admin.command(body);self.disable_owner()
  with self.assertRaises(self.protocol.AccessFault):admin.command(body)
 def test_stale_role_fingerprint_rejected_without_event(self):
  body=self.grant_body(role_fingerprint='wrong');before=self.counts()
  self.fault('LOCAL_ROLE_CHANGED',lambda:self.admin().command(body));self.assertEqual(self.counts(),before)
 def test_competing_revision_has_one_winner(self):
  first=self.grant_body();second=self.grant_body();self.admin().command(first);counts=self.counts()
  self.fault('REVISION_CONFLICT',lambda:self.admin().command(second));self.assertEqual(self.counts(),counts)
 def test_same_request_is_receipt_and_does_not_restore_revoked_grant(self):
  body=self.grant_body();row=self.admin().command(body)['grant'];self.admin().command(self.command('revoke_grant',self.staff_ref,expected_revision=row['revision']))
  replay=self.admin().command(body);self.assertTrue(replay['replayed']);self.assertFalse(replay['execution_authorized']);self.assertFalse(any(self.staff().session()['capability_permissions'].values()))
 def test_staff_and_foreign_company_cannot_administer(self):
  with self.assertRaises(self.protocol.AccessFault):self.admin(self.staff())
  body=self.grant_body();row=self.admin().command(body)
  self.fault('GRANT_NOT_FOUND',lambda:self.admin(self.foreign()).command(self.command('revoke_grant',self.staff_ref,expected_revision=row['grant']['revision'])))
 def test_foreign_company_cannot_recover_or_reuse_request(self):
  body=self.alias_body();result=self.admin().command(body)
  self.fault('RECEIPT_NOT_FOUND',lambda:self.admin(self.foreign()).read('receipts',body['request_id']))
  foreign=self.foreign();body['data']['local_actor_ref']=foreign.actor
  self.fault('REQUEST_CONFLICT',lambda:self.admin(foreign).command(body))
  self.fault('IDENTITY_REFERENCE_NOT_FOUND',lambda:self.admin(foreign).command(self.command('revoke_alias',result['alias']['id'],expected_revision=1)))
 def test_nondelegable_wallet_and_admin_roles_cannot_be_granted(self):
  for capability in sorted(self.protocol.NON_DELEGABLE|{'wallet.withdraw','wallet.read','role.admin'}):
   self.fault('INVALID_OR_NONDELEGABLE_CAPABILITY',lambda c=capability:self.admin().command(self.grant_body(capabilities=[c])))
  self.fault('LOCAL_ADMINISTRATOR_ROLE_IS_NOT_DELEGABLE',lambda:self.admin().command({**self.grant_body(),'subject_ref':self.owner().actor}))
 def test_mutated_request_and_extra_context_rejected(self):
  body=self.grant_body();self.admin().command(body)
  self.fault('REQUEST_CONFLICT',lambda:self.admin().command({**body,'data':{**body['data'],'evidence_digest':'b'*64}}))
  self.fault('INVALID_FIELDS',lambda:self.admin().command({**body,'tenant_ref':'foreign'}))
  self.fault('INVALID_FIELDS',lambda:self.admin().command({**body,'data':{**body['data'],'request_id':str(uuid.uuid4())}}))
 def test_invalid_expiry_revision_scope_and_evidence_are_atomic(self):
  before=self.counts()
  for values in [{'expires_at':'2020-01-01T00:00:00Z'},{'expires_at':'2030-01-01'},{'expires_at':False},{'expected_revision':True},{'evidence_digest':123},{'capabilities':['crm.prospect.manage']*2}]:
   with self.assertRaises(self.protocol.AccessFault):self.admin().command(self.grant_body(**values))
  self.assertEqual(self.counts(),before)
 def test_policy_event_failure_rolls_back_grant(self):
  with self.fail_policy_event():
   self.fault('INJECTED_EVENT_FAILURE',lambda:self.admin().command(self.grant_body()))
  self.assertIsNone(self.owner().store.get('grant',self.owner().tenant,subject_ref=self.staff_ref))
 def test_corrupt_policy_is_rejected(self):
  row=self.admin().command(self.grant_body())['grant'];self.corrupt('grant',row['id'])
  self.fault('POLICY_INTEGRITY_REVIEW_REQUIRED',lambda:self.staff().session())
 def test_consent_revocation_reaches_crm_and_is_idempotent(self):
  cid,body,result=self.consent();record=result['consent'];revoke=self.command('revoke_consent',record['id'],expected_revision=1)
  revoked=self.admin().command(revoke);self.assertEqual(revoked['crm_revocation']['state'],'REVOKED_IN_CRM')
  self.assertFalse(self.crm().get(cid)['consents']['EMAIL:MARKETING']['granted']);version=self.crm().get(cid)['revision']
  self.assertTrue(self.admin().command(revoke)['replayed']);self.assertEqual(self.crm().get(cid)['revision'],version)
 def test_consent_and_crm_revoke_roll_back_if_policy_event_fails(self):
  cid,body,result=self.consent();before=self.crm().get(cid);history_before=len(self.crm().history(cid)['events'])
  with self.fail_policy_event():
   self.fault('INJECTED_EVENT_FAILURE',lambda:self.admin().command(self.command('revoke_consent',result['consent']['id'],expected_revision=1)))
  after=self.crm().get(cid);self.assertEqual(len(self.crm().history(cid)['events']),history_before);self.assertEqual(after['revision'],before['revision']);self.assertTrue(after['consents']['EMAIL:MARKETING']['granted'])
  self.assertEqual(self.admin().read('consents')['items'][0]['state'],'RECORDED')
 def test_consent_expiry_never_authorizes_delivery(self):
  cid,body,row=self.consent()
  with patch.object(self.service_module,'now',return_value=datetime.now(timezone.utc)+timedelta(days=3)):
   status=self.owner().consent_status({k:body['data'][k] for k in ('customer_ref','channel','purpose')});self.assertFalse(status['local_record_current']);self.assertFalse(status['delivery_authorized'])
 def test_consent_source_revision_and_evidence_mismatch(self):
  cid,body,row=self.consent()
  for key,value in [('source_contact_revision',0),('evidence_digest','b'*64)]:
   bad={**body,'request_id':str(uuid.uuid4()),'data':{**body['data'],'expected_revision':1,key:value}}
   with self.assertRaises(self.protocol.AccessFault):self.admin().command(bad)
 def test_every_channel_and_purpose_has_a_separate_consent(self):
  for channel in sorted(self.protocol.CHANNELS):
   for purpose in sorted(self.protocol.PURPOSES):
    cid,body,result=self.consent(channel,purpose);self.assertEqual(result['source']['contact_ref'],cid);self.assertFalse(result['delivery_authorized'])
 def test_foreign_contact_cannot_supply_consent(self):
  cid,body,result=self.consent();body['request_id']=str(uuid.uuid4());before=self.counts()
  with self.assertRaises(Exception) as caught:self.admin(self.foreign()).command(body)
  self.assertIn(getattr(caught.exception,'status',None),(403,404));self.assertEqual(self.counts(),before)
 def test_alias_expiry_and_equal_ids_never_grant_remote_access(self):
  result=self.admin().command(self.alias_body());self.assertFalse(result['cross_system_access_granted'])
  with patch.object(self.service_module,'now',return_value=datetime.now(timezone.utc)+timedelta(days=3)):
   rows=self.admin().read('aliases')['items'];self.assertEqual(rows[0]['state'],'EXPIRED');self.assertFalse(rows[0]['remote_identity_verified'])
 def test_alias_cannot_point_to_its_own_realm_or_foreign_local_member(self):
  self.fault('EXPLICIT_DISTINCT_REALM_REQUIRED',lambda:self.admin().command(self.alias_body(external_system=self.owner().system)))
  with self.assertRaises(self.protocol.AccessFault):self.admin().command(self.alias_body(local_actor_ref=self.foreign().actor))
 def test_schema_missing_and_unknown_sections_fail_closed(self):
  with patch.object(type(self.owner().store),'ready',return_value=False):
   self.fault('ACCESS_SCHEMA_INSTALL_REQUIRED',self.admin)
  self.fault('UNKNOWN_SECTION',lambda:self.admin().read('wallet'))
 def test_same_id_can_be_audited_without_creating_a_second_action(self):
  body=self.alias_body();first=self.admin().command(body);before=self.counts()
  for i in range(3):self.assertEqual(self.admin().read('receipts',body['request_id'])['result']['alias']['id'],first['alias']['id'])
  self.assertEqual(self.counts(),before)

 def test_simultaneous_revision_writers_have_a_single_commit(self):
  results=self.race(self.grant_body())
  self.assertEqual(sorted(results),[200,409])
  rows=self.admin().read('team')['members'];record=next(m['grant'] for m in rows if m['actor_ref']==self.staff_ref)
  self.assertEqual(record['revision'],1)
