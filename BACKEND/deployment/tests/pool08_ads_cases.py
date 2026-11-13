"""Local paid-media governance; intentionally no provider campaign creation/spend."""
import importlib,os,json,uuid,copy
from unittest.mock import patch
from pool08_mobile_message_cases import MobileCases
class AdsCases:
 def setup_ads(self):
  self.module=importlib.import_module(self.module_path+'.ads');store=importlib.import_module(self.module_path+'.ads_store');self.ads=self.module.Ads(store.Store(self.gen.crm.store),self.gen.crm);self.policy={'version':'fixture-1','currency':'COP','max_reserved_minor':150000,'max_daily_minor':50000,'support_digest':'a'*64};self.profile={'version':'fixture-1','platform':'META','account_id':'act_123','currency':'COP','ownership_support_digest':'b'*64};env=patch.dict(os.environ,{'COMMERCIAL_ADS_LIMITS':json.dumps({self.module.SYSTEM+':'+self.ads.store.scope:self.policy}),'COMMERCIAL_ADS_ACCOUNTS':json.dumps({self.ads.key():{'owned':self.profile}})});env.start();self.addCleanup(env.stop)
 def body(self,op='create',ref=None,rev=0,**data):
  if op=='create':
   asset=MobileCases.media(self);data={'title':'Plan local','platform':'META','account_ref':'owned','currency':'COP','total_budget_minor':100000,'daily_budget_minor':20000,'duration_days':5,'variants':[{'label':'A','headline':'Variante A','weight':50,'media_ref':asset},{'label':'B','headline':'Variante B','weight':50,'media_ref':asset}],**data}
  return {'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':rev,'data':data}
 def create_ad(self,**data):return self.ads.command(self.body(**data))['job_id']
 def action(self,ref,op,**data):return self.ads.command(self.body(op,ref,self.ads.get(ref)['revision'],**data))
 def approve(self,ref):self.action(ref,'review',confirmed_creatives=True,confirmed_budget=True);self.action(ref,'approve_plan',confirmed_impact=True,maximum_minor=1000000)
 def test_draft_and_receipt_idempotency_do_not_create_provider_campaign(self):
  self.setup_ads();body=self.body();r=self.ads.command(body);self.assertTrue(self.ads.command(body)['replayed']);d=self.ads.get(r['job_id']);self.assertEqual(d['remote_state'],'NOT_CREATED');self.assertIsNone(d['real_spend_minor']);self.assertFalse(self.ads.list()['spending_enabled']);body['data']['title']='Otro'
  with self.assertRaises(self.error):self.ads.command(body)
 def test_two_approvals_reserve_only_local_plan_and_cancel_releases(self):
  self.setup_ads();ref=self.create_ad();self.approve(ref);d=self.ads.get(ref);self.assertNotEqual(d['review']['request_id'],d['authorization']['request_id']);self.assertEqual(self.ads.company_reserved(),100000);self.action(ref,'cancel');self.assertEqual(self.ads.company_reserved(),0)
 def test_company_cap_prevents_overbooking_without_mutating_second_campaign(self):
  self.setup_ads();one=self.create_ad();two=self.create_ad();self.approve(one);self.action(two,'review',confirmed_creatives=True,confirmed_budget=True)
  with self.assertRaises(self.error):self.action(two,'approve_plan',confirmed_impact=True,maximum_minor=1000000)
  self.assertFalse(self.ads.get(two)['reserved']);self.assertEqual(self.ads.company_reserved(),100000)
 def test_exact_budgets_reject_float_bool_and_fractional_allocations(self):
  self.setup_ads()
  for data in [{'total_budget_minor':1.5},{'total_budget_minor':True},{'total_budget_minor':100001,'daily_budget_minor':20001},{'duration_days':31},{'currency':'USD'}]:
   with self.assertRaises(self.error):self.create_ad(**data)
 def test_declared_observation_proposes_without_changing_weights_or_budget(self):
  self.setup_ads();ref=self.create_ad();self.approve(ref);self.action(ref,'observe',source='MANUAL_DECLARED',support_digest='c'*64,variants=[{'label':'A','impressions':1000,'clicks':100,'cost_minor':10000},{'label':'B','impressions':1000,'clicks':100,'cost_minor':5000}]);d=self.ads.get(ref);self.assertEqual(d['proposal']['weights'],[40,60]);self.assertFalse(d['proposal']['automatically_applied']);self.assertFalse(d['proposal']['source_authenticity_verified']);self.assertEqual([v['weight'] for v in d['variants']],[50,50]);self.assertEqual(d['total_budget_minor'],100000)
 def test_insufficient_data_never_claims_optimizer_success(self):
  self.setup_ads();ref=self.create_ad();self.approve(ref);self.action(ref,'observe',source='MANUAL_DECLARED',support_digest='d'*64,variants=[{'label':'A','impressions':100,'clicks':2,'cost_minor':10000},{'label':'B','impressions':100,'clicks':3,'cost_minor':5000}]);self.assertEqual(self.ads.get(ref)['proposal']['state'],'INSUFFICIENT_REVIEWED_DATA')
 def test_false_impact_and_stale_revision_are_rejected(self):
  self.setup_ads();ref=self.create_ad();self.action(ref,'review',confirmed_creatives=True,confirmed_budget=True)
  with self.assertRaises(self.error):self.action(ref,'approve_plan',confirmed_impact=1,maximum_minor=1000000)
  with self.assertRaises(self.error):self.ads.command(self.body('cancel',ref,1))
 def test_policy_or_creative_revocation_invalidates_second_review(self):
  self.setup_ads();ref=self.create_ad();self.action(ref,'review',confirmed_creatives=True,confirmed_budget=True)
  with patch.dict(os.environ,{'COMMERCIAL_ADS_LIMITS':json.dumps({self.module.SYSTEM+':'+self.ads.store.scope:{**self.policy,'version':'changed'}})}):
   with self.assertRaises(self.error):self.action(ref,'approve_plan',confirmed_impact=True,maximum_minor=1000000)
  asset=self.ads.get(ref)['variants'][0]['media_ref'];lib=importlib.import_module(self.module_path+'.library_api').service(self.gen.crm);lib.command({'request_id':str(uuid.uuid4()),'operation':'withdraw','item_id':asset['item_id'],'expected_revision':3,'data':{'confirmed':True}})
  with self.assertRaises(self.error):self.action(ref,'approve_plan',confirmed_impact=True,maximum_minor=1000000)
 def test_revoked_role_cannot_read_reserve_cancel_or_execute(self):
  self.setup_ads();ref=self.create_ad()
  with patch.object(self.gen.crm,'authorize',side_effect=self.error('REVOKED',403)):
   for action in [lambda:self.ads.get(ref),lambda:self.ads.list(),lambda:self.action(ref,'cancel'),lambda:self.ads.execute(ref)]:
    with self.assertRaises(self.error):action()
 def test_live_execution_remains_closed_even_after_local_approval(self):
  self.setup_ads();ref=self.create_ad();self.approve(ref)
  with self.assertRaises(self.error):self.ads.execute(ref)
  self.assertIsNone(self.ads.get(ref)['remote_campaign_id']);self.assertFalse(self.ads.get(ref)['execution_qualified'])
 def test_company_audit_tampering_blocks_budget_calculation(self):
  self.setup_ads();ref=self.create_ad();events=list(self.ads.store.events(ref));events[0]['operation']='forged'
  with patch.object(self.ads.store,'events',return_value=iter(events)):
   with self.assertRaises(self.error):self.ads.company_reserved()
 def test_unconfigured_platform_is_not_silently_mapped_to_meta(self):
  self.setup_ads()
  for platform in ('TIKTOK','GOOGLE_YOUTUBE','UNKNOWN'):
   with self.assertRaises(self.error):self.create_ad(platform=platform)
 def test_daily_cap_is_aggregated_not_just_checked_per_campaign(self):
  self.setup_ads();one=self.create_ad(total_budget_minor=40000,daily_budget_minor=40000,duration_days=1);two=self.create_ad(total_budget_minor=40000,daily_budget_minor=40000,duration_days=1);self.approve(one);self.action(two,'review',confirmed_creatives=True,confirmed_budget=True)
  with self.assertRaises(self.error):self.action(two,'approve_plan',confirmed_impact=True,maximum_minor=1000000)
  self.assertEqual(self.ads.company_reserved('daily_budget_minor'),40000)
 def test_tiktok_and_google_video_plans_remain_distinct_local_campaigns(self):
  self.setup_ads();import subprocess,tempfile
  from pathlib import Path
  with tempfile.TemporaryDirectory(prefix='ads-video-') as folder:
   path=Path(folder)/'clip.mp4';subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=720x1280:r=24','-t','3','-an','-c:v','libx264','-pix_fmt','yuv420p','-threads','1',str(path)],check=True,timeout=30);asset=MobileCases.media(self,path.read_bytes(),'video/mp4')
  for platform in ('TIKTOK','GOOGLE_YOUTUBE'):
   with patch.dict(os.environ,{'COMMERCIAL_ADS_ACCOUNTS':json.dumps({self.ads.key():{'owned':{**self.profile,'platform':platform}}})}):
    variants=[{'label':label,'headline':'Vídeo '+label,'weight':50,'media_ref':asset} for label in ('A','B')];ref=self.create_ad(platform=platform,variants=variants,total_budget_minor=40000,daily_budget_minor=10000,duration_days=4);self.approve(ref);d=self.ads.get(ref);self.assertEqual(d['platform'],platform);self.assertEqual(d['remote_state'],'NOT_CREATED');self.assertTrue(d['reserved'])
 def test_control_proposal_uses_existing_motor_contract_without_grant_or_spending(self):
  self.setup_ads();ref=self.create_ad();self.approve(ref);self.action(ref,'prepare_control');brief=self.ads.get(ref)['control_brief'];self.assertEqual(brief['engine'],'Open Duet + agent-desktop');self.assertEqual(brief['operational_general'],'Jarvi');self.assertEqual(brief['conversational_general'],'Neko');self.assertEqual(brief['agent_optimizer'],'SOUP');self.assertEqual(brief['required_independent_authorizations']['browser_open'],2);self.assertEqual(brief['required_independent_authorizations']['browser_click'],3);self.assertIsNone(brief['execution_grant']);self.assertFalse(brief['spending_authorization']);self.assertFalse(brief['submitted_to_engine']);self.assertEqual(brief['source']['scope'],self.ads.store.scope);self.assertEqual(brief['source']['source_revision'],self.ads.get(ref)['revision'])
 def test_cancel_invalidates_prepared_motor_proposal(self):
  self.setup_ads();ref=self.create_ad();self.approve(ref);self.action(ref,'prepare_control');self.action(ref,'cancel');self.assertIsNone(self.ads.get(ref)['control_brief'])
