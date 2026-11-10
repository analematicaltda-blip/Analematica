"""Reject false success, restored authorizations and changed ESG mappings."""
import sys,unittest,uuid,hashlib,json,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.services.recovery_contract import validate
class RecoveryContractChecks(unittest.TestCase):
 def setUp(self):self.context={'tenant_id':str(uuid.uuid4())}
 def test_foreign_purchase_or_restored_authorization_rejected(self):
  data={'company_id':self.context['tenant_id'],'invoice_id':1,'read_only':True,'confirmations_restored':False}
  validate('purchase_history',data,{'invoice_id':1},self.context)
  for change in [{'company_id':str(uuid.uuid4())},{'invoice_id':2},{'confirmations_restored':True}]:
   with self.assertRaises(ValueError):validate('purchase_history',{**data,**change},{'invoice_id':1},self.context)
 def test_partial_bank_group_cannot_claim_completeness(self):
  data={'company_id':self.context['tenant_id'],'ledger_written':False,'bank_verified':False,'money_transferred':False,'reconciliation_id':str(uuid.uuid4()),'review_id':str(uuid.uuid4()),'fully_reconciled':False,'associations_confirmed':True,'coverage':{'unresolved_rows':1}}
  validate('confirm_bank_groups',data,{'review_id':data['review_id']},self.context)
  for change in [{'fully_reconciled':True},{'money_transferred':True},{'bank_verified':True}]:
   with self.assertRaises(ValueError):validate('confirm_bank_groups',{**data,**change},{'review_id':data['review_id']},self.context)
 def test_esg_digest_mapping_and_noncertification_are_verified(self):
  mapping={'framework':'GRI','version':'declared','disclosure':'declared','boundary':'direct_combustion','applicability_reason':'Synthetic','evidence_digest':'a'*64}
  data={'company_id':self.context['tenant_id'],'schema':'sgacd-esg-draft-v1','since':'2026-11-01','until':'2026-11-10','read_only':True,'esg_certified':False,'supports_independently_verified':False,'applicability_independently_verified':False,'ledger_written':False,'money_transferred':False,'disclosures':[mapping]}
  data['report_digest']=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest();payload={'since':data['since'],'until':data['until'],'mappings':[mapping]};validate('esg_report',data,payload,self.context)
  for change in [{'esg_certified':True},{'report_digest':'f'*64},{'supports_independently_verified':True}]:
   with self.assertRaises(ValueError):validate('esg_report',{**data,**change},payload,self.context)
 def test_purchase_return_cannot_claim_payment(self):
  data={'company_id':self.context['tenant_id'],'journal_id':str(uuid.uuid4()),'ledger_written':True,'money_transferred':False};validate('confirm_purchase_return',data,{},self.context)
  with self.assertRaises(ValueError):validate('confirm_purchase_return',{**data,'money_transferred':True},{},self.context)
if __name__=='__main__':unittest.main()
