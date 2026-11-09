"""Native purchase metadata -> persisted source -> two reviews -> canonical ledger."""
import copy,runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_commercial_tax_check.py')),run_name='native_purchase_fixture')
from apps.prestadores.mi_negocio.gestion_contable.compras import native_purchase as engine
from apps.prestadores.mi_negocio.gestion_contable.compras.models import Proveedor,FacturaCompra
from apps.core_erp.accounting import commercial_tax_posting as ledger,source_bindings
from apps.core_erp.accounting.models import JournalEntry,AccountingEventReceipt
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.tax_register import reconcile_tax_register
from apps.core_erp.outbox_models import OutboxEvent
from apps.turismo.models import VerifiedCompanyLink
from rest_framework.test import APIRequestFactory,force_authenticate
from rest_framework.exceptions import PermissionDenied
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
create=fixture['fixture']['create']
for model in [Proveedor,FacturaCompra]:create(model)
class NativePurchaseChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['CommercialTaxChecks']();self.case.setUp();self.company=self.case.company;self.actor=self.case.actor;self.provider=self.case.base.case.provider
  self.scope={'actor':self.actor,'provider_id':self.provider.pk};self.supplier_args={'request_id':str(uuid.uuid4()),'name':'Synthetic native supplier','identification':'S-'+uuid.uuid4().hex[:12].upper(),'evidence_digest':'a'*64,'confirmed':True}
  self.party=engine.record_supplier(**self.scope,**self.supplier_args)
  self.invoice_args={'request_id':str(uuid.uuid4()),'supplier_id':self.party['supplier_id'],'number':'SYNTHETIC-001','issue_date':self.case.base.day.isoformat(),'due_date':None,'subtotal':'100.00','tax':'19.00','gross':'119.00','document_digest':uuid.uuid4().hex*2,'evidence_digest':'b'*64,'confirmed':True}
 def capture(self,**extra):return engine.record_invoice(**self.scope,**{**self.invoice_args,**extra})
 def review(self,capture,**extra):return engine.review_purchase(**self.scope,**{'invoice_id':capture['invoice_id'],'selection':copy.deepcopy(self.case.fact['items']),'settlement_account_id':str(self.case.payable.pk),'economic_fact':'GOODS_OR_SERVICES_RECEIVED','evidence_digest':'c'*64,'expected_revision':0,'confirmed':True,**extra})
 def post(self,capture,review,**extra):return engine.post_purchase(**self.scope,**{'invoice_id':capture['invoice_id'],'review_id':review['review_id'],'confirmed':True,**extra})
 def state(self,capture):return engine.purchase_state(**self.scope,invoice_id=capture['invoice_id'])
 def reverse_review(self,capture):return engine.review_purchase_reversal(**self.scope,invoice_id=capture['invoice_id'],reason_code='CORRECTION',evidence_digest='d'*64,confirmed=True)
 def reverse(self,capture,r):return engine.reverse_purchase(**self.scope,invoice_id=capture['invoice_id'],review_id=r['review_id'],confirmed=True)
 def call(self,action,payload,provider=None):
  request=APIRequestFactory().post('/fixture/?provider_id='+str(provider or self.provider.pk),payload,format='json');force_authenticate(request,user=self.actor);return PlanCuentaViewSet.as_view({'post':action})(request)
 def test_metadata_capture_never_posts_or_runs_broken_legacy_signal(self):
  c=self.capture();self.assertFalse(c['ledger_written']);self.assertEqual(FacturaCompra.objects.get(pk=c['invoice_id']).estado,'POR_PAGAR');self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_supplier_and_invoice_requests_are_idempotent(self):
  self.assertTrue(engine.record_supplier(**self.scope,**self.supplier_args)['replayed']);c=self.capture();again=self.capture();self.assertTrue(again['replayed']);self.assertEqual(c['invoice_id'],again['invoice_id'])
  with self.assertRaises(AccountingError):self.capture(gross='120.00',tax='20.00')
 def test_duplicate_invoice_number_and_document_digest_rejected(self):
  self.capture()
  with self.assertRaises(AccountingError):self.capture(request_id=str(uuid.uuid4()))
  with self.assertRaises(AccountingError):self.capture(request_id=str(uuid.uuid4()),number='SYNTHETIC-002')
 def test_review_does_not_post_and_native_post_replays_same_journal(self):
  c=self.capture();r=self.review(c);self.assertTrue(r['native_source_verified']);self.assertFalse(r['ledger_written']);a=self.post(c,r);b=self.post(c,r);self.assertEqual(a['journal_id'],b['journal_id']);self.assertTrue(b['replayed']);self.assertEqual(self.state(c)['posted']['journal_id'],a['journal_id']);self.assertFalse(a['money_transferred']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1)
 def test_native_purchase_tax_is_visible_in_unified_register(self):
  c=self.capture();self.post(c,self.review(c));r=reconcile_tax_register(self.company.pk,account_id=str(self.case.input_tax.pk),since=self.case.base.day.isoformat(),until=self.case.base.day.isoformat());self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'19.00');self.assertEqual(r['lines'][0]['document_id'],c['document_id'])
 def test_both_confirmations_are_required(self):
  c=self.capture()
  with self.assertRaises(AccountingError):self.review(c,confirmed=False)
  r=self.review(c)
  with self.assertRaises(AccountingError):self.post(c,r,confirmed=False)
 def test_policy_breakdown_must_match_stored_invoice(self):
  c=self.capture();selection=copy.deepcopy(self.case.fact['items']);selection[0]['net']='101.00'
  with self.assertRaises(AccountingError):self.review(c,selection=selection)
 def test_economic_receipt_is_not_inferred_from_invoice(self):
  c=self.capture()
  with self.assertRaises(AccountingError):self.review(c,economic_fact='INVOICE_EXISTS')
 def test_source_amount_change_between_confirmations_blocks(self):
  c=self.capture();r=self.review(c);FacturaCompra.objects.filter(pk=c['invoice_id']).update(subtotal='200.00')
  with self.assertRaises(AccountingError):self.post(c,r)
 def test_supplier_identity_change_blocks_posting(self):
  c=self.capture();r=self.review(c);Proveedor.objects.filter(pk=self.party['supplier_id']).update(identificacion='DIFFERENT-ID')
  with self.assertRaises(AccountingError):self.post(c,r)
 def test_cancelled_or_paid_native_invoice_cannot_be_newly_posted(self):
  c=self.capture();r=self.review(c)
  for state in ['ANULADA','PAGADA']:
   FacturaCompra.objects.filter(pk=c['invoice_id']).update(estado=state)
   with self.assertRaises(AccountingError):self.post(c,r)
 def test_posted_result_survives_source_change_without_reposting(self):
  c=self.capture();r=self.review(c);a=self.post(c,r);FacturaCompra.objects.filter(pk=c['invoice_id']).update(estado='ANULADA');b=self.post(c,r);self.assertTrue(b['replayed']);self.assertTrue(b['source_changed_since_posting']);self.assertEqual(a['journal_id'],b['journal_id']);self.assertFalse(self.state(c)['source_matches_review'])
 def test_generic_post_cannot_bypass_native_source_guard(self):
  c=self.capture();r=self.review(c)
  with self.assertRaises(AccountingError):ledger.post_fact(self.company.pk,actor=self.actor,document_id=c['document_id'],review_id=r['review_id'],confirmed=True)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_generic_review_cannot_detach_reserved_document(self):
  c=self.capture();f=copy.deepcopy(self.case.fact);f.update(document_id=c['document_id'],document_digest=self.invoice_args['document_digest'])
  with self.assertRaises(AccountingError):ledger.review_fact(self.company.pk,actor=self.actor,fact=f,evidence_digest='c'*64,expected_revision=0,confirmed=True)
 def test_same_reserved_digest_cannot_be_posted_with_another_document_uuid(self):
  self.capture();f=copy.deepcopy(self.case.fact);f['document_digest']=self.invoice_args['document_digest']
  with self.assertRaises(AccountingError):ledger.review_fact(self.company.pk,actor=self.actor,fact=f,evidence_digest='c'*64,expected_revision=0,confirmed=True)
 def test_missing_capture_or_reservation_proof_never_reconstructed(self):
  c=self.capture();OutboxEvent.objects.filter(pk=source_bindings.reserved_id(self.company.pk,c['document_id'])).delete()
  with self.assertRaises(AccountingError):self.review(c)
 def test_foreign_supplier_and_foreign_invoice_refused(self):
  other=fixture['CommercialTaxChecks']();other.setUp();foreign=Proveedor.objects.create(perfil_id=other.base.case.provider.pk,nombre='Synthetic foreign',identificacion='FOREIGN-ID')
  with self.assertRaises(AccountingError):self.capture(supplier_id=foreign.pk)
  c=self.capture()
  with self.assertRaises((AccountingError,PermissionDenied)):engine.purchase_state(actor=other.actor,provider_id=other.base.case.provider.pk,invoice_id=c['invoice_id'])
 def test_native_proof_failure_rolls_back_entire_post(self):
  c=self.capture();r=self.review(c);original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type')==engine.POSTED:raise RuntimeError('Synthetic native proof failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.post(c,r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists());self.assertFalse(AccountingEventReceipt.objects.filter(tenant=self.company).exists());self.assertTrue(self.post(c,r)['ledger_written'])
 def test_missing_native_posted_proof_blocks_replay_and_state(self):
  c=self.capture();r=self.review(c);self.post(c,r);OutboxEvent.objects.filter(event_type=engine.POSTED,payload__company_id=str(self.company.pk)).delete()
  with self.assertRaises(AccountingError):self.post(c,r)
  with self.assertRaises(AccountingError):self.state(c)
 def test_native_reversal_two_confirmations_and_replay(self):
  c=self.capture();r=self.review(c);a=self.post(c,r);reverse=self.reverse_review(c);b=self.reverse(c,reverse);again=self.reverse(c,reverse);self.assertTrue(again['replayed']);self.assertEqual(again['journal_id'],b['journal_id']);self.assertNotEqual(a['journal_id'],b['journal_id']);self.assertTrue(self.post(c,r)['reversed'])
 def test_generic_reversal_cannot_bypass_native_adapter(self):
  c=self.capture();self.post(c,self.review(c))
  with self.assertRaises(AccountingError):ledger.review_reversal(self.company.pk,actor=self.actor,document_id=c['document_id'],reason_code='CORRECTION',evidence_digest='d'*64,confirmed=True)
 def test_historical_invoice_without_capture_is_not_assumed_unposted(self):
  row=FacturaCompra.objects.create(perfil_id=self.provider.pk,proveedor_id=self.party['supplier_id'],number='HISTORICAL-001',issue_date=self.case.base.day,subtotal='100.00',impuestos='19.00',total='119.00',creado_por=self.actor)
  with self.assertRaises(AccountingError):self.review({'invoice_id':row.pk})
 def test_api_native_intake_review_post_and_private_recovery(self):
  body={**self.invoice_args};r=self.call('record_native_purchase',body);self.assertEqual(r.status_code,200,r.data);c=r.data
  body={'invoice_id':c['invoice_id'],'selection':copy.deepcopy(self.case.fact['items']),'settlement_account_id':str(self.case.payable.pk),'economic_fact':'GOODS_OR_SERVICES_RECEIVED','evidence_digest':'c'*64,'expected_revision':0,'confirmed':True};r=self.call('review_native_purchase',body);self.assertEqual(r.status_code,200,r.data)
  p=self.call('post_native_purchase',{'invoice_id':c['invoice_id'],'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(p.status_code,200,p.data);state=self.call('native_purchase_state',{'invoice_id':c['invoice_id']});self.assertEqual(state.status_code,200,state.data);self.assertEqual(state.data['posted']['journal_id'],p.data['journal_id']);self.assertIn('no-store',state['Cache-Control'])
 def test_api_context_override_and_revoked_link_refused(self):
  c=self.capture();r=self.review(c);body={'invoice_id':c['invoice_id'],'review_id':r['review_id'],'confirmed':True}
  self.assertEqual(self.call('post_native_purchase',{**body,'company_id':str(uuid.uuid4())}).status_code,400)
  VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now());self.assertEqual(self.call('post_native_purchase',body).status_code,403)
 def test_source_list_is_paged_without_other_company_or_documents(self):
  for n in range(21):self.capture(request_id=str(uuid.uuid4()),number='SYNTHETIC-'+str(n+2),document_digest=uuid.uuid4().hex*2)
  one=engine.purchase_sources(**self.scope,after_id=None);two=engine.purchase_sources(**self.scope,after_id=one['next_after_id']);self.assertEqual(len(one['invoices']),20);self.assertEqual(len(two['invoices']),1);self.assertFalse(one['documents_returned']);self.assertNotIn(two['invoices'][0]['invoice_id'],{r['invoice_id'] for r in one['invoices']})
 def test_supplier_intake_replay_does_not_hide_source_changes(self):
  Proveedor.objects.filter(pk=self.party['supplier_id']).update(nombre='Changed supplier')
  with self.assertRaises(AccountingError):engine.record_supplier(**self.scope,**self.supplier_args)
 def test_invoice_intake_replay_does_not_hide_source_changes(self):
  c=self.capture();FacturaCompra.objects.filter(pk=c['invoice_id']).update(estado='ANULADA')
  with self.assertRaises(AccountingError):self.capture()
 def test_failed_digest_reservation_rolls_back_invoice_capture(self):
  original=OutboxEvent.objects.create;calls=[]
  def create(**kw):
   if kw.get('event_type')==source_bindings.RESERVED:
    calls.append(kw)
    if len(calls)==2:raise RuntimeError('Synthetic digest reservation failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.capture()
  self.assertFalse(FacturaCompra.objects.filter(perfil_id=self.provider.pk).exists());self.assertFalse(OutboxEvent.objects.filter(event_type=engine.INTAKE,aggregate_root=str(self.company.pk)).exists());self.assertFalse(OutboxEvent.objects.filter(event_type=source_bindings.RESERVED,aggregate_root__startswith=str(self.company.pk)).exists())
 def test_missing_digest_reservation_blocks_generic_and_native_post(self):
  c=self.capture();r=self.review(c);OutboxEvent.objects.filter(pk=source_bindings.digest_id(self.company.pk,self.invoice_args['document_digest'])).delete()
  with self.assertRaises(AccountingError):self.post(c,r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_native_permission_scope_does_not_leak_after_error(self):
  c=self.capture();r=self.review(c)
  with self.assertRaises(AccountingError):self.post(c,r,confirmed=False)
  with self.assertRaises(AccountingError):ledger.post_fact(self.company.pk,actor=self.actor,document_id=c['document_id'],review_id=r['review_id'],confirmed=True)
  self.assertTrue(self.post(c,r)['ledger_written'])
 def test_purchase_catalog_includes_expenses_without_changing_sales_catalog(self):
  from apps.core_erp.accounting.catalog import purchase_catalog,recognition_catalog
  native=purchase_catalog(self.company,paged='1');sales=recognition_catalog(self.company,paged='1');self.assertIn(self.case.expense.pk,{r['id'] for r in native['accounts']});self.assertNotIn(self.case.expense.pk,{r['id'] for r in sales['accounts']});self.assertNotIn(self.case.base.revenue.pk,{r['id'] for r in native['accounts']})
 def test_ambiguous_or_unsafe_native_identifiers_rejected(self):
  for value in [True,1.0,'1',0,9007199254740992]:
   with self.assertRaises(AccountingError):engine.supplier(self.provider,value)
 def test_inconsistent_intake_amounts_create_no_invoice(self):
  for changes in [{'gross':'118.00'},{'subtotal':100.0},{'document_digest':'bad'}]:
   with self.assertRaises((AccountingError,ValueError)):self.capture(**changes)
  self.assertFalse(FacturaCompra.objects.filter(perfil_id=self.provider.pk).exists())
 def test_cancelled_source_can_reverse_original_without_rebooking(self):
  c=self.capture();r=self.review(c);self.post(c,r);FacturaCompra.objects.filter(pk=c['invoice_id']).update(estado='ANULADA');reverse=self.reverse_review(c);self.reverse(c,reverse);self.assertTrue(self.post(c,r)['reversed']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),2)
 def test_supplier_sources_are_owned_paged_and_not_identity_certification(self):
  result=engine.supplier_sources(**self.scope,after_id=None);self.assertEqual(len(result['suppliers']),1);self.assertEqual(result['suppliers'][0]['supplier_id'],self.party['supplier_id']);self.assertFalse(result['identity_verified']);self.assertFalse(result['documents_returned'])
if __name__=='__main__':unittest.main()
