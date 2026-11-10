"""ESG report derives effective measurements at explicit economic/knowledge cuts."""
import runpy,unittest,copy
from pathlib import Path
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_environmental_corrections_check.py')),run_name='esg_fixture')
from django.utils import timezone
from apps.prestadores.mi_negocio.gestion_contable.contabilidad import esg_reporting as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.exceptions import PermissionDenied
class ESGReportChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['EnvironmentalCorrectionChecks']();self.base.setUp();self.day=self.base.case.day
  self.args={'actor':self.base.owner,'provider_id':self.base.provider.pk,'since':self.day,'until':self.day,'as_of':timezone.now().isoformat(),'mappings':{}}
 def report(self,**kw):return engine.report(**{**self.args,**kw})
 def test_effective_report_does_not_double_count_corrections(self):
  before=self.report();self.base.record(self.base.review());after=self.report(as_of=timezone.now().isoformat());self.assertEqual(before['totals_by_boundary']['direct_combustion'],'12.345600');self.assertEqual(after['totals_by_boundary']['direct_combustion'],'24.691200');self.assertEqual(after['activity_count'],1);self.assertEqual(after['items'][0]['revision'],1)
 def test_knowledge_cut_keeps_original_after_later_correction(self):
  before=self.report();self.base.record(self.base.review());self.assertEqual(self.report(),before)
 def test_before_record_is_empty_not_invented_zero_coverage(self):
  root=OutboxEvent.objects.get(pk=self.base.observation);r=self.report(as_of=(root.created_at-timedelta(microseconds=1)).isoformat());self.assertEqual(r['items'],[]);self.assertEqual(r['totals_by_boundary'],{})
 def test_client_mapping_is_declared_not_certified(self):
  m={'direct_combustion':{'framework':'GRI','version':'2016','reference':'305-1','evidence_digest':'a'*64}};r=self.report(mappings=m);self.assertEqual(r['unmapped_count'],0);self.assertEqual(r['items'][0]['framework_mapping'],m['direct_combustion']);self.assertFalse(r['framework_applicability_verified']);self.assertFalse(r['esg_certified'])
 def test_unmapped_sources_are_visible(self):self.assertEqual(self.report()['unmapped_count'],1)
 def test_future_naive_or_excessive_period_rejected(self):
  for kw in [{'as_of':timezone.now().replace(tzinfo=None).isoformat()},{'as_of':(timezone.now()+timedelta(days=1)).isoformat()},{'since':'1900-01-01'},{'mappings':{'auto':'GRI'}}]:
   with self.assertRaises((AccountingError,ValueError)):self.report(**kw)
 def test_tampered_factor_claim_fails_closed(self):
  OutboxEvent.objects.filter(event_type=engine.records.FACTOR).delete()
  with self.assertRaises(AccountingError):self.report()
 def test_owner_scope_and_no_writes(self):
  with self.assertRaises(PermissionDenied):self.report(actor=self.base.case.case.other)
  count=OutboxEvent.objects.count();r=self.report();self.assertEqual(count,OutboxEvent.objects.count())
  for k in ['ledger_written','money_transferred','liability_recognized','carbon_credit_issued','esg_certified','sources_independently_verified','confirmations_restored']:self.assertIs(r[k],False)
 def test_incompatible_boundaries_are_reported_separately(self):
  c=self.base.case;r=c.review(activities=[{**c.activity,'id':'power-1','unit':'kwh','quantity':'2','factor_id':'power','passengers':None}],factors=[{**c.factor,'id':'power','unit':'kwh','boundary':'electricity_location_based','kg_co2e_per_unit':'0.1'}]);c.record(r);result=self.report(as_of=timezone.now().isoformat());self.assertEqual(result['totals_by_boundary'],{'direct_combustion':'12.345600','electricity_location_based':'0.200000'});self.assertNotIn('kg_co2e',result)
 def test_economic_cut_excludes_outside_activity(self):
  day=(timezone.localdate()-timedelta(days=1)).isoformat();self.assertEqual(self.report(since=day,until=day)['activity_count'],0)
 def test_real_api_contract_is_read_only_and_rejects_unknown_fields(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  def call(extra):
   payload={k:v for k,v in self.args.items() if k not in {'actor','provider_id'}};payload.update(extra);r=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),payload,format='json');force_authenticate(r,user=self.base.owner);return PlanCuentaViewSet.as_view({'post':'esg_report'})(r)
  r=call({});self.assertEqual(r.status_code,200,r.data);self.assertFalse(r.data['esg_certified']);self.assertEqual(call({'confirmed':True}).status_code,400)
 def test_changed_observation_envelope_cannot_be_reported(self):
  OutboxEvent.objects.filter(pk=self.base.observation).update(domain='foreign')
  with self.assertRaises(AccountingError):self.report()
if __name__=='__main__':unittest.main()
