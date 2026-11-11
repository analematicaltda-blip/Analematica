"""Concept capacities, cumulative original taxes, append-only corrections and audit."""
import copy,runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_purchase_concepts_check.py')),run_name='item_returns_fixture')
from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_item_returns as engine
from apps.prestadores.mi_negocio.gestion_contable.compras.models import FacturaCompra
from apps.core_erp.accounting.models import JournalEntry,AccountingEventReceipt,Account
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.tax_register import reconcile_tax_register
from apps.core_erp.outbox_models import OutboxEvent
class ItemReturnChecks(unittest.TestCase):
 def setUp(self):
  self.multi=fixture['PurchaseConceptChecks']();self.multi.setUp();self.base=self.multi.base;self.case=self.base.case
  self.multi.items[1].update(tax_category='EXCLUDED',tax_accounts={});self.capture=self.multi.capture(tax='11.40',gross='111.40');self.base.post(self.capture,self.multi.review(self.capture));self.scope={**self.base.scope,'invoice_id':self.capture['invoice_id']};self.ids=[i['item_id'] for i in self.multi.items];self.day=self.case.base.day.isoformat()
 def state(self):return engine.state(**self.scope)
 def review(self,selection=None,**kw):
  return engine.review(**self.scope,**{'return_id':str(uuid.uuid4()),'selection':selection or [{'item_id':self.ids[0],'net':'30.00'}],'entry_date':self.day,'document_digest':uuid.uuid4().hex*2,'evidence_digest':'c'*64,'expected_revision':self.state()['revision'],'confirmed':True,**kw})
 def post(self,r,**kw):return engine.post(**self.scope,review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def item(self,r,index=0):return next(i for i in r['items'] if i['item_id']==self.ids[index])
 def void_review(self,r,**kw):
  return engine.review_void(**self.scope,**{'return_id':r['return_id'],'request_id':str(uuid.uuid4()),'entry_date':self.day,'reason_code':'DATA_ENTRY_ERROR','evidence_digest':'d'*64,'expected_revision':self.state()['revision'],'confirmed':True,**kw})
 def void(self,r,**kw):return engine.post_void(**self.scope,review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def test_rounding_cannot_return_more_payable_than_original_concept(self):
  item_id=self.ids[0];account=str(self.case.retention.pk)
  origin={'net':5,'item':{'basis_account_id':str(self.case.input_tax.pk)},'components':[{'code':'R1','kind':'WITHHOLDING','account_id':account,'amount':1},{'code':'R2','kind':'WITHHOLDING','account_id':account,'amount':1}]*2}
  with patch.object(engine,'originals',return_value={item_id:origin}):
   with self.assertRaises(AccountingError):engine.plan({}, {item_id:0},[{'item_id':item_id,'net':'0.02'}])
 def test_only_selected_taxable_concept_changes_and_original_is_preserved(self):
  before=JournalEntry.plain_objects.filter(tenant=self.base.company).count();r=self.review();self.assertEqual(r['preview']['totals'],{'net':'30.00','tax':'5.70','withholding':'0.75','gross':'35.70','settlement':'34.95'});a=self.post(r);self.assertEqual(self.item(a)['remaining']['net'],'30.00');self.assertEqual(self.item(a,1)['remaining']['net'],'40.00');self.assertFalse(a['money_transferred']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.company).count(),before+1)
 def test_excluded_concept_never_inherits_other_concept_tax(self):
  a=self.post(self.review(selection=[{'item_id':self.ids[1],'net':'20.00'}]));self.assertEqual(a['returns'][0]['totals']['tax'],'0.00');self.assertEqual(a['returns'][0]['totals']['withholding'],'0.00');self.assertEqual(self.item(a)['returned']['net'],'0.00')
 def test_tax_register_reduces_only_original_component_amounts(self):
  self.post(self.review())
  for account,kind,expected in [(self.case.input_tax,'INPUT_TAX','5.70'),(self.case.retention,'WITHHOLDING','0.75')]:
   report=reconcile_tax_register(self.base.company.pk,account_id=str(account.pk),since=self.day,until=self.day);self.assertEqual(report['tax_by_kind'][kind],expected);self.assertEqual(report['unattributed_journals'],0)
 def test_selected_multiple_concepts_and_total_exhaustion(self):
  a=self.post(self.review(selection=[{'item_id':self.ids[0],'net':'60.00'},{'item_id':self.ids[1],'net':'40.00'}]));self.assertTrue(all(i['remaining']['net']=='0.00' for i in a['items']))
  with self.assertRaises(AccountingError):self.review()
 def test_replay_has_one_post_and_recovery_restores_no_approval(self):
  r=self.review();a=self.post(r);b=self.post(r);self.assertEqual(a['journal_id'],b['journal_id']);self.assertTrue(b['replayed']);self.assertFalse(self.state()['confirmations_restored']);self.assertEqual(AccountingEventReceipt.objects.filter(tenant=self.base.company,event_id__startswith=engine.PREFIX).count(),1)
 def test_two_pending_returns_cannot_overallocate(self):
  a=self.review(selection=[{'item_id':self.ids[0],'net':'40.00'}]);b=self.review(selection=[{'item_id':self.ids[0],'net':'40.00'}]);self.post(a)
  with self.assertRaises(AccountingError):self.post(b)
 def test_over_return_duplicate_unknown_or_fractional_concepts_rejected(self):
  for selection in [[{'item_id':self.ids[0],'net':'60.01'}],[{'item_id':self.ids[0],'net':'1.001'}],[{'item_id':str(uuid.uuid4()),'net':'1.00'}],[{'item_id':self.ids[0],'net':'1.00'}]*2]:
   with self.assertRaises((AccountingError,ValueError)):self.review(selection=selection)
 def test_first_and_second_authorizations_are_separate(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.post(r,confirmed=False)
 def test_source_paid_or_changed_blocks_new_post(self):
  r=self.review();FacturaCompra.objects.filter(pk=self.capture['invoice_id']).update(estado='PAGADA')
  with self.assertRaises(AccountingError):self.post(r)
 def test_proof_failure_rolls_back_journal_and_document_claim(self):
  r=self.review();before=JournalEntry.plain_objects.filter(tenant=self.base.company).count();original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type')==engine.POSTED:raise RuntimeError('Synthetic evidence failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.post(r)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.company).count(),before);self.assertEqual(self.state()['revision'],0);self.post(r)
 def test_missing_proof_or_claim_never_frees_capacity(self):
  r=self.review();self.post(r);OutboxEvent.objects.filter(event_type=engine.POSTED,payload__body__invoice_id=self.capture['invoice_id'])._raw_delete('default')
  with self.assertRaises(AccountingError):self.state()
 def test_correction_is_two_confirmations_lifo_and_restores_only_its_concepts(self):
  first=self.review();self.post(first);second=self.review(selection=[{'item_id':self.ids[1],'net':'10.00'}]);self.post(second)
  with self.assertRaises(AccountingError):self.void_review(first)
  proposal=self.void_review(second)
  with self.assertRaises(AccountingError):self.void(proposal,confirmed=False)
  a=self.void(proposal);self.assertEqual(self.item(a)['returned']['net'],'30.00');self.assertEqual(self.item(a,1)['returned']['net'],'0.00');self.assertTrue(self.void(proposal)['replayed'])
 def test_correction_restores_tax_and_does_not_release_document(self):
  r=self.review();self.post(r);self.void(self.void_review(r));report=reconcile_tax_register(self.base.company.pk,account_id=str(self.case.input_tax.pk),since=self.day,until=self.day);self.assertEqual(report['tax_by_kind']['INPUT_TAX'],'11.40')
  with self.assertRaises(AccountingError):self.review(document_digest=r['preview']['document_digest'])
 def test_full_reversal_blocked_until_all_returns_corrected_then_preserves_history(self):
  r=self.review();a=self.post(r)
  with self.assertRaises(AccountingError):self.base.reverse_review(self.capture)
  with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(a['journal_id'],tenant_id=self.base.company.pk,actor=self.base.actor)
  self.void(self.void_review(r));review=self.base.reverse_review(self.capture);self.base.reverse(self.capture,review);self.assertTrue(self.state()['original_reversed'])
 def test_rounding_uses_cumulative_original_components_until_exact_exhaustion(self):
  self.post(self.review(selection=[{'item_id':self.ids[0],'net':'0.01'}]));self.post(self.review(selection=[{'item_id':self.ids[0],'net':'0.01'}]));a=self.post(self.review(selection=[{'item_id':self.ids[0],'net':'59.98'}]));i=self.item(a);self.assertEqual(i['returned']['tax'],'11.40');self.assertEqual(i['returned']['withholding'],'1.50');self.assertEqual(i['remaining']['tax'],'0.00')
if __name__=='__main__':unittest.main()
