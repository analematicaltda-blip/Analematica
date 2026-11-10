"""Audited native corrections, partial returns and recovery in disposable ORM."""
import runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_native_purchase_check.py')),run_name='purchase_recovery_fixture')
from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_recovery as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
class PurchaseRecoveryChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['NativePurchaseChecks']();self.base.setUp();self.capture=self.base.capture();self.scope={**self.base.scope,'invoice_id':self.capture['invoice_id']}
 def review_correction(self,**kw):return engine.review_correction(**{**self.scope,'request_id':str(uuid.uuid4()),'changes':{'notes':'Synthetic correction'},'evidence_digest':'d'*64,'confirmed':True,**kw})
 def correct(self,r,**kw):return engine.confirm_correction(**{**self.scope,'review_id':r['review_id'],'confirmed':True,**kw})
 def post(self):return self.base.post(self.capture,self.base.review(self.capture))
 def review_return(self,**kw):return engine.review_return(**{**self.scope,'request_id':str(uuid.uuid4()),'return_bps':5000,'economic_date':self.base.invoice_args['issue_date'],'reason_code':'PARTIAL_RETURN','evidence_digest':'e'*64,'confirmed':True,**kw})
 def returned(self,r,**kw):return engine.confirm_return(**{**self.scope,'review_id':r['review_id'],'confirmed':True,**kw})
 def test_correction_preserves_capture_and_supports_post_and_history(self):
  r=self.review_correction();a=self.correct(r);self.assertTrue(self.correct(r)['replayed']);self.post();history=engine.history(**self.scope);self.assertEqual(len(history['corrections']),1);self.assertFalse(history['confirmations_restored']);self.assertIsNotNone(history['state']['posted'])
 def test_amount_correction_exactness_and_stale_review(self):
  a=self.review_correction(changes={'subtotal':'200.00','tax':'38.00','gross':'238.00'});b=self.review_correction();self.correct(a)
  with self.assertRaises(AccountingError):self.correct(b)
  with self.assertRaises(AccountingError):self.review_correction(changes={'gross':'239.00'})
 def test_posted_or_reviewed_purchase_cannot_be_edited(self):
  r=self.review_correction();self.base.review(self.capture)
  with self.assertRaises(AccountingError):self.correct(r)
  with self.assertRaises(AccountingError):self.review_correction()
 def test_partial_returns_cumulative_bound_and_replay(self):
  self.post();r=self.review_return(return_bps=4000);a=self.returned(r);self.assertTrue(self.returned(r)['replayed']);self.assertFalse(a['money_transferred']);self.assertEqual(len(engine.history(**self.scope)['returns']),1)
  self.returned(self.review_return(return_bps=6000))
  with self.assertRaises(AccountingError):self.review_return(return_bps=100)
  with self.assertRaises(AccountingError):self.base.reverse_review(self.capture)
 def test_competing_returns_and_fractional_cents_are_rejected(self):
  self.post();a=self.review_return(return_bps=4000);b=self.review_return(return_bps=6000);self.returned(a)
  with self.assertRaises(AccountingError):self.returned(b)
  with self.assertRaises(AccountingError):self.review_return(return_bps=1)
 def test_proof_failure_rolls_back_return_journal(self):
  self.post();r=self.review_return(return_bps=4000);count=JournalEntry.plain_objects.count();original=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.RETURNED:raise RuntimeError('Synthetic return proof failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.returned(r)
  self.assertEqual(count,JournalEntry.plain_objects.count());self.assertTrue(self.returned(r)['ledger_written'])
 def test_return_two_confirmations_and_no_unposted_return(self):
  with self.assertRaises(AccountingError):self.review_return()
  self.post()
  with self.assertRaises(AccountingError):self.review_return(confirmed=False)
  r=self.review_return(return_bps=4000)
  with self.assertRaises(AccountingError):self.returned(r,confirmed=False)
 def native_review(self):
  from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_returns
  return purchase_returns.review(**self.scope,return_id=str(uuid.uuid4()),net_amount='25.00',entry_date=self.base.invoice_args['issue_date'],document_digest=uuid.uuid4().hex*2,evidence_digest='b'*64,expected_revision=0,confirmed=True)
 def test_native_return_blocks_previously_reviewed_recovery_return(self):
  from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_returns
  self.post();old=self.review_return();new=self.native_review()
  purchase_returns.post(**self.scope,review_id=new['review_id'],confirmed=True)
  with self.assertRaises(AccountingError):self.returned(old)
  with self.assertRaises(AccountingError):self.review_return()
 def test_recovery_return_blocks_previously_reviewed_native_return(self):
  from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_returns
  self.post();new=self.native_review();self.returned(self.review_return())
  with self.assertRaises(AccountingError):purchase_returns.post(**self.scope,review_id=new['review_id'],confirmed=True)
  with self.assertRaises(AccountingError):self.native_review()
if __name__=='__main__':unittest.main()
