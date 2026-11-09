"""Transactional request persistence against isolated real ORM tables."""
import copy,runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from django.db import transaction
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_foundation_check.py')),run_name='invoice_queue_fixture')
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.invoice_queue import enqueue_invoice_intent
from apps.core_erp.accounting.exceptions import AccountingError
fixture['fixture']['fixture']['create'](OutboxEvent)
class InvoiceQueueTests(unittest.TestCase):
 def setUp(self):
  fixture['AccountingFoundation'].setUp(self);self.actor=fixture['fixture']['F'].owner
  self.value={'schema':'sgacd-invoice-intent-v1','company_id':str(self.tenant.pk),'source_type':'reservation','source_id':str(uuid.uuid4()),'revision':1,'state':'CONFIRMED','currency':'COP','items':[{'item_id':str(uuid.uuid4()),'net':'100.00','tax':'19.00','tax_category':'TAXABLE','policy_reference':'reviewed-policy:1'}]}
 def enqueue(self,value=None):return enqueue_invoice_intent(value or self.value,company_id=self.tenant.pk,actor=self.actor)
 def test_persist_and_replay_one_pending_request_no_publication(self):
  with patch('apps.core_erp.event_bus.EventBus.emit',side_effect=AssertionError('No bus allowed')):
   a=self.enqueue();b=self.enqueue()
  self.assertFalse(a['replayed']);self.assertTrue(b['replayed']);self.assertEqual(a['outbox_id'],b['outbox_id'])
  row=OutboxEvent.objects.get(pk=a['outbox_id']);self.assertEqual(row.status,'PENDING');self.assertIsNone(row.published_at)
  for key in ['published_by_this_call','fiscal_accepted','ledger_written']:self.assertFalse(a[key])
 def test_changed_payload_rejected_original_unchanged(self):
  a=self.enqueue();before=copy.deepcopy(OutboxEvent.objects.get(pk=a['outbox_id']).payload);self.value['items'][0]['net']='200.00'
  with self.assertRaises(ValueError):self.enqueue()
  self.assertEqual(OutboxEvent.objects.get(pk=a['outbox_id']).payload,before)
 def test_outer_rollback_removes_request(self):
  source=self.value['source_id']
  with self.assertRaises(RuntimeError):
   with transaction.atomic():self.enqueue();raise RuntimeError('Producer failed')
  self.assertFalse(OutboxEvent.objects.filter(aggregate_root=source).exists())
 def test_write_failure_leaves_no_request(self):
  with patch.object(OutboxEvent.objects,'create',side_effect=RuntimeError('Storage unavailable')):
   with self.assertRaises(RuntimeError):self.enqueue()
  self.assertFalse(OutboxEvent.objects.filter(aggregate_root=self.value['source_id']).exists())
 def test_other_company_snapshot_rejected(self):
  self.value['company_id']=str(self.foreign.pk)
  with self.assertRaises(ValueError):self.enqueue()
  self.assertFalse(OutboxEvent.objects.filter(aggregate_root=self.value['source_id']).exists())
 def test_missing_actor_rejected(self):
  with self.assertRaises(AccountingError):enqueue_invoice_intent(self.value,company_id=self.tenant.pk,actor=None)
 def test_replay_preserves_existing_delivery_status(self):
  a=self.enqueue();OutboxEvent.objects.filter(pk=a['outbox_id']).update(status='PROCESSED')
  b=self.enqueue();self.assertEqual(b['outbox_status'],'PROCESSED');self.assertFalse(b['published_by_this_call'])
 def test_revision_creates_distinct_request(self):
  a=self.enqueue();self.value['revision']=2;b=self.enqueue()
  self.assertNotEqual(a['outbox_id'],b['outbox_id'])
if __name__=='__main__':unittest.main()
