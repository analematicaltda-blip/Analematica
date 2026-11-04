"""Calendar outbox: real DB/auth policies, simulated worker transport, no external sends."""
import json
import os
import uuid
from datetime import timedelta
from unittest.mock import patch,Mock
import unittest
import test_workspace as fixtures
from app.models.user import Usuario
from app.models.workspace import WorkspaceAsset,WorkspaceChannel
from app.models.billing import Suscripcion,ConsumoInquilino
from app.models.campaigns import Campaign,CampaignTarget
from app.services import campaign_service as cs,workspace_service as ws

class CampaignTests(unittest.TestCase):
 def setUp(self):
  fixtures.WorkspaceTests.setUp(self)
  switch=patch.dict(os.environ,{'CAMPAIGN_DELIVERY_ENABLED':'1'});switch.start();self.addCleanup(switch.stop)
 tearDown=fixtures.WorkspaceTests.tearDown
 login=fixtures.WorkspaceTests.login
 def get(self,path):return self.client.get('/api/v1/workspace/campaigns'+path)
 def post(self,path,body):return self.client.post('/api/v1/workspace/campaigns'+path,json=body)
 def put(self,path,body):return self.client.put('/api/v1/workspace/campaigns'+path,json=body)
 def asset(self):
  access=ws.access_for(self.db,self.db.get(Usuario,self.users['full-admin_empresa']))
  return ws.save_asset(self.db,access,{'filename':uuid.uuid4().hex+'.mp4'},'reel','Own source')['id']
 def connect(self,provider='youtube'):
  credentials={key:'test-not-real-'+key for key in cs.PROVIDERS[provider]['fields']}
  if provider=='gmail':credentials['sender_email']='sender@example.org'
  for key in ['account_id','page_id','phone_number_id']:
   if key in credentials:credentials[key]='123456789'
  result=self.put('/channels/'+provider,{'label':'Own '+provider,'credentials':credentials});self.assertEqual(result.status_code,200,result.text);return credentials
 def contact(self,provider='gmail',address='member@example.org'):
  result=self.post('/contacts',{'contacts':[{'provider':provider,'address':address,'consent_source':'Signed enrollment 2026-11-04','subscribed':True}]});self.assertEqual(result.status_code,201,result.text);return result.json()['ids'][0]
 def body(self,providers=None,contacts=None):return {'idempotency_key':str(uuid.uuid4()),'asset_id':self.asset(),'title':'Test campaign','description':'Own company only','scheduled_at':(cs.now()-timedelta(seconds=1)).isoformat(),'timezone':'America/Bogota','providers':providers or ['youtube'],'contact_ids':contacts or [],'options':{'youtube':{'made_for_kids':False},'whatsapp':{'template_name':'approved_video','template_language':'es','template_variables':[]}}}
 def create(self,body):
  result=self.post('',body);self.assertEqual(result.status_code,201,result.text);return result.json()
 def approve(self,campaign):
  result=self.post('/'+campaign['id']+'/approve',{'confirm_dispatch':True});self.assertEqual(result.status_code,200,result.text)
 def transport(self,path,body=None,method=None):
  if path=='/internal/campaigns/adapt':return Mock(json=lambda:{'filename':uuid.uuid4().hex+'.mp4'})
  if path=='/internal/campaigns/deliver':return Mock(json=lambda:{'outcome':'accepted','remote_id':'test-'+body['job_id'],'provider_state':{}})
  raise AssertionError('Unexpected worker path '+path)
 def test_preview_mode_cannot_approve_or_dispatch_external_jobs(self):
  self.connect();row=self.create(self.body())
  with patch.dict(os.environ,{'CAMPAIGN_DELIVERY_ENABLED':'0'}),patch.object(ws,'worker') as worker:
   self.assertEqual(self.post('/'+row['id']+'/approve',{'confirm_dispatch':True}).status_code,409)
   self.assertEqual(cs.tick(self.db),0);worker.assert_not_called()
 def test_basic_and_undelegated_staff_cannot_use_campaigns_or_connect_channels(self):
  for account,expected in [('basic-admin_empresa',402),('full-jefe_area',403)]:
   self.login(account)
   with patch.object(ws,'worker') as worker:
    for path in ['', '/channels','/settings','/contacts']:self.assertEqual(self.get(path).status_code,expected,path)
    self.assertEqual(self.post('',self.body()).status_code,expected);worker.assert_not_called()
 def test_channels_are_encrypted_scoped_and_never_reflect_secrets(self):
  for provider in cs.PROVIDERS:
   secrets=self.connect(provider)
   response=self.get('/channels');self.assertEqual(response.status_code,200)
   for value in secrets.values():self.assertNotIn(value,response.text)
  for row in self.db.query(WorkspaceChannel).all():self.assertNotIn('test-not-real-',row.encrypted_credentials)
  response=self.put('/channels/gmail',{'label':'test','credentials':{'client_secret':'NEVER-ECHO-ME'}});self.assertEqual(response.status_code,422);self.assertNotIn('NEVER-ECHO-ME',response.text)
  self.login('other-admin_empresa');self.assertEqual(self.get('/channels').json()['channels'],[])
 def test_draft_is_idempotent_and_has_no_external_side_effect(self):
  body=self.body()
  with patch.object(ws,'worker') as worker:
   one=self.create(body);two=self.create(body);self.assertEqual(one['id'],two['id']);worker.assert_not_called()
  self.assertEqual(self.post('',{**body,'title':'Different payload'}).status_code,409)
  self.assertEqual(self.db.query(CampaignTarget).count(),1);self.assertEqual(self.db.query(ConsumoInquilino).count(),0)
 def test_calendar_requires_aware_valid_time_and_explicit_approval(self):
  body=self.body()
  for changed in [{'scheduled_at':'2026-11-04T15:00:00'},{'timezone':'Not/AZone'},{'scheduled_at':(cs.now()-timedelta(days=1)).isoformat()}]:self.assertEqual(self.post('',{**body,**changed}).status_code,422)
  row=self.create(body);self.assertEqual(self.post('/'+row['id']+'/approve',{'confirm_dispatch':False}).status_code,422)
  self.assertEqual(self.post('/'+row['id']+'/approve',{'confirm_dispatch':True}).status_code,409)
  self.connect();self.approve(row)
  self.assertEqual(self.post('/'+row['id']+'/approve',{'confirm_dispatch':True}).status_code,409)
 def test_bulk_audience_dispatches_once_per_recipient_reuses_adaptation_and_charges_once(self):
  contacts=[self.contact(),self.contact(address='second@example.org')];self.connect('gmail');row=self.create(self.body(['gmail'],contacts));self.approve(row)
  with patch.object(ws,'worker',side_effect=self.transport) as worker:
   self.assertEqual(cs.tick(self.db),2);self.assertEqual(cs.tick(self.db),0)
   deliveries=[call.args[1] for call in worker.call_args_list if call.args[0].endswith('/deliver')]
   self.assertEqual({body['recipient'] for body in deliveries},{'member@example.org','second@example.org'})
   self.assertEqual(len([call for call in worker.call_args_list if call.args[0].endswith('/adapt')]),1)
   self.assertTrue(all(body['workspace'].startswith('tenant:') for body in deliveries))
  self.db.expire_all();self.assertEqual(self.db.query(ConsumoInquilino).filter_by(capacidad='social_posts').one().cantidad_usada,2)
  self.assertEqual(self.get('').json()['campaigns'][0]['state'],'completed')
  self.assertEqual({row['recipient'] for row in self.get('').json()['campaigns'][0]['targets']},{'member@example.org','second@example.org'})
 def test_future_calendar_waits_and_survives_new_database_session(self):
  self.connect();body=self.body();body['scheduled_at']=(cs.now()+timedelta(minutes=10)).isoformat();row=self.create(body);self.approve(row)
  self.assertEqual(self.get('').json()['campaigns'][0]['state'],'scheduled')
  with self.factory() as fresh,patch.object(ws,'worker',side_effect=self.transport) as worker:
   self.assertEqual(cs.tick(fresh),0);worker.assert_not_called()
   with patch.object(cs,'now',return_value=cs.now()+timedelta(minutes=11)):self.assertEqual(cs.tick(fresh),1)
 def test_tenant_isolation_in_campaign_approval_audience_and_adaptation(self):
  contact=self.contact();row=self.create(self.body());self.connect();self.login('other-admin_empresa')
  self.assertEqual(self.post('/'+row['id']+'/approve',{'confirm_dispatch':True}).status_code,404)
  self.assertEqual(self.post('/adaptations',{'asset_id':row['asset_id'],'profile':'gmail'}).status_code,404)
  self.assertEqual(self.get('/contacts').json()['contacts'],[])
  body=self.body(['gmail'],[contact]);self.assertEqual(self.post('',body).status_code,404)
 def test_revoked_permission_inactive_plan_and_changed_channel_block_scheduled_sends(self):
  for mode in ['channel','plan']:
   self.login('full-admin_empresa');self.connect();row=self.create(self.body());self.approve(row)
   if mode=='channel':self.connect() # new encrypted revision, even with the same visible label
   else:
    user=self.db.get(Usuario,self.users['full-admin_empresa']);sub=self.db.query(Suscripcion).filter_by(inquilino_id=user.inquilino_id).one();sub.estado='vencida';self.db.commit()
   with patch.object(ws,'worker') as worker:cs.tick(self.db);worker.assert_not_called()
   self.db.expire_all();self.assertEqual(self.db.query(CampaignTarget).filter_by(campaign_id=row['id']).one().state,'blocked')
 def test_unsubscribe_is_checked_again_at_dispatch(self):
  contact=self.contact();self.connect('gmail');row=self.create(self.body(['gmail'],[contact]));self.approve(row)
  self.assertEqual(self.put('/contacts/'+contact,{'subscribed':False}).status_code,200)
  with patch.object(ws,'worker') as worker:cs.tick(self.db);worker.assert_not_called()
  self.db.expire_all();self.assertEqual(self.db.query(CampaignTarget).one().state,'blocked')
 def test_pending_provider_is_polled_with_new_phase_not_duplicated(self):
  self.connect();row=self.create(self.body());self.approve(row)
  def worker(path,body=None,method=None):
   if path.endswith('/deliver'):return Mock(json=lambda:{'outcome':'pending' if body['phase']==0 else 'published','remote_id':'remote','provider_state':{'container_id':'123'}})
   return self.transport(path,body,method)
  with patch.object(ws,'worker',side_effect=worker) as transport:
   cs.tick(self.db)
   with patch.object(cs,'now',return_value=cs.now()+timedelta(seconds=31)):cs.tick(self.db)
   phases=[call.args[1]['phase'] for call in transport.call_args_list if call.args[0].endswith('/deliver')];self.assertEqual(phases,[0,1])
  self.db.expire_all();self.assertEqual(self.db.query(ConsumoInquilino).one().cantidad_usada,1)
 def test_uncertain_result_never_requeues_and_cancel_prevents_unsent_targets(self):
  self.connect();row=self.create(self.body());self.approve(row)
  def worker(path,body=None,method=None):
   if path.endswith('/deliver'):raise RuntimeError('connection interrupted')
   return self.transport(path,body,method)
  with patch.object(ws,'worker',side_effect=worker) as transport:
   cs.tick(self.db);cs.tick(self.db);self.assertEqual(len([call for call in transport.call_args_list if call.args[0].endswith('/deliver')]),1)
  self.db.expire_all();self.assertEqual(self.db.query(CampaignTarget).one().state,'unknown')
  second=self.create(self.body());self.approve(second);self.post('/'+second['id']+'/cancel',{})
  with patch.object(ws,'worker') as transport:cs.tick(self.db);transport.assert_not_called()
 def test_reschedule_restores_draft_and_media_links_require_signed_target_scope(self):
  self.connect();row=self.create(self.body());self.approve(row)
  response=self.put('/'+row['id']+'/schedule',{'scheduled_at':(cs.now()+timedelta(hours=1)).isoformat(),'timezone':'America/Bogota'});self.assertEqual(response.status_code,200,response.text);self.assertEqual(response.json()['state'],'draft')
  token=cs.link_token('access',row['targets'][0]['id'],'tenant:1',timedelta(hours=1));self.assertEqual(self.get('/media/'+row['targets'][0]['id']+'?token='+token).status_code,404)
 def test_one_click_unsubscribe_get_is_safe_and_post_records_bye(self):
  contact=self.contact();access=ws.access_for(self.db,self.db.get(Usuario,self.users['full-admin_empresa']));token=cs.link_token('campaign-unsubscribe',contact,access.scope,timedelta(days=1));path='/unsubscribe?token='+token
  self.assertEqual(self.get(path).status_code,200);self.assertTrue(self.get('/contacts').json()['contacts'][0]['subscribed'])
  self.assertEqual(self.client.post('/api/v1/workspace/campaigns'+path).status_code,200);self.assertFalse(self.get('/contacts').json()['contacts'][0]['subscribed'])

 def test_delegation_revoked_after_approval_blocks_creator_at_dispatch(self):
  self.connect();body=self.body();member=self.users['full-jefe_area']
  self.client.put(f'/api/v1/workspace/team/{member}/permissions',json={'permissions':{'publish':True}})
  self.login('full-jefe_area');row=self.create(body);self.approve(row)
  self.login('full-admin_empresa');self.client.put(f'/api/v1/workspace/team/{member}/permissions',json={'permissions':{'publish':False}})
  with patch.object(ws,'worker') as worker:cs.tick(self.db);worker.assert_not_called()
  self.db.expire_all();self.assertEqual(self.db.query(CampaignTarget).one().state,'blocked')
 def test_concurrent_workers_claim_one_job_only(self):
  from concurrent.futures import ThreadPoolExecutor
  from threading import Barrier
  self.connect();row=self.create(self.body());self.approve(row);barrier=Barrier(2)
  def run():
   with self.factory() as db:barrier.wait();return cs.tick(db)
  with patch.object(ws,'worker',side_effect=self.transport) as worker,ThreadPoolExecutor(max_workers=2) as pool:
   futures=[pool.submit(run) for _ in range(2)];self.assertEqual(sorted(f.result() for f in futures),[0,1])
   self.assertEqual(len([call for call in worker.call_args_list if call.args[0].endswith('/deliver')]),1)
 def test_unknown_reconciles_by_reading_journal_without_repeating_send(self):
  self.connect();row=self.create(self.body());self.approve(row)
  def worker(path,body=None,method=None):
   if path.endswith('/deliver'):raise RuntimeError('lost response')
   if '/result/' in path:return Mock(json=lambda:{'found':True,'status':'complete','result':{'outcome':'accepted','remote_id':'confirmed-late','provider_state':{}}})
   return self.transport(path,body,method)
  with patch.object(ws,'worker',side_effect=worker) as transport:
   cs.tick(self.db)
   with patch.object(cs,'now',return_value=cs.now()+timedelta(minutes=6)):cs.tick(self.db)
   self.assertEqual(len([call for call in transport.call_args_list if call.args[0].endswith('/deliver')]),1)
  self.db.expire_all();job=self.db.query(CampaignTarget).one();self.assertEqual(job.state,'accepted');self.assertEqual(job.phase,1)
 def test_instagram_requires_public_origin_configuration_and_only_owner_can_set_it(self):
  self.connect('instagram');row=self.create(self.body(['instagram']))
  self.assertEqual(self.post('/'+row['id']+'/approve',{'confirm_dispatch':True}).status_code,409)
  self.assertEqual(self.put('/settings/media-origin',{'origin':'https://media.example.org'}).status_code,403)
  self.login('owner-admin_general')
  self.assertEqual(self.put('/settings/media-origin',{'origin':'https://private-8080.app.github.dev'}).status_code,503)
  self.assertEqual(self.put('/settings/media-origin',{'origin':'https://example.org:bad'}).status_code,503)
  self.assertEqual(self.put('/settings/media-origin',{'origin':'https://media.example.org'}).status_code,200)
  self.login('full-admin_empresa');self.approve(row)

if __name__=='__main__':unittest.main()
