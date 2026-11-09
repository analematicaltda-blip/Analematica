"""Explicit tax/withholding policy versions and exact previews, not statutory acceptance."""
import runpy,unittest,copy
from pathlib import Path
from decimal import localcontext
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='tax_policy_fixture')
from apps.core_erp.accounting import tax_policies as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class TaxPolicyTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['RecognitionTests']();self.case.setUp();self.company=self.case.case.tenant;self.actor=self.case.case.actor
  self.policy={'code':'OWNER_REVIEWED','jurisdiction':'CO','currency':'COP','valid_from':'2026-01-01','valid_until':'2026-06-30','rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'DECLARED_IVA','kind':'OUTPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']},{'code':'DECLARED_WITHHOLDING','kind':'WITHHOLDING','rate_bps':250,'applies_to':['TAXABLE','EXEMPT','EXCLUDED']}]}
 def review(self,**extra):return engine.review_policy(self.company.pk,**{'actor':self.actor,'policy':self.policy,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True,**extra})
 def record(self,review,**extra):return engine.record_policy(self.company.pk,**{'actor':self.actor,'review_id':review['review_id'],'confirmed':True,**extra})
 def quote(self,**extra):return engine.quote_policy(self.company.pk,**{'code':self.policy['code'],'revision':1,'economic_date':'2026-03-01','net':'100.00','tax_category':'TAXABLE','direction':'SALE',**extra})
 def test_two_confirmations_and_replay_no_posting(self):
  review=self.review()
  with self.assertRaises(AccountingError):self.record(review,confirmed=False)
  a=self.record(review);b=self.record(review);self.assertEqual(a['policy_id'],b['policy_id']);self.assertTrue(b['replayed']);self.assertFalse(a['regulatory_verified']);self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_exact_tax_withholding_and_credit_note(self):
  self.record(self.review());r=self.quote();self.assertEqual((r['output_tax'],r['withholding'],r['gross'],r['payable']),('19.00','2.50','119.00','116.50'));self.assertFalse(r['fiscal_document_created'])
  credit=self.quote(direction='CREDIT_NOTE');self.assertEqual(credit['payable'],'-116.50');self.assertEqual(credit['output_tax'],'-19.00')
 def test_exempt_excluded_are_not_charged_output_tax(self):
  self.record(self.review())
  for category in ('EXEMPT','EXCLUDED'):
   r=self.quote(tax_category=category);self.assertEqual(r['output_tax'],'0.00');self.assertEqual(r['payable'],'97.50')
 def test_successive_versions_history_and_overlap_rejection(self):
  self.record(self.review());second=copy.deepcopy(self.policy);second.update(valid_from='2026-07-01',valid_until='2026-12-31');second['components'][0]['rate_bps']=1800
  self.record(self.review(policy=second,expected_revision=1));self.assertEqual(self.quote(revision=2,economic_date='2026-08-01')['output_tax'],'18.00');self.assertEqual(self.quote()['output_tax'],'19.00')
  self.assertEqual([r['revision'] for r in engine.policy_history(self.company.pk,code=self.policy['code'])['items']],[2,1])
  with self.assertRaises(AccountingError):self.record(self.review(expected_revision=2))
 def test_stale_concurrent_review_cannot_overwrite_recorded_version(self):
  one=self.review();two=self.review(evidence_digest='b'*64);self.record(one)
  with self.assertRaises(AccountingError):self.record(two)
 def test_exact_rounding_ignores_global_decimal_precision(self):
  self.record(self.review())
  with localcontext() as ctx:
   ctx.prec=3;r=self.quote(net='999999999999.99')
  self.assertEqual(r['output_tax'],'190000000000.00')
 def test_bad_rates_categories_dates_and_missing_policy_rejected(self):
  with self.assertRaises(AccountingError):self.quote()
  for rate in (True,19.0,-1,10001):
   invalid=copy.deepcopy(self.policy);invalid['components'][0]['rate_bps']=rate
   with self.assertRaises(AccountingError):self.review(policy=invalid)
  invalid=copy.deepcopy(self.policy);invalid['components'][0]['applies_to']=['EXCLUDED']
  with self.assertRaises(AccountingError):self.review(policy=invalid)
  self.record(self.review())
  with self.assertRaises(AccountingError):self.quote(economic_date='2027-01-01')
 def test_real_api_review_record_and_quote(self):
  def call(action,data):
   request=APIRequestFactory().post('/fixture/?provider_id='+str(self.case.case.provider.pk),data,format='json');force_authenticate(request,user=self.actor)
   return PlanCuentaViewSet.as_view({'post':action})(request)
  r=call('review_tax_policy',{'policy':self.policy,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True});self.assertEqual(r.status_code,200,r.data)
  self.assertEqual(call('record_tax_policy',{'review_id':r.data['review_id'],'confirmed':True}).status_code,200)
  r=call('quote_tax_policy',{'code':self.policy['code'],'revision':1,'economic_date':'2026-03-01','net':'100.00','tax_category':'TAXABLE','direction':'SALE'});self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['payable'],'116.50');self.assertIn('no-store',r['Cache-Control'])
if __name__=='__main__':unittest.main()
