"""Commercial reporting regression cases against each owned transactional store."""
import importlib,uuid,copy,os,json,httpx
from datetime import datetime,timedelta,timezone,date
from unittest.mock import patch
class AnalyticsCases:
 def setup_analytics(self):
  self.a=importlib.import_module(self.module_path+'.analytics');self.sources=importlib.import_module(self.module_path+'.analytics_sources');self.forecast=importlib.import_module(self.module_path+'.analytics_forecast');self.costs=importlib.import_module(self.module_path+'.analytics_costs');store=importlib.import_module(self.module_path+'.analytics_store');self.now=datetime(2026,11,12,12,tzinfo=timezone.utc);self.analytics=self.a.Analytics(store.Store(self.gen.crm.store),self.gen.crm,clock=lambda:self.now)
 def body(self):return {'request_id':str(uuid.uuid4()),'operation':'build','job_id':None,'expected_revision':0,'data':{'since':'2026-10-01','until':'2026-10-31','provider_reads':False,'confirmed_scope':True}}
 def sources_ok(self,rows=None):
  from contextlib import ExitStack
  stack=ExitStack();stack.enter_context(patch.object(self.sources,'contacts',return_value=[]));stack.enter_context(patch.object(self.sources,'opportunities',return_value=[]));stack.enter_context(patch.object(self.sources,'documents',return_value=[]));stack.enter_context(patch.object(self.sources,'income',return_value={'rows':rows or [],'proof':[],'scope':'VERIFIED_COMMERCIAL_MODULE_JOURNALS_ONLY'}));stack.enter_context(patch.object(self.sources,'attribution',return_value={'groups':[]}));return stack
 def test_persisted_report_zero_is_distinct_from_unavailable_and_does_not_write_ledger(self):
  self.setup_analytics()
  with self.sources_ok():receipt=self.analytics.command(self.body())
  d=self.analytics.get(receipt['job_id']);self.assertEqual(d['status'],'SOURCE_SNAPSHOT');self.assertEqual(d['report']['period_economics']['net_revenue_cop'],'0.00');self.assertEqual(d['report']['forecast']['state'],'INSUFFICIENT_REVIEWED_HISTORY');self.assertIsNone(d['report']['LTV']['value']);self.assertFalse(d['report']['fiscal_or_bank_action_executed']);self.assertTrue(self.analytics.history(d['id'])['history_verified'])
 def test_source_failure_does_not_fabricate_zero_sales(self):
  self.setup_analytics()
  with self.sources_ok(),patch.object(self.sources,'income',side_effect=self.error('LEDGER_UNAVAILABLE',503)):
   r=self.analytics.collect('2026-10-01','2026-10-31')
  self.assertEqual(r['state'],'PARTIAL');self.assertIsNone(r['period_economics']);self.assertEqual(r['sources']['ledger']['reason'],'LEDGER_UNAVAILABLE')
 def test_report_replay_returns_existing_reservation_without_repeating_reads(self):
  self.setup_analytics();body=self.body()
  with self.sources_ok(),patch.object(self.analytics,'collect',wraps=self.analytics.collect) as collect:
   first=self.analytics.command(body);replay=self.analytics.command(body);self.assertEqual(collect.call_count,1)
  self.assertTrue(replay['replayed']);self.assertEqual(replay['job_id'],first['job_id']);self.assertEqual(self.analytics.get(first['job_id'])['revision'],2)
  changed=copy.deepcopy(body);changed['data']['since']='2026-10-02'
  with self.assertRaises(self.error):self.analytics.command(changed)
 def test_dates_scope_and_confirmation_are_required_before_collection(self):
  self.setup_analytics()
  for field,value in [('until','2027-01-01'),('since','2026-11-01'),('confirmed_scope',False),('provider_reads',1)]:
   b=self.body();b['data'][field]=value
   with self.assertRaises(self.error):self.analytics.command(b)
  self.assertEqual(self.analytics.list()['reports'],[])
 def test_revoked_role_blocks_report_and_receipt(self):
  self.setup_analytics();b=self.body()
  with self.sources_ok():r=self.analytics.command(b)
  with patch.object(self.gen.crm,'authorize',side_effect=self.error('REVOKED',403)):
   for op in [lambda:self.analytics.get(r['job_id']),lambda:self.analytics.history(r['job_id']),lambda:self.analytics.receipt(b['request_id'])]:
    with self.assertRaises(self.error):op()
 def test_corrupt_audit_blocks_report(self):
  self.setup_analytics()
  with self.sources_ok():r=self.analytics.command(self.body())
  events=list(self.analytics.store.events(r['job_id']));events[0]['operation']='tampered'
  with patch.object(self.analytics.store,'events',return_value=iter(events)):
   with self.assertRaises(self.error):self.analytics.get(r['job_id'])
 def test_interrupted_collection_can_only_recover_after_timeout(self):
  self.setup_analytics();b=self.body()
  with patch.object(self.analytics,'collect',side_effect=RuntimeError('interrupted')):
   with self.assertRaises(RuntimeError):self.analytics.command(b)
  ref=self.analytics.receipt(b['request_id'])['job_id'];recover={'request_id':str(uuid.uuid4()),'operation':'recover','job_id':ref,'expected_revision':1,'data':{}}
  with self.assertRaises(self.error):self.analytics.command(recover)
  self.now+=timedelta(minutes=16);self.analytics.command(recover);self.assertEqual(self.analytics.get(ref)['status'],'INTERRUPTED')
 def test_drafts_do_not_count_as_revenue_and_uncertain_sales_block_metrics(self):
  self.setup_analytics();r=self.sources.income(self.gen.crm,[{'status':'DRAFT'}]);self.assertEqual(r['rows'],[])
  with self.assertRaises(self.error):self.sources.income(self.gen.crm,[{'status':'PENDING_CONFIRM'}])
 def test_temporal_forecast_uses_explicit_history_and_independent_holdout(self):
  self.setup_analytics();series=[{'date':(date(2026,1,1)+timedelta(days=n)).isoformat(),'value':'10.00'} for n in range(40)];r=self.forecast.forecast(series);self.assertEqual(r['state'],'BASELINE_ESTIMATE');self.assertEqual(r['test_mae'],'0.00');self.assertEqual(len(r['predictions']),7);self.assertEqual(r['training_points'],26);self.assertFalse(r['calibrated_for_production'])
  broken=copy.deepcopy(series);broken[20]['date']='2026-02-20'
  with self.assertRaises(self.error):self.forecast.forecast(broken)
  for v in ['NaN','Infinity','0.001',1.5,True]:
   with self.assertRaises(self.error):self.forecast.money(v)
 def test_forecast_does_not_use_test_period_for_model_selection(self):
  self.setup_analytics();series=[{'date':(date(2026,1,1)+timedelta(days=n)).isoformat(),'value':str(n)+'.00'} for n in range(40)];r=self.forecast.forecast(series);other=copy.deepcopy(series)
  for p in other[-7:]:p['value']='9999.00'
  changed=self.forecast.forecast(other);self.assertEqual(r['model'],changed['model']);self.assertEqual(r['validation_mae'],changed['validation_mae']);self.assertNotEqual(r['test_mae'],changed['test_mae'])
 def test_provider_reads_disabled_before_any_network(self):
  self.setup_analytics()
  with patch.dict(os.environ,{'COMMERCIAL_ANALYTICS_PROVIDER_READ_ENABLED':'0'}):
   with self.assertRaises(self.error):self.costs.collect(self.gen.crm,'2026-10-01','2026-10-31',lambda **kw:(_ for _ in ()).throw(AssertionError('network')))
 def test_meta_costs_require_correct_account_and_currency(self):
  self.setup_analytics();crm=self.gen.crm;key=self.costs.SYSTEM+':'+crm.store.scope+':'+(getattr(crm.store,'provider',None) or '-');profile={'main':{'platform':'META','account_id':'123','owner_id':crm.actor,'credential_env':'COMMERCIAL_ANALYTICS_SECRET_META','developer_token_env':'','api_version':''}};env={'COMMERCIAL_ANALYTICS_PROVIDER_READ_ENABLED':'1','COMMERCIAL_ANALYTICS_ACCOUNTS':json.dumps({key:profile}),'COMMERCIAL_ANALYTICS_SECRET_META':'synthetic-read-token-123'};seen=[]
  def send(req):
   seen.append(req);self.assertEqual(req.url.host,'graph.facebook.com');self.assertEqual(req.method,'GET')
   return httpx.Response(200,json={'id':'act_123','account_id':'123','currency':'COP'} if not req.url.path.endswith('insights') else {'data':[{'account_id':'123','campaign_id':'42','date_start':'2026-10-01','date_stop':'2026-10-01','spend':'12.340001','impressions':'20','clicks':'2'}]})
  with patch.dict(os.environ,env):
   r=self.costs.collect(crm,'2026-10-01','2026-10-31',lambda **kw:httpx.Client(transport=httpx.MockTransport(send),**kw));self.assertEqual(r['rows'][0]['cost_cop'],'12.340001');self.assertEqual(len(seen),2)
   with self.assertRaises(self.error):self.costs.collect(crm,'2026-10-01','2026-10-31',lambda **kw:httpx.Client(transport=httpx.MockTransport(lambda req:httpx.Response(200,json={'id':'act_123','account_id':'123','currency':'USD'})),**kw))
 def test_google_and_tiktok_cost_protocols_keep_exact_precision(self):
  self.setup_analytics();crm=self.gen.crm;key=self.costs.SYSTEM+':'+crm.store.scope+':'+(getattr(crm.store,'provider',None) or '-')
  for platform in ('TIKTOK','GOOGLE_YOUTUBE'):
   profile={'main':{'platform':platform,'account_id':'123','owner_id':crm.actor,'credential_env':'COMMERCIAL_ANALYTICS_SECRET_TEST','developer_token_env':'COMMERCIAL_ANALYTICS_SECRET_DEV','api_version':'v20'}};env={'COMMERCIAL_ANALYTICS_PROVIDER_READ_ENABLED':'1','COMMERCIAL_ANALYTICS_ACCOUNTS':json.dumps({key:profile}),'COMMERCIAL_ANALYTICS_SECRET_TEST':'synthetic-read-token-123','COMMERCIAL_ANALYTICS_SECRET_DEV':'synthetic-developer-123'}
   def send(req):
    if platform=='GOOGLE_YOUTUBE':
     self.assertEqual(req.url.host,'googleads.googleapis.com');self.assertEqual(req.method,'POST');query=json.loads(req.content)['query']
     return httpx.Response(200,json={'results':[{'customer':{'id':'123','currencyCode':'COP'}}]} if 'FROM customer' in query else {'results':[{'campaign':{'id':'42'},'segments':{'date':'2026-10-01'},'metrics':{'costMicros':'12340001','impressions':'20','clicks':'2'}}]})
    self.assertEqual(req.url.host,'business-api.tiktok.com');self.assertEqual(req.method,'GET')
    return httpx.Response(200,json={'code':0,'data':{'list':[{'advertiser_id':'123','currency':'COP'}]} if 'advertiser/info' in req.url.path else {'list':[{'dimensions':{'campaign_id':'42','stat_time_day':'2026-10-01'},'metrics':{'spend':'12.340001','impressions':'20','clicks':'2'}}],'page_info':{'total_page':1,'total_number':1}}})
   with patch.dict(os.environ,env):
    r=self.costs.collect(crm,'2026-10-01','2026-10-31',lambda **kw:httpx.Client(transport=httpx.MockTransport(send),**kw));self.assertEqual(r['rows'][0]['cost_cop'],'12.340001');self.assertFalse(r['real_provider_qualified'])
 def test_remote_income_requires_fresh_bound_reader(self):
  self.setup_analytics()
  if self.costs.SYSTEM!='sga-cd':return
  sale={'id':str(uuid.uuid4()),'status':'CONFIRMED','source':{'content':{'contact_id':str(uuid.uuid4())}}}
  with self.assertRaises(self.error):self.sources.income(self.gen.crm,[sale])
  r=self.sources.income(self.gen.crm,[sale],lambda d:{'scope':'VERIFIED_COMMERCIAL_MODULE_JOURNALS_ONLY','rows':[{'sale_id':'native','contact_id':'native','date':'2026-10-01','amount':'5.00','kind':'SALE','journal_hash':'a'*64}],'proof':[]});self.assertEqual(r['rows'][0]['contact_id'],sale['source']['content']['contact_id']);self.assertEqual(r['rows'][0]['sale_id'],sale['id'])
 def test_current_crm_and_real_capture_adapter_are_available_for_empty_scope(self):
  self.setup_analytics();people=self.sources.contacts(self.gen.crm);self.assertIsInstance(people,list);result=self.sources.attribution(self.gen.crm,people);self.assertIn('groups',result);self.assertFalse(result['causal_attribution_claimed'])
 def test_ltv_requires_reviewed_policy_and_never_substitutes_arpu(self):
  self.setup_analytics();ltv=importlib.import_module(self.module_path+'.analytics_ltv');key=self.costs.SYSTEM+':'+self.gen.crm.store.scope+':'+(getattr(self.gen.crm.store,'provider',None) or '-');econ={'rows':[{'date':'2026-10-01','amount':'310.00','contact_id':'sample','kind':'SALE'}],'scope':'VERIFIED_COMMERCIAL_MODULE_JOURNALS_ONLY'}
  with patch.dict(os.environ,{'COMMERCIAL_ANALYTICS_LTV_POLICIES':'{}'}):self.assertIsNone(ltv.estimate(self.gen.crm,econ,'2026-10-01','2026-10-31',self.now)['value'])
  policy={'version':'lab-1','owner_ref':self.gen.crm.actor,'reviewer_ref':'synthetic-reviewer','support_digest':'a'*64,'valid_from':'2026-11-01T00:00:00+00:00','valid_until':'2026-12-01T00:00:00+00:00','gross_margin_fraction':'0.5','monthly_churn_fraction':'0.1','horizon_months':2,'justification':'Supuestos de laboratorio declarados, no aceptación productiva'}
  with patch.dict(os.environ,{'COMMERCIAL_ANALYTICS_LTV_POLICIES':json.dumps({key:policy})}):
   result=ltv.estimate(self.gen.crm,econ,'2026-10-01','2026-10-31',self.now);self.assertEqual(result['value'],'285.00');self.assertEqual(result['monthly_observed_revenue_per_customer_cop'],'300.00');self.assertEqual(result['state'],'DECLARED_ASSUMPTION_SCENARIO');self.assertFalse(result['calibrated_for_production']);self.assertFalse(result['support_authenticity_verified'])
  policy['monthly_churn_fraction']='0'
  with patch.dict(os.environ,{'COMMERCIAL_ANALYTICS_LTV_POLICIES':json.dumps({key:policy})}):
   with self.assertRaises(self.error):ltv.estimate(self.gen.crm,econ,'2026-10-01','2026-10-31',self.now)
 def test_meta_pagination_never_follows_provider_supplied_url(self):
  self.setup_analytics();crm=self.gen.crm;key=self.costs.SYSTEM+':'+crm.store.scope+':'+(getattr(crm.store,'provider',None) or '-');profile={'main':{'platform':'META','account_id':'123','owner_id':crm.actor,'credential_env':'COMMERCIAL_ANALYTICS_SECRET_META','developer_token_env':'','api_version':''}};env={'COMMERCIAL_ANALYTICS_PROVIDER_READ_ENABLED':'1','COMMERCIAL_ANALYTICS_ACCOUNTS':json.dumps({key:profile}),'COMMERCIAL_ANALYTICS_SECRET_META':'synthetic-read-token-123'};seen=[]
  def send(req):
   self.assertEqual(req.url.host,'graph.facebook.com');seen.append(req)
   return httpx.Response(200,json={'id':'act_123','account_id':'123','currency':'COP'} if not req.url.path.endswith('insights') else {'data':[],'paging':{'next':'https://untrusted.invalid/steal','cursors':{'after':'same-cursor'}}})
  with patch.dict(os.environ,env):
   with self.assertRaises(self.error):self.costs.collect(crm,'2026-10-01','2026-10-31',lambda **kw:httpx.Client(transport=httpx.MockTransport(send),**kw))
  self.assertEqual(len(seen),3)
 def test_duplicate_provider_account_aliases_cannot_double_costs(self):
  self.setup_analytics();crm=self.gen.crm;key=self.costs.SYSTEM+':'+crm.store.scope+':'+(getattr(crm.store,'provider',None) or '-');p={'platform':'META','account_id':'123','owner_id':crm.actor,'credential_env':'COMMERCIAL_ANALYTICS_SECRET_META','developer_token_env':'','api_version':''};env={'COMMERCIAL_ANALYTICS_PROVIDER_READ_ENABLED':'1','COMMERCIAL_ANALYTICS_ACCOUNTS':json.dumps({key:{'first':p,'second':p}}),'COMMERCIAL_ANALYTICS_SECRET_META':'synthetic-read-token-123'}
  def send(req):return httpx.Response(200,json={'id':'act_123','account_id':'123','currency':'COP'} if not req.url.path.endswith('insights') else {'data':[]})
  with patch.dict(os.environ,env):
   with self.assertRaises(self.error):self.costs.collect(crm,'2026-10-01','2026-10-31',lambda **kw:httpx.Client(transport=httpx.MockTransport(send),**kw))
 def test_incomplete_tiktok_report_is_not_a_zero_cost_source(self):
  self.setup_analytics();crm=self.gen.crm;key=self.costs.SYSTEM+':'+crm.store.scope+':'+(getattr(crm.store,'provider',None) or '-');p={'platform':'TIKTOK','account_id':'123','owner_id':crm.actor,'credential_env':'COMMERCIAL_ANALYTICS_SECRET_TEST','developer_token_env':'','api_version':''};env={'COMMERCIAL_ANALYTICS_PROVIDER_READ_ENABLED':'1','COMMERCIAL_ANALYTICS_ACCOUNTS':json.dumps({key:{'main':p}}),'COMMERCIAL_ANALYTICS_SECRET_TEST':'synthetic-read-token-123'}
  def send(req):return httpx.Response(200,json={'code':0,'data':{'list':[{'advertiser_id':'123','currency':'COP'}]} if 'advertiser/info' in req.url.path else {'list':[],'page_info':{'total_page':1,'total_number':1}}})
  with patch.dict(os.environ,env):
   with self.assertRaises(self.error):self.costs.collect(crm,'2026-10-01','2026-10-31',lambda **kw:httpx.Client(transport=httpx.MockTransport(send),**kw))
