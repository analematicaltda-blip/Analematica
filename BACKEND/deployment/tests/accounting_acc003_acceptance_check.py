"""ACC003: single effect, payload binding and atomic recovery of local outbox."""
import runpy,unittest,uuid,copy
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal,localcontext
f=runpy.run_path(str(Path(__file__).with_name('accounting_delivery_check.py')),run_name='acc003_fixture')
from django.utils import timezone
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting import delivery
from apps.core_erp.accounting.delivery_models import AccountingDailyBalance,AccountingDelivery
class ACC003Acceptance(unittest.TestCase):
 def setUp(self):self.c=f['DeliveryTests']();self.c.setUp();self.addCleanup(self.c.tearDown)
 def args(self):return {'tenant_id':self.c.tenant.pk,'entry_date':timezone.localdate(),'description':'Atomic retry acceptance','lines_data':[{'account':self.c.a,'debit':'10.00'},{'account':self.c.b,'credit':'10.00'}],'actor':self.c.user,'idempotency_key':'ACC003-retry'}
 def counts(self):return tuple(m.plain_objects.count() if hasattr(m,'plain_objects') else m.objects.count() for m in [JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog,OutboxEvent])
 def test_duplicate_manual_event_has_single_journal_outbox_receipt(self):
  first=LedgerEngine.post_lines(**self.args());before=self.counts()
  for _ in range(3):self.assertEqual(LedgerEngine.post_lines(**self.args()).pk,first.pk)
  self.assertEqual(self.counts(),before);self.assertEqual(AccountingEventReceipt.objects.get(journal=first).event_id,'ACC003-retry');self.assertEqual(OutboxEvent.objects.filter(pk=first.pk).count(),1)
 def test_changed_payload_same_key_is_rejected_without_new_effect(self):
  LedgerEngine.post_lines(**self.args());before=self.counts()
  for change in [{'description':'Different'},{'lines_data':[{'account':self.c.a,'debit':'11.00'},{'account':self.c.b,'credit':'11.00'}]}]:
   with self.assertRaises(AccountingError):LedgerEngine.post_lines(**{**self.args(),**change})
   self.assertEqual(self.counts(),before)
 def test_receipt_audit_or_outbox_failure_rolls_back_entire_manual_transaction(self):
  for manager in [AccountingEventReceipt.objects,AccountingAuditLog.objects,OutboxEvent.objects]:
   before=self.counts()
   with patch.object(manager,'create',side_effect=OSError('Synthetic interrupted write')):
    with self.assertRaises(OSError):LedgerEngine.post_lines(**self.args())
   self.assertEqual(self.counts(),before)
  posted=LedgerEngine.post_lines(**self.args());self.assertTrue(posted.is_posted);self.assertEqual(OutboxEvent.objects.filter(pk=posted.pk).count(),1)
 def test_event_receipt_failure_and_retry_are_atomic_and_payload_bound(self):
  self.c.a.code='111005';self.c.a.save();self.c.b.code='130505';self.c.b.save();body={'tenant_id':str(self.c.tenant.pk),'financial_event_id':'ACC003-event','amount':'10.00'};before=self.counts()
  with patch.object(AccountingEventReceipt.objects,'create',side_effect=OSError('Synthetic receipt failure')):
   with self.assertRaises(OSError):LedgerEngine.post_event('PAYMENT_RECEIVED',body,actor=self.c.user)
  self.assertEqual(self.counts(),before);posted=LedgerEngine.post_event('PAYMENT_RECEIVED',body,actor=self.c.user);self.assertEqual(LedgerEngine.post_event('PAYMENT_RECEIVED',body,actor=self.c.user).pk,posted.pk)
  with self.assertRaises(AccountingError):LedgerEngine.post_event('PAYMENT_RECEIVED',{**body,'amount':'11.00'},actor=self.c.user)
 def test_replay_rejects_missing_outbox_without_reconstruction(self):
  posted=LedgerEngine.post_lines(**self.args());OutboxEvent.objects.filter(pk=posted.pk).delete();before=self.counts()
  with self.assertRaises(AccountingError):LedgerEngine.post_lines(**self.args())
  self.assertEqual(self.counts(),before);self.assertFalse(OutboxEvent.objects.filter(pk=posted.pk).exists())
 def test_replay_rejects_changed_envelope_or_payload(self):
  posted=LedgerEngine.post_lines(**self.args());event=OutboxEvent.objects.get(pk=posted.pk);original=copy.deepcopy(event.payload)
  for values in [{'domain':'other'},{'version':1},{'aggregate_root':str(uuid.uuid4())},{'payload':{**original,'total_debit':'11.00'}}]:
   previous={k:getattr(event,k) for k in values};OutboxEvent.objects.filter(pk=event.pk).update(**values)
   with self.assertRaises(AccountingError):LedgerEngine.post_lines(**self.args())
   OutboxEvent.objects.filter(pk=event.pk).update(**previous)
  self.assertEqual(LedgerEngine.post_lines(**self.args()).pk,posted.pk)
 def test_transport_status_does_not_change_transaction_identity(self):
  posted=LedgerEngine.post_lines(**self.args());OutboxEvent.objects.filter(pk=posted.pk).update(status='PROCESSED',published_at=timezone.now());self.assertEqual(LedgerEngine.post_lines(**self.args()).pk,posted.pk)
 def test_projection_is_exact_and_lost_ack_does_not_duplicate_effect(self):
  LedgerEngine.post_lines(**{**self.args(),'lines_data':[{'account':self.c.a,'debit':'1000000.01'},{'account':self.c.b,'credit':'1000000.01'}]});delivery.enqueue(self.c.tenant.pk);lease=delivery.claim(self.c.tenant.pk)
  with localcontext() as context:
   context.prec=2;self.assertTrue(delivery.consume(self.c.tenant.pk,lease['id'],lease['token'])['applied'])
  AccountingDelivery.objects.filter(pk=lease['id']).update(status='RETRY',next_attempt_at=timezone.now(),delivered_at=None);again=delivery.claim(self.c.tenant.pk);self.assertFalse(delivery.consume(self.c.tenant.pk,again['id'],again['token'])['applied']);self.assertEqual(AccountingDailyBalance.objects.get(tenant=self.c.tenant,account=self.c.a).debit,Decimal('1000000.01'))
if __name__=='__main__':unittest.main()
