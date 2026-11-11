"""Multiple native purchase concepts, exact recovery and corporate conservation."""
import copy,runpy,sys,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_native_purchase_check.py')),run_name='concepts_fixture')
from apps.core_erp.accounting.models import Account,JournalEntry,LedgerEntry
from apps.core_erp.accounting import commercial_tax_posting as ledger
from apps.core_erp.accounting.tax_register import reconcile_tax_register
from apps.core_erp.accounting.exceptions import AccountingError
from apps.prestadores.mi_negocio.gestion_contable.compras import native_purchase as engine
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
from app.services.purchase_concepts_contract import validate as concepts
from app.services.native_purchase_contract import validate as boundary
class PurchaseConceptChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['NativePurchaseChecks']();self.base.setUp();self.case=self.base.case
  self.second=Account.plain_objects.create(tenant=self.base.company,chart_of_accounts=self.case.base.chart,code='510002',name='Synthetic second concept',type='EXPENSE')
  item=copy.deepcopy(self.case.fact['items'][0]);item['net']='60.00';other={**copy.deepcopy(item),'item_id':str(uuid.uuid4()),'net':'40.00','basis_account_id':str(self.second.pk)};self.items=[item,other]
  self.context={'tenant_id':str(self.base.company.pk),'provider_id':str(self.base.provider.pk)}
 def capture(self,**kw):return self.base.capture(**kw)
 def review(self,c,**kw):return self.base.review(c,selection=kw.pop('selection',self.items),**kw)
 def test_two_concepts_post_to_distinct_basis_and_preserve_exact_totals(self):
  c=self.capture();r=self.review(c);self.assertEqual(r['review_inputs']['selection'],self.items);concepts(r['review_inputs'],r['preview'],r['revision']);a=self.base.post(c,r)
  rows=LedgerEntry.plain_objects.filter(journal_entry_id=a['journal_id']);self.assertEqual(format(rows.get(account=self.case.expense).debit_amount,'.2f'),'60.00');self.assertEqual(format(rows.get(account=self.second).debit_amount,'.2f'),'40.00');self.assertEqual(r['preview']['totals']['settlement'],'116.50')
 def test_mixed_taxable_and_excluded_reconciles_only_applicable_tax(self):
  self.items[1].update(tax_category='EXCLUDED',tax_accounts={});c=self.capture(tax='11.40',gross='111.40');r=self.review(c);self.base.post(c,r);concepts(r['review_inputs'],r['preview'],r['revision']);report=reconcile_tax_register(self.base.company.pk,account_id=str(self.case.input_tax.pk),since=self.case.base.day.isoformat(),until=self.case.base.day.isoformat());self.assertEqual(report['tax_by_kind']['INPUT_TAX'],'11.40');ret=reconcile_tax_register(self.base.company.pk,account_id=str(self.case.retention.pk),since=self.case.base.day.isoformat(),until=self.case.base.day.isoformat());self.assertEqual(ret['tax_by_kind']['WITHHOLDING'],'1.50');self.assertEqual(r['preview']['totals']['settlement'],'109.90')
 def test_recovery_contains_exact_persisted_ids_mappings_and_revision(self):
  c=self.capture();r=self.review(c);state=self.base.state(c);self.assertEqual(state['review_inputs'],r['review_inputs']);self.assertFalse(state['confirmations_restored']);state['review_inputs']['selection'][0]['net']='999.00';self.assertEqual(self.base.state(c)['review_inputs']['selection'][0]['net'],'60.00')
 def test_revision_change_preserves_concepts_but_rejects_stale_post(self):
  c=self.capture();first=self.review(c);second=self.review(c,expected_revision=1);self.assertEqual(second['review_inputs']['revision'],2);self.assertEqual(second['review_inputs']['selection'],self.items)
  with self.assertRaises(AccountingError):self.base.post(c,first)
  self.assertTrue(self.base.post(c,second)['ledger_written'])
 def test_multiple_positive_input_tax_codes_are_preserved(self):
  policy=copy.deepcopy(self.case.policy);policy['code']='MULTI_INPUT';policy['components'].append({'code':'EXTRA','kind':'INPUT_TAX','rate_bps':500,'applies_to':['TAXABLE']});self.case.record_policy(policy)
  extra=Account.plain_objects.create(tenant=self.base.company,chart_of_accounts=self.case.base.chart,code='135002',name='Synthetic other input tax',type='ASSET')
  for item in self.items:item['policy_code']=policy['code'];item['tax_accounts']['EXTRA']=str(extra.pk)
  c=self.capture(tax='24.00',gross='124.00');r=self.review(c);concepts(r['review_inputs'],r['preview'],r['revision']);self.base.post(c,r);self.assertEqual(self.base.state(c)['review_inputs']['selection'],self.items)
 def test_full_reversal_preserves_both_original_concepts_and_offsets_tax(self):
  c=self.capture();r=self.review(c);a=self.base.post(c,r);reversed=self.base.reverse(c,self.base.reverse_review(c));self.assertNotEqual(a['journal_id'],reversed['journal_id']);self.assertEqual(self.base.state(c)['review_inputs']['selection'],self.items);report=reconcile_tax_register(self.base.company.pk,account_id=str(self.case.input_tax.pk),since=self.case.base.day.isoformat(),until=self.case.base.day.isoformat());self.assertEqual(report['tax_by_kind']['INPUT_TAX'],'0.00')
 def test_subtotal_mismatch_and_duplicate_concept_are_rejected(self):
  c=self.capture()
  for items in [[{**self.items[0],'net':'59.00'},self.items[1]],[self.items[0],{**self.items[1],'item_id':self.items[0]['item_id']}]]:
   with self.assertRaises(AccountingError):self.review(c,selection=items)
 def test_twenty_concepts_are_supported_and_twenty_one_are_refused(self):
  c=self.capture();items=[{**copy.deepcopy(self.items[0]),'item_id':str(uuid.uuid4()),'net':'5.00'} for _ in range(20)]
  # Per-concept half-up withholding changes the reviewed settlement, never invoice net/IVA.
  r=self.review(c,selection=items);self.assertEqual(len(r['review_inputs']['selection']),20);concepts(r['review_inputs'],r['preview'],r['revision'])
  with self.assertRaises(AccountingError):self.review(c,selection=items+[copy.deepcopy(items[0])],expected_revision=1)
 def test_corporate_contract_rejects_altered_concepts_tax_or_accounts(self):
  c=self.capture();r=self.review(c)
  for mutate in [lambda i,p:i['selection'][0].update(net='61.00'),lambda i,p:p['quotes'][0]['components'][0].update(amount='0.00'),lambda i,p:p['lines'][0].update(account_id=str(uuid.uuid4())),lambda i,p:i['selection'][1].update(item_id=i['selection'][0]['item_id']),lambda i,p:p['totals'].update(settlement='999.00')]:
   inputs=copy.deepcopy(r['review_inputs']);preview=copy.deepcopy(r['preview']);mutate(inputs,preview)
   with self.assertRaises(ValueError):concepts(inputs,preview,r['revision'])
 def test_corporate_boundary_matches_review_and_recovered_form(self):
  c=self.capture();r=self.review(c);payload={'invoice_id':c['invoice_id'],'selection':self.items,'settlement_account_id':str(self.case.payable.pk),'expected_revision':0}
  boundary('review_native_purchase',r,payload,self.context);state=self.base.state(c);boundary('native_purchase_state',state,{'invoice_id':c['invoice_id']},self.context)
  changed=copy.deepcopy(payload);changed['selection'][0]['policy_code']='OTHER'
  with self.assertRaises(ValueError):boundary('review_native_purchase',r,changed,self.context)
 def test_real_private_api_recovers_metadata_before_and_after_posting(self):
  c=self.capture();payload={'invoice_id':c['invoice_id'],'selection':self.items,'settlement_account_id':str(self.case.payable.pk),'economic_fact':'GOODS_OR_SERVICES_RECEIVED','evidence_digest':'c'*64,'expected_revision':0,'confirmed':True};r=self.base.call('review_native_purchase',payload);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['review_inputs']['selection'],self.items)
  a=self.base.call('post_native_purchase',{'invoice_id':c['invoice_id'],'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(a.status_code,200,a.data);state=self.base.call('native_purchase_state',{'invoice_id':c['invoice_id']});self.assertEqual(state.status_code,200,state.data);self.assertIn('no-store',state['Cache-Control']);self.assertEqual(state.data['review_inputs']['selection'],self.items)
if __name__=='__main__':unittest.main()
