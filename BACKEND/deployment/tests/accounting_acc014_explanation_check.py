"""Versioned tax explanations are not fiscal acceptance or new monetary effects."""
import runpy,unittest,copy
from pathlib import Path
from datetime import date,timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_tax_register_check.py')),run_name='acc014_fixture')
from apps.core_erp.accounting import tax_policies
from apps.core_erp.accounting.exceptions import AccountingError
class TaxExplanationChecks(unittest.TestCase):
 def setUp(self):self.base=fixture['TaxRegisterChecks']();self.base.setUp();self.addCleanup(self.base.doCleanups)
 def test_original_policy_version_evidence_and_validity_explained(self):
  self.base.post();r=self.base.report();self.assertEqual(r['schema'],'sgacd-tax-register-v3');row=r['lines'][0];self.assertEqual(row['policy_coverage'],'ORIGINAL_VERSION_REFERENCED');ref=row['policy_references'][0];self.assertEqual(ref['revision'],1);self.assertEqual(ref['code'],self.base.purchase.policy['code']);self.assertEqual(ref['direction'],'PURCHASE');self.assertEqual(ref['economic_date'],self.base.day);self.assertEqual(ref['reference_basis'],'ORIGINAL_DOCUMENT_POLICY_NOT_ADJUSTMENT_AMOUNT');self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'19.00');self.assertFalse(r['dian_compared'])
 def test_reversal_retains_original_policy_without_changing_tax(self):
  self.base.post();self.base.purchase.reverse(self.base.purchase.reversal_review());r=self.base.report();self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'0.00');self.assertEqual(r['lines'][0]['policy_references'],r['lines'][1]['policy_references'])
 def test_reservation_without_captured_policy_not_assumed_qualified(self):
  self.base.reservation();r=self.base.report(self.base.rec.tax);self.assertEqual(r['lines'][0]['policy_coverage'],'NOT_CAPTURED_IN_SOURCE');self.assertEqual(r['lines'][0]['policy_references'],[])
 def test_new_policy_revision_does_not_relabel_old_posting(self):
  self.base.post();p=copy.deepcopy(self.base.purchase.policy);p['components'][0]['rate_bps']=1800
  next_day=date.fromisoformat(p['valid_until'])+timedelta(days=1);p['valid_from']=next_day.isoformat();p['valid_until']=(next_day+timedelta(days=30)).isoformat()
  review=tax_policies.review_policy(self.base.company.pk,actor=self.base.owner,policy=p,evidence_digest='c'*64,expected_revision=1,confirmed=True)
  tax_policies.record_policy(self.base.company.pk,actor=self.base.owner,review_id=review['review_id'],confirmed=True)
  r=self.base.report();self.assertEqual(r['lines'][0]['policy_references'][0]['revision'],1);self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'19.00')
 def test_unhashable_policy_components_rejected_as_accounting_error(self):
  for field,value in [('kind',{}),('kind',[]),('applies_to',[{}]),('applies_to',[[]])]:
   p=copy.deepcopy(self.base.purchase.policy);p['components'][0][field]=value
   with self.assertRaises(AccountingError):tax_policies.normalize(p)
if __name__=='__main__':unittest.main(verbosity=2)
