"""ACC008 corporate API -> real authenticated ERP HTTP; synthetic stores only."""
import unittest,os,uuid,copy
from unittest.mock import patch
import test_corporate_ledger_integration as base
from app.services.invoice_source_contract import validate
class ACC008HTTP(unittest.TestCase):
 login=base.DualLedgerIntegration.login
 command=base.DualLedgerIntegration.command
 tearDown=base.DualLedgerIntegration.tearDown
 def setUp(self):
  env=patch.dict(os.environ,{'ACC008_CRM_FIXTURE':'1'});env.start();self.addCleanup(env.stop)
  base.DualLedgerIntegration.setUp(self)
 def review_payload(self,source,key):return {key:source,'items':[{'item_id':str(uuid.uuid4()),'net':'100.00','tax':'0.00','tax_category':'EXCLUDED','policy_reference':'synthetic-reviewed:1'}],'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True}
 def check_flags(self,data):
  for key in ['ledger_written','money_transferred','payment_verified','published','fiscal_accepted']:self.assertIs(data[key],False)
 def test_crm_request_and_replay_through_both_real_backends(self):
  body=self.review_payload(self.credentials['crm_opportunity_id'],'opportunity_id')
  review=self.command('review_crm_invoice',body);self.assertEqual(review.status_code,200,review.text);self.check_flags(review.json()['data'])
  req={'opportunity_id':body['opportunity_id'],'review_id':review.json()['data']['review_id'],'confirmed':True}
  first=self.command('request_crm_invoice',req);self.assertEqual(first.status_code,200,first.text);second=self.command('request_crm_invoice',req);self.assertEqual(second.status_code,200,second.text)
  self.assertFalse(first.json()['data']['replayed']);self.assertTrue(second.json()['data']['replayed']);self.assertEqual(first.json()['data']['outbox_id'],second.json()['data']['outbox_id']);self.check_flags(first.json()['data'])
  report=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':self.day});self.assertEqual(report.status_code,200,report.text);self.assertEqual(report.json()['data']['total_debit'],'15.00')
 def test_reservation_review_and_request_are_not_payment_or_fiscal_receipt(self):
  body=self.review_payload(self.credentials['reservation_id'],'reservation_id')
  review=self.command('review_reservation_invoice',body);self.assertEqual(review.status_code,200,review.text)
  result=self.command('request_reservation_invoice',{'reservation_id':body['reservation_id'],'review_id':review.json()['data']['review_id'],'confirmed':True});self.assertEqual(result.status_code,200,result.text);self.check_flags(result.json()['data']);self.assertEqual(result.json()['data']['status'],'REQUEST_ONLY')
 def test_corporate_context_and_second_confirmation_cannot_be_supplied_by_caller(self):
  body=self.review_payload(self.credentials['crm_opportunity_id'],'opportunity_id')
  self.assertEqual(self.command('review_crm_invoice',{**body,'company_id':str(uuid.uuid4())}).status_code,422)
  review=self.command('review_crm_invoice',body);self.assertEqual(review.status_code,200,review.text)
  req={'opportunity_id':body['opportunity_id'],'review_id':review.json()['data']['review_id'],'confirmed':False}
  self.assertEqual(self.command('request_crm_invoice',req).status_code,422)
class ACC008ResponseContract(unittest.TestCase):
 def test_fiscal_and_payment_claims_and_foreign_source_are_rejected(self):
  company=str(uuid.uuid4());source=str(uuid.uuid4());review=str(uuid.uuid4());payload={'opportunity_id':source,'expected_revision':0};selected={'tenant_id':company}
  valid={'schema':'sgacd-commercial-request-result-v1','company_id':company,'source_id':source,'source_type':'crm_opportunity','review_id':review,'revision':1,'status':'REVIEWED','request_created':False,**{key:False for key in ['ledger_written','fiscal_accepted','money_transferred','payment_verified','published']}}
  validate('review_crm_invoice',valid,payload,selected)
  for key,value in [('company_id',str(uuid.uuid4())),('source_id',str(uuid.uuid4())),('revision',True),('status','PAID'),('fiscal_accepted',True),('money_transferred',True),('payment_verified',True),('request_created',True)]:
   with self.subTest(key=key),self.assertRaises(ValueError):validate('review_crm_invoice',{**valid,key:value},payload,selected)

 def test_processed_queue_and_request_receipt_do_not_authorize_fiscal_claims(self):
  company=str(uuid.uuid4());source=str(uuid.uuid4());review=str(uuid.uuid4());payload={'opportunity_id':source,'review_id':review};selected={'tenant_id':company}
  valid={'schema':'sgacd-commercial-request-result-v1','company_id':company,'source_id':source,'source_type':'crm_opportunity','review_id':review,'revision':1,'status':'REQUEST_ONLY','request_persisted':True,'replayed':True,'outbox_id':str(uuid.uuid4()),'outbox_status':'PROCESSED','published_by_this_call':False,'source_authority_verified':True,'legal_tax_policy_verified':False,**{key:False for key in ['ledger_written','fiscal_accepted','money_transferred','payment_verified','published']}}
  validate('request_crm_invoice',valid,payload,selected)
  for key,value in [('status','FISCAL_ACCEPTED'),('review_id',str(uuid.uuid4())),('outbox_status','DIAN_ACCEPTED'),('legal_tax_policy_verified',True),('published_by_this_call',True)]:
   with self.subTest(key=key),self.assertRaises(ValueError):validate('request_crm_invoice',{**valid,key:value},payload,selected)
