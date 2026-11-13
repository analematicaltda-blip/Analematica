"""Real HTTP administrator flows, owned SQL schemas, no real customer/provider."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import datetime,timedelta,timezone
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='access_http_setup')
base=fixture['CRMHTTPChecks']
class AccessAdminHTTPChecks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__)
 tearDownClass=classmethod(base.tearDownClass.__func__)
 targets=base.targets
 prefix=base.prefix
 unwrap=base.unwrap
 def test_explicit_alias_replay_revoke_and_receipt(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/access/'
   ctx=self.unwrap(client.get(url+'context'+suffix,params=query));self.assertFalse(ctx['wallet_permissions_granted'])
   self.assertNotIn('ledger.sale.post',ctx['capabilities']);self.assertFalse(ctx['cross_system_access_granted'])
   members=self.unwrap(client.get(url+'team'+suffix,params=query))['members'];self.assertTrue(members)
   data=dict(local_actor_ref=ctx['context']['actor_ref'],external_system=ctx['external_systems'][0],external_tenant_ref='external-'+uuid.uuid4().hex,external_actor_ref='999999',expected_revision=0,expires_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),evidence_digest='a'*64)
   body=dict(request_id=str(uuid.uuid4()),operation='link_identity',subject_ref=None,data=data)
   result=self.unwrap(client.post(url+'commands'+suffix,params=query,json=body));self.assertFalse(result['cross_system_access_granted']);alias=result['alias'];self.assertEqual(alias['state'],'EXTERNAL_REVIEW_REQUIRED')
   self.assertTrue(self.unwrap(client.post(url+'commands'+suffix,params=query,json=body))['replayed'])
   receipt=self.unwrap(client.get(url+'receipts/'+body['request_id']+suffix,params=query));self.assertEqual(receipt['result']['alias']['id'],alias['id'])
   body['data']={**data,'external_actor_ref':'another'};self.assertEqual(client.post(url+'commands'+suffix,params=query,json=body).status_code,409)
   revoke=dict(request_id=str(uuid.uuid4()),operation='revoke_alias',subject_ref=alias['id'],data={'expected_revision':alias['revision']})
   self.assertEqual(self.unwrap(client.post(url+'commands'+suffix,params=query,json=revoke))['alias']['state'],'REVOKED')
   self.assertTrue(self.unwrap(client.get(url+'history'+suffix,params=query))['items'])
 def test_current_contact_consent_is_required_and_revocable(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/';ctx=self.unwrap(client.get(url+'context'+suffix,params=query));due=(datetime.now(timezone.utc)+timedelta(days=2)).isoformat()
   create=dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data={'name':'Access synthetic','email':uuid.uuid4().hex+'@example.test','origin':'TEST','responsible_ref':ctx['actor_ref']})
   cid=self.unwrap(client.post(url+'commands'+suffix,params=query,json=create))['contact_id']
   body=dict(request_id=str(uuid.uuid4()),operation='record_consent',subject_ref=None,data={'customer_ref':cid,'source_contact_revision':1,'channel':'EMAIL','purpose':'MARKETING','evidence_digest':'a'*64,'expires_at':due,'expected_revision':0})
   endpoint=url+'access/commands'+suffix
   self.assertEqual(client.post(endpoint,params=query,json=body).status_code,409)
   consent=dict(request_id=str(uuid.uuid4()),operation='consent',contact_id=cid,expected_revision=1,data={'channel':'EMAIL','purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':due})
   self.unwrap(client.post(url+'commands'+suffix,params=query,json=consent));body['data']['source_contact_revision']=2
   result=self.unwrap(client.post(endpoint,params=query,json=body));self.assertTrue(result['source']['bound_to_crm']);self.assertFalse(result['authenticity_of_evidence_verified']);self.assertFalse(result['delivery_authorized'])
   record=result['consent'];revoke=dict(request_id=str(uuid.uuid4()),operation='revoke_consent',subject_ref=record['id'],data={'expected_revision':1})
   self.assertEqual(self.unwrap(client.post(endpoint,params=query,json=revoke))['consent']['state'],'REVOKED')
   current=self.unwrap(client.get(url+'contacts/'+cid+suffix,params=query))
   withdraw=dict(request_id=str(uuid.uuid4()),operation='withdraw',contact_id=cid,expected_revision=current['revision'],data={'reason':'Synthetic withdrawal'})
   withdrawn=self.unwrap(client.post(url+'commands'+suffix,params=query,json=withdraw));body['request_id']=str(uuid.uuid4());body['data'].update(expected_revision=2,source_contact_revision=withdrawn['revision'])
   self.assertEqual(client.post(endpoint,params=query,json=body).status_code,409)
 def test_delegation_is_live_scoped_and_never_delegates_wallet(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/access/'
   creds=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1]
   staff={'Authorization':'Bearer '+creds['staff_token']}
   self.assertEqual(client.get(url+'team'+suffix,params=query,headers=staff).status_code,403)
   members=self.unwrap(client.get(url+'team'+suffix,params=query))['members'];member=next(m for m in members if m['actor_ref']==creds['staff_ref'])
   data=dict(capabilities=['crm.prospect.manage'],role_fingerprint=member['role_fingerprint'],expected_revision=member['grant']['revision'] if member['grant'] else 0,expires_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),evidence_digest='a'*64)
   body=dict(request_id=str(uuid.uuid4()),operation='grant',subject_ref=member['actor_ref'],data=data)
   bad={**body,'data':{**data,'capabilities':['wallet.withdraw']}}
   self.assertEqual(client.post(url+'commands'+suffix,params=query,json=bad).status_code,422)
   result=self.unwrap(client.post(url+'commands'+suffix,params=query,json=body));self.assertFalse(result['wallet_permissions_granted'])
   self.assertEqual(client.get(prefix+'crm/context'+suffix,params=query,headers=staff).status_code,200)
   self.assertEqual(client.post(url+'commands'+suffix,params=query,json=body,headers=staff).status_code,403)
   self.assertEqual(client.get(url+'team'+suffix,params=query,headers={'Authorization':'Bearer '+creds['other_token']}).status_code,403 if system!='sga-cd' else 200)
   revoke=dict(request_id=str(uuid.uuid4()),operation='revoke_grant',subject_ref=member['actor_ref'],data={'expected_revision':result['grant']['revision']})
   self.unwrap(client.post(url+'commands'+suffix,params=query,json=revoke))
   self.assertEqual(client.get(prefix+'crm/context'+suffix,params=query,headers=staff).status_code,403)
 def test_malformed_json_and_provider_context_are_bounded(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/access/commands'+suffix
   for raw,status in [('{"a":1,"a":2}',400),(' '*17000,413)]:
    response=client.post(url,params=query,content=raw,headers={'Content-Type':'application/json'});self.assertEqual(response.status_code,status,response.text);self.assertEqual(response.headers['cache-control'],'no-store')
   self.assertEqual(client.post(url,params=query,content='<xml/>',headers={'Content-Type':'application/xml'}).status_code,415)
   self.assertEqual(client.get(prefix+'crm/access/commands'+suffix,params=query).status_code,405 if system!='sga-cd' else 404)
   if system!='sga-cd':self.assertEqual(client.get(prefix+'crm/access/context'+suffix,params=[('provider_id',query['provider_id']),('provider_id',query['provider_id'])]).status_code,400)
 def test_consent_revocation_changes_source_crm(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/';ctx=self.unwrap(client.get(url+'context'+suffix,params=query));due=(datetime.now(timezone.utc)+timedelta(days=2)).isoformat()
   create=dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data={'name':'Revocation HTTP synthetic','email':uuid.uuid4().hex+'@example.test','origin':'TEST','responsible_ref':ctx['actor_ref']})
   cid=self.unwrap(client.post(url+'commands'+suffix,params=query,json=create))['contact_id']
   grant=dict(request_id=str(uuid.uuid4()),operation='consent',contact_id=cid,expected_revision=1,data=dict(channel='EMAIL',purpose='MARKETING',granted=True,evidence_digest='a'*64,expires_at=due))
   self.unwrap(client.post(url+'commands'+suffix,params=query,json=grant))
   record=dict(request_id=str(uuid.uuid4()),operation='record_consent',subject_ref=None,data=dict(customer_ref=cid,source_contact_revision=2,channel='EMAIL',purpose='MARKETING',evidence_digest='a'*64,expires_at=due,expected_revision=0))
   row=self.unwrap(client.post(url+'access/commands'+suffix,params=query,json=record))['consent']
   revoke=dict(request_id=str(uuid.uuid4()),operation='revoke_consent',subject_ref=row['id'],data={'expected_revision':1})
   self.assertEqual(self.unwrap(client.post(url+'access/commands'+suffix,params=query,json=revoke))['crm_revocation']['state'],'REVOKED_IN_CRM')
   contact=self.unwrap(client.get(url+'contacts/'+cid+suffix,params=query));self.assertFalse(contact['consents']['EMAIL:MARKETING']['granted'])
   self.assertTrue(self.unwrap(client.post(url+'access/commands'+suffix,params=query,json=revoke))['replayed'])
 def test_authority_context_invalid_payloads_and_private_responses(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/access/'
   for section in ('context','team','consents','aliases','history'):
    response=client.get(url+section+suffix,params=query);self.assertEqual(response.status_code,200,response.text);self.assertEqual(response.headers['cache-control'],'no-store')
    self.assertIn(client.get(url+section+suffix,params=query,headers={'Authorization':''}).status_code,(401,403))
   self.assertEqual(client.get(url+'context'+suffix,params={**query,'tenant_ref':'foreign'}).status_code,400)
   self.assertEqual(client.get(url+'receipts/'+str(uuid.uuid4())+suffix,params=query).status_code,404)
   for payload in ([],{}, {'request_id':str(uuid.uuid4()),'operation':[], 'subject_ref':None,'data':{}},{'request_id':str(uuid.uuid4()),'operation':'wallet.withdraw','subject_ref':None,'data':{}}):
    self.assertEqual(client.post(url+'commands'+suffix,params=query,json=payload).status_code,422)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AccessAdminHTTPChecks)).wasSuccessful())
