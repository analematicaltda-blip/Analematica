"""Persisted purchase history, bounded and owner scoped, with verified phases."""
import runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_native_purchase_check.py')),run_name='purchase_history_fixture')
engine=fixture['engine'];FacturaCompra=fixture['FacturaCompra'];OutboxEvent=fixture['OutboxEvent'];AccountingError=fixture['AccountingError']
class PurchaseHistoryChecks(unittest.TestCase):
 def setUp(self):self.base=fixture['NativePurchaseChecks']();self.base.setUp()
 def history(self,**kw):return engine.purchase_history(**self.base.scope,**{'after_id':None,'search':'',**kw})
 def row(self):return self.history()['invoices'][0]
 def test_phases_follow_actual_capture_review_post_and_reversal(self):
  c=self.base.capture();self.assertEqual(self.row()['accounting_phase'],'CAPTURED');r=self.base.review(c);self.assertEqual(self.row()['accounting_phase'],'REVIEWED');p=self.base.post(c,r);self.assertEqual(self.row()['journal_id'],p['journal_id']);self.assertEqual(self.row()['accounting_phase'],'POSTED');self.base.reverse(c,self.base.reverse_review(c));self.assertEqual(self.row()['accounting_phase'],'REVERSED')
 def test_changed_invoice_is_visible_without_reposting(self):
  c=self.base.capture();self.base.post(c,self.base.review(c));FacturaCompra.objects.filter(pk=c['invoice_id']).update(estado='ANULADA');self.assertTrue(self.row()['source_changed']);self.assertEqual(self.row()['accounting_phase'],'POSTED')
 def test_changed_capture_without_review_is_not_reported_unchanged(self):
  c=self.base.capture();FacturaCompra.objects.filter(pk=c['invoice_id']).update(notas='changed');self.assertTrue(self.row()['source_changed']);self.assertEqual(self.row()['accounting_phase'],'CAPTURED')
 def test_legacy_has_no_invented_evidence(self):
  self.base.capture();c=FacturaCompra.objects.create(perfil_id=self.base.provider.pk,proveedor_id=self.base.party['supplier_id'],number='LEGACY-1',issue_date=self.base.case.base.day,subtotal='1.00',impuestos='0.00',total='1.00',estado='POR_PAGAR',creado_por=self.base.actor);row=self.history(search='LEGACY')['invoices'][0];self.assertEqual(row['invoice_id'],c.pk);self.assertEqual(row['accounting_phase'],'LEGACY_UNRECONCILED');self.assertIsNone(row['source_changed']);self.assertIsNone(row['journal_id'])
 def test_missing_or_tampered_native_origin_fails_closed(self):
  c=self.base.capture();self.base.post(c,self.base.review(c));OutboxEvent.objects.filter(event_type=engine.POSTED,aggregate_root=str(self.base.company.pk)).delete()
  with self.assertRaises(AccountingError):self.history()
 def test_pagination_search_and_no_duplicates(self):
  for n in range(22):self.base.capture(request_id=str(uuid.uuid4()),number='PAGE-'+str(n).zfill(2),document_digest=uuid.uuid4().hex*2)
  a=self.history(search='PAGE-');self.assertEqual(len(a['invoices']),20);b=self.history(search='PAGE-',after_id=a['next_after_id']);self.assertEqual(len(b['invoices']),2);self.assertIsNone(b['next_after_id']);self.assertFalse(set(r['invoice_id'] for r in a['invoices'])&set(r['invoice_id'] for r in b['invoices']));self.assertEqual(self.history(search='NONE')['invoices'],[])
 def test_query_is_read_only_and_never_restores_confirmations(self):
  self.base.capture();before=OutboxEvent.objects.count();r=self.history();self.assertEqual(OutboxEvent.objects.count(),before)
  for key in ['ledger_written','money_transferred','documents_returned','confirmations_restored','regulatory_verified']:self.assertIs(r[key],False)
 def test_strict_search_cursor_and_api_contract(self):
  for kw in [{'search':' leading'},{'search':'a'*51},{'after_id':True},{'after_id':-1}]:
   with self.assertRaises(AccountingError):self.history(**kw)
  self.assertEqual(self.base.call('native_purchase_history',{'after_id':None,'search':''}).status_code,200);self.assertEqual(self.base.call('native_purchase_history',{'after_id':None,'search':'','confirmed':True}).status_code,400)
 def test_missing_capture_link_cannot_downgrade_native_to_legacy(self):
  c=self.base.capture();OutboxEvent.objects.filter(pk=uuid.uuid5(engine.NS,'invoice-capture:'+str(self.base.company.pk)+':'+str(c['invoice_id']))).delete()
  with self.assertRaises(AccountingError):self.history()
 def test_foreign_provider_cannot_read_history(self):
  self.base.capture();self.assertEqual(self.base.call('native_purchase_history',{'after_id':None,'search':''},provider=uuid.uuid4()).status_code,403)
if __name__=='__main__':unittest.main()
