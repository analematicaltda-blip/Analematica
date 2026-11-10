"""Real dual API environmental estimate; explicitly synthetic factor."""
import unittest
import test_corporate_ledger_integration as integration
class CorporateEnvironmentalTests(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 setUp=integration.DualLedgerIntegration.setUp
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def test_explicit_factor_same_estimate_both_apis_no_accounting_write(self):
  payload={'activities':[{'id':'synthetic-route','date':'2026-11-09','quantity':'100','unit':'vehicle_km','factor_id':'synthetic-factor','passengers':4}],'factors':[{'id':'synthetic-factor','version':'test-v1','unit':'vehicle_km','kg_co2e_per_unit':'0.123456','valid_from':'2026-01-01','valid_until':'2026-12-31','source_digest':'a'*64,'geography':'CO','boundary':'direct_combustion'}]}
  r=self.command('estimate_environmental',payload);self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];self.assertEqual(data['kg_co2e'],'12.345600');self.assertFalse(data['ledger_written']);self.assertFalse(data['liability_recognized']);self.assertEqual(self.command('estimate_environmental',payload).json()['data'],data)
  session=self.unwrap(self.erp.get('/api/v1/erp-session/').json())
  direct=self.unwrap(self.erp.post(integration.bridge.BASE+'estimar-impacto-ambiental/',params={'provider_id':self.provider},json=payload,headers={'X-CSRFToken':session['csrf_token'],'Origin':self.origin,'Referer':self.origin+'/'}).json());self.assertEqual(direct,data)
  payload['activities'][0]['unit']='litre_fuel';self.assertEqual(self.command('estimate_environmental',payload).status_code,409)
 def test_two_reviews_durable_state_and_duplicate_activity_rejection(self):
  payload={'activities':[{'id':'durable-route','date':self.day,'quantity':'100','unit':'vehicle_km','factor_id':'durable-factor','passengers':4}],'factors':[{'id':'durable-factor','version':'test-v1','unit':'vehicle_km','kg_co2e_per_unit':'0.123456','valid_from':self.day[:4]+'-01-01','valid_until':self.day[:4]+'-12-31','source_digest':'a'*64,'geography':'CO','boundary':'direct_combustion'}],'evidence_digest':'b'*64,'confirmed':True}
  r=self.command('review_environmental',payload);self.assertEqual(r.status_code,200,r.text);review=r.json()['data']['review_id'];self.assertEqual(self.command('record_environmental',{'review_id':review,'confirmed':False}).status_code,422)
  record=self.command('record_environmental',{'review_id':review,'confirmed':True});self.assertEqual(record.status_code,200,record.text);self.assertFalse(record.json()['data']['ledger_written']);self.assertTrue(self.command('record_environmental',{'review_id':review,'confirmed':True}).json()['data']['replayed'])
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/environmental_state',params={'review_id':review});self.assertEqual(state.status_code,200,state.text);self.assertFalse(state.json()['confirmations_restored']);self.assertEqual(state.json()['applied']['observation_id'],record.json()['data']['observation_id']);self.assertIn('no-store',state.headers['cache-control'])
  direct=self.unwrap(self.erp.get(integration.bridge.BASE+'estado-medicion-ambiental/',params={'provider_id':self.provider,'review_id':review}).json());self.assertEqual(direct,state.json())
  changed=self.command('review_environmental',{**payload,'evidence_digest':'c'*64});self.assertEqual(changed.status_code,200,changed.text);self.assertEqual(self.command('record_environmental',{'review_id':changed.json()['data']['review_id'],'confirmed':True}).status_code,409)
 def test_esg_evidence_report_uses_recorded_sources_without_certifying(self):
  from datetime import datetime,timezone
  payload={'activities':[{'id':'esg-http-route','date':self.day,'quantity':'100','unit':'vehicle_km','factor_id':'esg-http-factor','passengers':None}],'factors':[{'id':'esg-http-factor','version':'synthetic-v1','unit':'vehicle_km','kg_co2e_per_unit':'0.1','valid_from':self.day,'valid_until':self.day,'source_digest':'a'*64,'geography':'CO','boundary':'direct_combustion'}],'evidence_digest':'b'*64,'confirmed':True}
  r=self.command('review_environmental',payload);self.assertEqual(r.status_code,200,r.text);r=self.command('record_environmental',{'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  args={'since':self.day,'until':self.day,'as_of':datetime.now(timezone.utc).isoformat(),'mappings':{}};r=self.command('esg_report',args);self.assertEqual(r.status_code,200,r.text);d=r.json()['data'];self.assertEqual(d['totals_by_boundary'],{'direct_combustion':'10.000000'});self.assertEqual(d['unmapped_count'],1);self.assertFalse(d['esg_certified']);self.assertFalse(d['ledger_written']);self.assertEqual(self.command('esg_report',args).json()['data'],d);self.assertEqual(self.command('esg_report',{**args,'company_id':'forbidden'}).status_code,422)
if __name__=='__main__':unittest.main()
