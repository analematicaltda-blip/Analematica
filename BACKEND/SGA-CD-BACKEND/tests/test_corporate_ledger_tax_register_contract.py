"""Do not forward inconsistent arithmetic or unexpected private fields upstream."""
import copy,unittest,uuid
from app.services.tax_register_contract import validate
class TaxRegisterContractChecks(unittest.TestCase):
 def setUp(self):
  company,account,document=[str(uuid.uuid4()) for _ in range(3)];self.args={'company_id':company,'account_id':account,'since':'2026-11-01','until':'2026-11-30'}
  row={'journal_id':str(uuid.uuid4()),'date':'2026-11-09','journal_hash':'a'*64,'is_reversal':False,'debit':'19.00','credit':'0.00','normal_movement':'19.00','tax_by_kind':{'INPUT_TAX':'19.00','OUTPUT_TAX':'0.00','WITHHOLDING':'0.00'},'unattributed_normal_movement':'0.00','classification':'REVIEWED_COMMERCIAL_TAX','document_id':document,'reservation_id':None}
  self.report={'schema':'sgacd-tax-register-v2','company_id':company,'tenant_id':company,'account_id':account,'account_code':'1355','account_type':'ASSET','normal_side':'DEBIT','since':self.args['since'],'until':self.args['until'],'currency':'COP','read_only':True,'posted_only':True,'valuation':'base_currency','debit':'19.00','credit':'0.00','normal_movement':'19.00','attributed_normal_movement':'19.00','tax_by_kind':copy.deepcopy(row['tax_by_kind']),'unattributed_normal_movement':'0.00','unattributed_journals':0,'lines':[row],'ledger_written':False,'dian_compared':False,'fiscal_accepted':False,'regulatory_verified':False,'scope':'SELECTED_ACCOUNT_MOVEMENTS_NOT_A_TAX_RETURN'}
 def check(self,r=None):return validate(self.report if r is None else r,**self.args)
 def test_valid_register_is_retained_without_mutation(self):
  before=copy.deepcopy(self.report);self.assertIs(self.check(),self.report);self.assertEqual(self.report,before)
 def test_unexpected_private_fields_are_refused(self):
  for target in [self.report,self.report['lines'][0]]:
   target['medical_document']='SYNTHETIC PRIVATE'
   with self.assertRaises(ValueError):self.check()
   del target['medical_document']
 def test_total_line_and_tax_arithmetic_cannot_disagree(self):
  for key,value in [('debit','20.00'),('normal_movement','1.00'),('attributed_normal_movement','1.00'),('unattributed_journals',1)]:
   r=copy.deepcopy(self.report);r[key]=value
   with self.assertRaises(ValueError):self.check(r)
  self.report['lines'][0]['tax_by_kind']['INPUT_TAX']='1.00'
  with self.assertRaises(ValueError):self.check()
 def test_binary_floats_and_negative_debits_are_refused(self):
  for amount in [19.0,True,'-19.00','NaN','19.001']:
   r=copy.deepcopy(self.report);r['lines'][0]['debit']=amount
   with self.assertRaises(ValueError):self.check(r)
 def test_company_account_and_financial_status_cannot_change(self):
  for key,value in [('company_id',str(uuid.uuid4())),('account_id',str(uuid.uuid4())),('fiscal_accepted',True),('normal_side','CREDIT'),('currency','USD')]:
   r=copy.deepcopy(self.report);r[key]=value
   with self.assertRaises(ValueError):self.check(r)
 def test_duplicate_journal_and_bad_dates_refused(self):
  r=copy.deepcopy(self.report);r['lines'].append(copy.deepcopy(r['lines'][0]))
  with self.assertRaises(ValueError):self.check(r)
  for day in ['2026-10-01','2026-11-09junk','2026-11-31']:
   r=copy.deepcopy(self.report);r['lines'][0]['date']=day
   with self.assertRaises(ValueError):self.check(r)
 def test_fabricated_attribution_and_source_identifiers_refused(self):
  for changes in [{'classification':'UNATTRIBUTED_REQUIRES_REVIEW','document_id':None},{'document_id':'bad-uuid'},{'reservation_id':str(uuid.uuid4())},{'classification':'DIAN_VERIFIED'}]:
   r=copy.deepcopy(self.report);r['lines'][0].update(changes)
   with self.assertRaises(ValueError):self.check(r)
 def test_unknown_tax_kind_is_not_accepted(self):
  self.report['tax_by_kind']['UNSUPPORTED']='1.00'
  with self.assertRaises(ValueError):self.check()
 def v3(self):
  report=copy.deepcopy(self.report);report['schema']='sgacd-tax-register-v3';line=report['lines'][0];line['policy_coverage']='ORIGINAL_VERSION_REFERENCED';line['policy_references']=[{'item_id':str(uuid.uuid4()),'policy_id':str(uuid.uuid4()),'code':'TAX_RULE','revision':1,'policy_digest':'a'*64,'valid_from':'2026-01-01','valid_until':'2026-12-31','evidence_digest':'b'*64,'tax_category':'TAXABLE','direction':'PURCHASE','economic_date':'2026-11-01','reference_basis':'ORIGINAL_DOCUMENT_POLICY_NOT_ADJUSTMENT_AMOUNT'}];return report
 def test_v3_policy_provenance_and_legacy_v2_are_accepted(self):self.check(self.v3());self.check()
 def test_v3_missing_duplicate_invalid_or_private_provenance_denied(self):
  for case in ['missing','duplicate','revision','validity','private','coverage']:
   report=self.v3();line=report['lines'][0];refs=line['policy_references']
   if case=='missing':del line['policy_references']
   if case=='duplicate':refs*=2
   if case=='revision':refs[0]['revision']=True
   if case=='validity':refs[0]['valid_until']='2026-01-01'
   if case=='private':refs[0]['private_document']='not allowed'
   if case=='coverage':line['policy_coverage']='NOT_CAPTURED_IN_SOURCE'
   with self.assertRaises(ValueError):self.check(report)
if __name__=='__main__':unittest.main()
