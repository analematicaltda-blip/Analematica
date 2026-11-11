"""Current CRM source retrieval over both real local backends; not DIAN issuance."""
import unittest
import test_corporate_ledger_acc008 as base
from app.services import corporate_ledger as bridge
class ACC009HTTP(unittest.TestCase):
 setUp=base.ACC008HTTP.setUp
 tearDown=base.ACC008HTTP.tearDown
 login=base.ACC008HTTP.login
 command=base.ACC008HTTP.command
 review_payload=base.ACC008HTTP.review_payload
 def test_crm_reviewed_source_matches_erp_without_fiscal_acceptance(self):
  body=self.review_payload(self.credentials['crm_opportunity_id'],'opportunity_id');review=self.command('review_crm_invoice',body);self.assertEqual(review.status_code,200,review.text)
  params={'opportunity_id':body['opportunity_id'],'review_id':review.json()['data']['review_id']}
  response=self.client.get('/api/v1/workspace/corporate/accounting/sources/crm_ubl_source',params=params);self.assertEqual(response.status_code,200,response.text)
  direct=self.erp.get(bridge.BASE+'fuente-borrador-ubl-crm/',params={**params,'provider_id':self.provider});self.assertEqual(direct.status_code,200,direct.text)
  self.assertEqual(response.json(),self.unwrap(direct.json()));self.assertEqual(response.json()['snapshot']['state'],'WON');self.assertTrue(response.json()['read_only']);self.assertFalse(response.json()['fiscal_accepted']);self.assertFalse(response.json()['identity_independently_verified']);self.assertNotIn('xml',response.json())
 def test_mixed_or_duplicate_source_context_is_rejected(self):
  url='/api/v1/workspace/corporate/accounting/sources/crm_ubl_source'
  self.assertEqual(self.client.get(url,params={'reservation_id':self.credentials['reservation_id'],'review_id':'x'}).status_code,422)
  self.assertEqual(self.client.get(url+'?opportunity_id=a&opportunity_id=b&review_id=x').status_code,422)
