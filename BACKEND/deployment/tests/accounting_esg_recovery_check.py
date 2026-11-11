"""Disposable sources: draft mapping, effective corrections, integrity and isolation."""
import runpy,unittest,copy
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_environmental_corrections_check.py')),run_name='esg_fixture')
from apps.prestadores.mi_negocio.gestion_contable.contabilidad import esg_reports as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.exceptions import PermissionDenied

class ESGChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['EnvironmentalCorrectionChecks']();self.base.setUp();self.day=self.base.case.day
  self.mapping={'framework':'GRI','version':'declared-2026','disclosure':'declared-emissions','boundary':'direct_combustion','applicability_reason':'Synthetic applicability for local test only','evidence_digest':'d'*64}
  self.args={'actor':self.base.owner,'provider_id':self.base.provider.pk,'since':self.day,'until':self.day,'mappings':[self.mapping]}
 def report(self,**kw):return engine.report(**{**self.args,**kw})
 def test_effective_correction_replaces_original_and_digest_is_stable(self):
  original=self.report();self.assertEqual(original['disclosures'][0]['value'],'12.345600')
  self.base.record(self.base.review());r=self.report();self.assertEqual(r['disclosures'][0]['value'],'24.691200');self.assertEqual(len(r['sources']),1);self.assertEqual(r['sources'][0]['revision'],1);self.assertEqual(self.report(),r);self.assertNotEqual(original['report_digest'],r['report_digest'])
 def test_no_writes_or_certification(self):
  count=OutboxEvent.objects.count();r=self.report();self.assertEqual(count,OutboxEvent.objects.count());self.assertFalse(r['esg_certified']);self.assertFalse(r['supports_independently_verified']);self.assertEqual(r['status'],'DRAFT_REQUIRES_PROFESSIONAL_REVIEW')
 def test_malformed_framework_or_boundary_is_domain_error(self):
  for key in ['framework','boundary']:
   for value in [[],{},None,True]:
    with self.assertRaises(AccountingError):self.report(mappings=[{**self.mapping,key:value}])
 def test_frameworks_must_be_explicit_and_unique(self):
  for mappings in [[],[self.mapping,self.mapping],[{**self.mapping,'framework':'CERTIFIED'}],[{**self.mapping,'evidence_digest':'x'}]]:
   with self.assertRaises(AccountingError):self.report(mappings=mappings)
 def test_missing_boundary_has_no_fabricated_data(self):
  r=self.report(mappings=[{**self.mapping,'boundary':'electricity_location_based'}]);self.assertFalse(r['disclosures'][0]['data_available']);self.assertEqual(r['unmapped_boundaries'],['direct_combustion'])
 def test_factor_tampering_blocks_report(self):
  row=OutboxEvent.objects.filter(event_type=engine.records.FACTOR,payload__company_id=str(self.base.company.pk)).get();row.payload['content']['source_digest']='f'*64;row.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.report()
 def test_foreign_owner_denied(self):
  with self.assertRaises(PermissionDenied):self.report(actor=self.base.case.case.other)
 def test_real_http_no_store_and_unknown_parameters(self):
  call=self.base.case.case.call;payload={k:v for k,v in self.args.items() if k not in {'actor','provider_id'}}
  response=call('esg_report','post',payload);self.assertEqual(response.status_code,200,response.data);self.assertIn('no-store',response['Cache-Control']);self.assertEqual(response.data['disclosures'][0]['value'],'12.345600')
  self.assertEqual(call('esg_report','post',{**payload,'certified':True}).status_code,400)
if __name__=='__main__':unittest.main()
