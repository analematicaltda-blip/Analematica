"""Explicit synthetic factors, no external claims or financial writes."""
import copy,runpy,unittest
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='environmental_fixture')
from apps.core_erp.accounting.environmental import estimate
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent

class EnvironmentalChecks(unittest.TestCase):
 def setUp(self):
  self.factor={'id':'fixture-diesel','version':'synthetic-v1','unit':'vehicle_km','kg_co2e_per_unit':'0.123456','valid_from':'2026-01-01','valid_until':'2026-12-31','source_digest':'a'*64,'geography':'CO','boundary':'direct_combustion'}
  self.activity={'id':'route-1','date':'2026-11-09','quantity':'100','unit':'vehicle_km','factor_id':'fixture-diesel','passengers':4}
 def estimate(self,**extra):return estimate(**{'company_id':'company-a','activities':[self.activity],'factors':[self.factor],**extra})
 def test_exact_total_and_allocation_no_financial_write(self):
  before=(JournalEntry.plain_objects.count(),OutboxEvent.objects.count());r=self.estimate();self.assertEqual(r['kg_co2e'],'12.345600');self.assertEqual(r['items'][0]['kg_co2e_per_passenger'],'3.086400');self.assertEqual(before,(JournalEntry.plain_objects.count(),OutboxEvent.objects.count()))
  for key in ['ledger_written','money_transferred','liability_recognized','carbon_credit_issued','esg_certified','factor_sources_independently_verified']:self.assertIs(r[key],False)
 def test_zero_is_explicit_not_missing(self):
  self.activity['quantity']='0';self.assertEqual(self.estimate()['kg_co2e'],'0.000000')
 def test_factor_dates_and_unit_enforced(self):
  for key,value in [('date','2027-01-01'),('date','20260101'),('unit','litre_fuel')]:
   with self.subTest(key=key,value=value):
    a={**self.activity,key:value}
    with self.assertRaises(AccountingError):self.estimate(activities=[a])
 def test_decimal_rejects_float_negative_nan_exponent_and_oversize(self):
  for value in [0.1,True,None,'-1','NaN','Infinity','1e3','01','0.0000001','1000000001','1'*100]:
   with self.subTest(value=value):
    with self.assertRaises(AccountingError):self.estimate(activities=[{**self.activity,'quantity':value}])
 def test_invalid_factor_amounts_also_rejected(self):
  for value in [1,'-1','NaN','1e9']:
   with self.assertRaises(AccountingError):self.estimate(factors=[{**self.factor,'kg_co2e_per_unit':value}])
 def test_missing_evidence_and_validity(self):
  for key,value in [('source_digest',''),('source_digest','A'*64),('valid_until','2025-01-01'),('boundary','unknown'),('geography','https://external.invalid'),('unit',[])]:
   with self.subTest(key=key):
    with self.assertRaises(AccountingError):self.estimate(factors=[{**self.factor,key:value}])
 def test_duplicate_activity_and_factor_rejected(self):
  with self.assertRaises(AccountingError):self.estimate(activities=[self.activity,self.activity])
  with self.assertRaises(AccountingError):self.estimate(factors=[self.factor,self.factor])
 def test_missing_and_unused_factor_rejected(self):
  with self.assertRaises(AccountingError):self.estimate(activities=[{**self.activity,'factor_id':'missing'}])
  with self.assertRaises(AccountingError):self.estimate(factors=[self.factor,{**self.factor,'id':'unused'}])
 def test_passenger_km_never_multiplied_or_divided_twice(self):
  self.factor['unit']=self.activity['unit']='passenger_km';self.activity['passengers']=None;self.assertEqual(self.estimate()['kg_co2e'],'12.345600');self.assertIsNone(self.estimate()['items'][0]['kg_co2e_per_passenger'])
  self.activity['passengers']=4
  with self.assertRaises(AccountingError):self.estimate()
 def test_passenger_count_must_be_positive_exact_integer(self):
  for value in [True,0,-1,1.5,'4',10001]:
   with self.assertRaises(AccountingError):self.estimate(activities=[{**self.activity,'passengers':value}])
 def test_incompatible_boundaries_no_combined_total(self):
  f={**self.factor,'id':'lifecycle','boundary':'lifecycle'};a={**self.activity,'id':'route-2','factor_id':'lifecycle'};r=self.estimate(factors=[self.factor,f],activities=[self.activity,a]);self.assertIsNone(r['kg_co2e']);self.assertEqual(r['unavailable_reason'],'INCOMPATIBLE_SYSTEM_BOUNDARIES');self.assertEqual(len(r['totals_by_boundary']),2)
 def test_aggregate_rounds_once_not_each_activity(self):
  self.factor['kg_co2e_per_unit']='0.000001';self.activity['quantity']='0.4';r=self.estimate(activities=[self.activity,{**self.activity,'id':'route-2'}]);self.assertEqual(r['kg_co2e'],'0.000001');self.assertEqual(r['items'][0]['kg_co2e'],'0.0000004')
 def test_digest_stable_order_sensitive_to_version_company_quantity(self):
  a={**self.activity,'id':'route-2'};r=self.estimate(activities=[self.activity,a]);self.assertEqual(r['assessment_digest'],self.estimate(activities=[a,self.activity])['assessment_digest'])
  for kwargs in [{'company_id':'company-b'},{'factors':[{**self.factor,'version':'synthetic-v2'}]},{'activities':[{**self.activity,'quantity':'101'}]}]:self.assertNotEqual(self.estimate()['assessment_digest'],self.estimate(**kwargs)['assessment_digest'])
 def test_strict_fields_and_bounds(self):
  for extra in [{'activities':[]},{'factors':[]},{'activities':[self.activity]*31},{'factors':[self.factor]*11},{'activities':[{**self.activity,'price':'100'}]},{'factors':[{**self.factor,'certified':True}]}]:
   with self.assertRaises(AccountingError):self.estimate(**extra)
 def test_inputs_not_mutated(self):
  before=copy.deepcopy((self.activity,self.factor));self.estimate();self.assertEqual(before,(self.activity,self.factor))
 def test_real_owner_api_and_foreign_denial(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  case=fixture['AdapterTests']();case.setUp()
  def call(data,provider=None):
   request=APIRequestFactory().post('/fixture/?provider_id='+str(provider or case.provider.pk),data,format='json');force_authenticate(request,user=case.user);return PlanCuentaViewSet.as_view({'post':'environmental_estimate'})(request)
  data={'activities':[self.activity],'factors':[self.factor]};r=call(data);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['company_id'],str(case.tenant.pk));self.assertIn('no-store',r['Cache-Control']);self.assertEqual(r.data['kg_co2e'],'12.345600')
  self.assertEqual(call(data,'00000000-0000-0000-0000-000000000001').status_code,403)
  self.assertEqual(call({**data,'company_id':'other'}).status_code,400)
if __name__=='__main__':unittest.main()
