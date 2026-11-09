"""Real local outbox, lease/retry and consumer contracts with no remote services."""
import runpy,unittest,os,json
from io import StringIO
from pathlib import Path
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_posting_check.py')),run_name='delivery_fixture')
from apps.core_erp.accounting import delivery
from apps.core_erp.accounting.delivery_models import AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from django.core.management import call_command
for model in (AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance):fixture['fixture']['fixture']['fixture']['create'](model)

class DeliveryTests(unittest.TestCase):
 def setUp(self):
  fixture['fixture']['AccountingFoundation'].setUp(self)
  self.user=fixture['fixture']['fixture']['F'].owner
  self.flag=patch.dict(os.environ,{'ACCOUNTING_LOCAL_PROJECTION_ENABLED':'1'});self.flag.start()
 def tearDown(self):self.flag.stop()
 def journal(self):return LedgerEngine.post_lines(tenant_id=self.tenant.pk,entry_date=timezone.localdate(),description='Local projection fixture',lines_data=[{'account':self.a,'debit':'10.00'},{'account':self.b,'credit':'10.00'}],actor=self.user,idempotency_key='fixture-event')
 def lease(self):
  self.journal();delivery.enqueue(self.tenant.pk);return delivery.claim(self.tenant.pk)
 def test_commercial_and_operational_events_are_not_accounting_projection(self):
  for kind in ['commercial.invoice.requested.v1','operations.reservation.confirmed.v1']:
   OutboxEvent.objects.create(event_type=kind,domain='commercial' if kind.startswith('commercial') else 'operations',aggregate_root=str(self.tenant.pk),payload={'company_id':str(self.tenant.pk),'tenant_id':str(self.tenant.pk)})
  result=delivery.run_batch(self.tenant.pk)
  self.assertEqual(result['delivered'],0)
  self.assertFalse(AccountingDelivery.objects.filter(tenant=self.tenant).exists())
  self.assertFalse(AccountingProjectionReceipt.objects.filter(tenant=self.tenant).exists())
  self.assertEqual(OutboxEvent.objects.filter(payload__company_id=str(self.tenant.pk),status='PENDING',published_at__isnull=True).count(),2)
 def test_commercial_transport_processed_flag_does_not_certify_fiscal_receipt(self):
  from apps.core_erp.accounting.commercial_outbox_status import inspect_commercial_outbox
  OutboxEvent.objects.create(event_type='commercial.invoice.requested.v1',domain='commercial',aggregate_root=str(self.tenant.pk),payload={'company_id':str(self.tenant.pk)},status='PROCESSED')
  OutboxEvent.objects.create(event_type='commercial.invoice.requested.v1',domain='commercial',aggregate_root=str(self.foreign.pk),payload={'company_id':str(self.foreign.pk)},status='ERROR')
  result=inspect_commercial_outbox(self.tenant.pk)
  self.assertEqual(result['transport_counts']['invoice_requests']['PROCESSED'],1)
  self.assertEqual(result['transport_counts']['invoice_requests']['ERROR'],0)
  self.assertFalse(result['fiscal_receipt_verified']);self.assertEqual(result['fiscal_acceptance'],'NOT_VERIFIED')
  self.assertFalse(result['outbox_status_is_fiscal_acceptance'])
 def test_success_updates_balances_receipt_and_local_ack_not_external_ack(self):
  self.journal();result=delivery.run_batch(self.tenant.pk)
  self.assertEqual(result['delivered'],1)
  self.assertEqual(AccountingProjectionReceipt.objects.filter(tenant=self.tenant).count(),1)
  self.assertEqual(AccountingDailyBalance.objects.get(tenant=self.tenant,account=self.a).debit,Decimal('10'))
  state=delivery.status(self.tenant.pk);self.assertTrue(state['complete']);self.assertFalse(state['external_publication_verified'])
  event=OutboxEvent.objects.get(payload__tenant_id=str(self.tenant.pk));self.assertEqual(event.status,'PENDING');self.assertIsNone(event.published_at)
  self.assertEqual(delivery.run_batch(self.tenant.pk)['delivered'],0)
 def test_disabled_and_read_only_command_have_no_side_effects(self):
  self.journal();output=StringIO()
  with patch.dict(os.environ,{'ACCOUNTING_LOCAL_PROJECTION_ENABLED':'0'}):
   call_command('accounting_project',tenant=self.tenant.pk,stdout=output)
   with self.assertRaises(delivery.ProjectorDisabled):delivery.run_batch(self.tenant.pk)
  self.assertEqual(json.loads(output.getvalue())['mode'],'READ_ONLY')
  self.assertEqual(AccountingDelivery.objects.filter(tenant=self.tenant).count(),0)
 def test_stale_and_expired_tokens_cannot_apply(self):
  lease=self.lease()
  with self.assertRaises(delivery.LeaseLost):delivery.consume(self.tenant.pk,lease['id'],'a'*48)
  AccountingDelivery.objects.filter(pk=lease['id']).update(lease_until=timezone.now()-timedelta(seconds=1))
  with self.assertRaises(delivery.LeaseLost):delivery.consume(self.tenant.pk,lease['id'],lease['token'])
  new=delivery.claim(self.tenant.pk);self.assertNotEqual(new['token'],lease['token'])
  with self.assertRaises(delivery.LeaseLost):delivery.consume(self.tenant.pk,lease['id'],lease['token'])
  delivery.consume(self.tenant.pk,new['id'],new['token'])
 def test_lost_ack_replay_does_not_increment_projection_twice(self):
  lease=self.lease();delivery.consume(self.tenant.pk,lease['id'],lease['token'])
  AccountingDelivery.objects.filter(pk=lease['id']).update(status='RETRY',next_attempt_at=timezone.now(),delivered_at=None)
  again=delivery.claim(self.tenant.pk);result=delivery.consume(self.tenant.pk,again['id'],again['token'])
  self.assertFalse(result['applied'])
  self.assertEqual(AccountingDailyBalance.objects.get(tenant=self.tenant,account=self.a).debit,Decimal('10'))
 def test_consumer_failure_rolls_back_balances_receipt_and_ack(self):
  lease=self.lease()
  with patch.object(AccountingProjectionReceipt.objects,'create',side_effect=OSError('synthetic failure')):
   with self.assertRaises(OSError):delivery.consume(self.tenant.pk,lease['id'],lease['token'])
  self.assertFalse(AccountingDailyBalance.objects.filter(tenant=self.tenant).exists())
  self.assertFalse(AccountingProjectionReceipt.objects.filter(tenant=self.tenant).exists())
  self.assertEqual(AccountingDelivery.objects.get(pk=lease['id']).status,'LEASED')
 def test_payload_changed_after_enqueue_is_quarantined(self):
  self.journal();delivery.enqueue(self.tenant.pk)
  event=OutboxEvent.objects.get(payload__tenant_id=str(self.tenant.pk));event.payload['total_debit']='999.00';event.save()
  result=delivery.run_batch(self.tenant.pk)
  self.assertEqual(result['quarantined'],1);self.assertFalse(AccountingDailyBalance.objects.filter(tenant=self.tenant).exists())
  self.assertFalse(delivery.status(self.tenant.pk)['complete'])
 def test_journal_tampering_is_rejected_before_projection(self):
  journal=self.journal();LedgerEntry.plain_objects.filter(journal_entry=journal).update(description='tampered')
  self.assertEqual(delivery.run_batch(self.tenant.pk)['quarantined'],1)
  self.assertFalse(AccountingProjectionReceipt.objects.filter(tenant=self.tenant).exists())
 def test_retry_backoff_and_exhaustion_are_bounded(self):
  self.journal()
  for attempt in range(1,6):
   with patch('apps.core_erp.accounting.delivery.consume',side_effect=TimeoutError('do not persist secrets')):
    result=delivery.run_batch(self.tenant.pk)
   row=AccountingDelivery.objects.get(tenant=self.tenant)
   self.assertEqual(row.attempts,attempt);self.assertNotIn('secrets',row.last_error_code)
   self.assertEqual(row.status,'QUARANTINED' if attempt==5 else 'RETRY')
   self.assertEqual(result['quarantined' if attempt==5 else 'retry'],1)
   row.next_attempt_at=timezone.now();row.save(update_fields=['next_attempt_at'])
  self.assertIsNone(delivery.claim(self.tenant.pk))
 def test_final_expired_lease_is_not_left_executable_forever(self):
  lease=self.lease();AccountingDelivery.objects.filter(pk=lease['id']).update(attempts=5,lease_until=timezone.now()-timedelta(seconds=1))
  self.assertIsNone(delivery.claim(self.tenant.pk));self.assertEqual(AccountingDelivery.objects.get(pk=lease['id']).status,'QUARANTINED')
 def test_legacy_journal_and_opening_balances_block_complete_projection(self):
  journal=self.journal();delivery.run_batch(self.tenant.pk)
  type(self.a).plain_objects.filter(pk=self.a.pk).update(initial_balance=Decimal('1.00'))
  state=delivery.status(self.tenant.pk);self.assertFalse(state['complete']);self.assertTrue(state['opening_reconciliation_required']);self.assertEqual(state['balances'],[])
  type(self.a).plain_objects.filter(pk=self.a.pk).update(initial_balance=0)
  JournalEntry.plain_objects.filter(pk=journal.pk).update(hash_version='legacy')
  self.assertTrue(delivery.status(self.tenant.pk)['legacy_reconciliation_required'])
 def test_batch_limit_and_invalid_lease_never_return_success(self):
  for value in [0,101,True]:
   with self.assertRaises(delivery.AccountingError):delivery.run_batch(self.tenant.pk,value)
  lease=self.lease()
  for invalid in [None,'ñ'*48]:
   with self.assertRaises(delivery.LeaseLost):delivery.consume(self.tenant.pk,lease['id'],invalid)

 def test_reversal_projects_a_neutral_net_without_deleting_original(self):
  original=self.journal()
  LedgerEngine.reverse_entry(original.pk,'Reviewed projection reversal',tenant_id=self.tenant.pk,actor=self.user)
  result=delivery.run_batch(self.tenant.pk);self.assertEqual(result['delivered'],2)
  balance=AccountingDailyBalance.objects.get(tenant=self.tenant,account=self.a)
  self.assertEqual(balance.debit,balance.credit)
  self.assertEqual(AccountingProjectionReceipt.objects.filter(tenant=self.tenant).count(),2)
  self.assertTrue(delivery.status(self.tenant.pk)['complete'])

 def test_invalid_envelope_is_counted_as_quarantined_on_adoption(self):
  self.journal()
  OutboxEvent.objects.filter(payload__tenant_id=str(self.tenant.pk)).update(domain='invalid-domain')
  result=delivery.run_batch(self.tenant.pk)
  self.assertEqual(result['enqueued'],1);self.assertEqual(result['quarantined'],1)
  self.assertEqual(AccountingDelivery.objects.get(tenant=self.tenant).last_error_code,'INVALID_ENVELOPE')
  self.assertFalse(delivery.status(self.tenant.pk)['complete'])

 def test_company_isolation_and_incomplete_state_do_not_expose_amounts(self):
  lease=self.lease()
  with self.assertRaises(AccountingDelivery.DoesNotExist):delivery.consume(self.foreign.pk,lease['id'],lease['token'])
  state=delivery.status(self.tenant.pk);self.assertFalse(state['complete']);self.assertEqual(state['balances'],[])
  self.assertEqual(delivery.status(self.foreign.pk)['balances'],[])

if __name__=='__main__':unittest.main()
