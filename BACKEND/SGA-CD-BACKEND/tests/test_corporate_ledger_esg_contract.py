import copy,hashlib,json,unittest,uuid
from decimal import localcontext,Inexact,Rounded
from app.services.esg_report_contract import validate,FLAGS
class ESGContractChecks(unittest.TestCase):
 def setUp(self):
  self.ctx={'tenant_id':str(uuid.uuid4()),'provider_id':str(uuid.uuid4())};self.args={'since':'2026-11-09','until':'2026-11-09','as_of':'2026-11-09T12:00:00+00:00','mappings':{}}
  self.row={'observation_id':str(uuid.uuid4()),'activity_id':'route','date':'2026-11-09','quantity':'100','activity_unit':'vehicle_km','factor_id':'f','factor_version':'synthetic-v1','factor_rate':'0.1','factor_source_digest':'a'*64,'boundary':'direct_combustion','kg_co2e':'10.0','revision':0,'known_at':'2026-11-09T11:00:00+00:00','proof_digest':'b'*64,'framework_mapping':None}
  self.data={'schema':'sgacd-esg-evidence-report-v1','company_id':self.ctx['tenant_id'],'provider_id':self.ctx['provider_id'],**self.args,'items':[self.row],'totals_by_boundary':{'direct_combustion':'10.000000'},'activity_count':1,'unmapped_count':1,'unit':'kg_co2e','read_only':True,**{k:False for k in FLAGS}}
 def seal(self):self.data['report_digest']=hashlib.sha256(json.dumps({k:v for k,v in self.data.items() if k!='report_digest'},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
 def check(self):self.seal();return validate(self.data,self.args,self.ctx)
 def test_valid_report(self):self.check()
 def test_optional_operational_source_and_support(self):
  self.row.update(source_reference=str(uuid.uuid4()),source_segment='OUTBOUND',activity_support_digest='c'*64);self.check()
  del self.row['source_segment']
  with self.assertRaises(ValueError):self.check()
 def test_exact_under_hostile_decimal_context(self):
  with localcontext() as ctx:
   ctx.prec=2;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True;self.check()
 def test_unknown_activity_fields_not_exported(self):
  self.row['plaintext_support']='private'
  with self.assertRaises(ValueError):self.check()
 def test_nested_framework_type_rejected(self):
  self.args['mappings']={'direct_combustion':{'framework':[],'version':'2016','reference':'305-1','evidence_digest':'a'*64}}
  with self.assertRaises(ValueError):self.check()
 def test_cannot_invent_certification_payment_or_liability(self):
  for key in FLAGS:
   self.data[key]=True
   with self.assertRaises(ValueError):self.check()
   self.data[key]=False
 def test_changed_totals_or_binary_float_rejected(self):
  self.data['totals_by_boundary']['direct_combustion']='20.000000'
  with self.assertRaises(ValueError):self.check()
  self.data['totals_by_boundary']['direct_combustion']='10.000000';self.row['factor_rate']=0.1
  with self.assertRaises(ValueError):self.check()
 def test_duplicate_activity_or_future_knowledge_rejected(self):
  self.data['items'].append(copy.deepcopy(self.row));self.data['activity_count']=2
  with self.assertRaises(ValueError):self.check()
  self.data['items']=[self.row];self.data['activity_count']=1;self.row['known_at']='2026-11-09T13:00:00+00:00'
  with self.assertRaises(ValueError):self.check()
 def test_foreign_company_and_private_fields_rejected(self):
  self.data['company_id']=str(uuid.uuid4())
  with self.assertRaises(ValueError):self.check()
  self.data['company_id']=self.ctx['tenant_id'];self.data['plaintext_document']='forbidden'
  with self.assertRaises(ValueError):self.check()
 def test_digest_cannot_be_ignored(self):
  self.seal();self.data['items'][0]['quantity']='200'
  with self.assertRaises(ValueError):validate(self.data,self.args,self.ctx)
