"""Actual corporate/ERP HTTP corrections preserve original observation and ledger."""
import unittest
import test_corporate_ledger_integration as integration
class CorporateEnvironmentalCorrectionTests(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 setUp=integration.DualLedgerIntegration.setUp
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def original(self):
  self.activities=[{'id':'correctable-route','date':self.day,'quantity':'100','unit':'vehicle_km','factor_id':'explicit-test-factor','passengers':4}]
  self.factors=[{'id':'explicit-test-factor','version':'test-v1','unit':'vehicle_km','kg_co2e_per_unit':'0.123456','valid_from':self.day[:4]+'-01-01','valid_until':self.day[:4]+'-12-31','source_digest':'a'*64,'geography':'CO','boundary':'direct_combustion'}]
  r=self.command('review_environmental',{'activities':self.activities,'factors':self.factors,'evidence_digest':'b'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text);self.original_review=r.json()['data']['review_id']
  r=self.command('record_environmental',{'review_id':self.original_review,'confirmed':True});self.assertEqual(r.status_code,200,r.text);self.observation=r.json()['data']['observation_id']
  return {'observation_id':self.observation,'expected_revision':0,'activities':[{**self.activities[0],'quantity':'200'}],'factors':self.factors,'evidence_digest':'c'*64,'reason_code':'QUANTITY_ERROR','confirmed':True}
 def test_actual_correction_retry_recovery_preserves_original(self):
  args=self.original();r=self.command('review_environmental_correction',args);self.assertEqual(r.status_code,200,r.text);review=r.json()['data']['review_id']
  record={'observation_id':self.observation,'review_id':review,'confirmed':False};self.assertEqual(self.command('record_environmental_correction',record).status_code,422);record['confirmed']=True
  r=self.command('record_environmental_correction',record);self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['data']['ledger_written']);self.assertTrue(self.command('record_environmental_correction',record).json()['data']['replayed'])
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/environmental_corrections',params={'observation_id':self.observation});self.assertEqual(state.status_code,200,state.text);s=state.json();self.assertEqual(s['revision'],1);self.assertEqual(s['original_assessment']['kg_co2e'],'12.345600');self.assertEqual(s['effective_assessment']['kg_co2e'],'24.691200');self.assertFalse(s['confirmations_restored'])
  old=self.client.get('/api/v1/workspace/corporate/accounting/sources/environmental_state',params={'review_id':self.original_review});self.assertEqual(old.status_code,200,old.text);self.assertEqual(old.json()['corrections']['effective_assessment'],s['effective_assessment'])
 def test_stale_review_and_cross_activity_rejected(self):
  args=self.original();a=self.command('review_environmental_correction',args).json()['data'];b=self.command('review_environmental_correction',{**args,'activities':[{**args['activities'][0],'quantity':'300'}]}).json()['data']
  self.assertEqual(self.command('record_environmental_correction',{'observation_id':self.observation,'review_id':a['review_id'],'confirmed':True}).status_code,200)
  self.assertEqual(self.command('record_environmental_correction',{'observation_id':self.observation,'review_id':b['review_id'],'confirmed':True}).status_code,409)
  self.assertEqual(self.command('review_environmental_correction',{**args,'expected_revision':1,'activities':[{**args['activities'][0],'id':'another-activity'}]}).status_code,409)
if __name__=='__main__':unittest.main()
