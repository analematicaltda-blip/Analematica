"""Read-only durable rehearsal recovery never restores payment authority."""
import runpy,unittest,copy,uuid
from pathlib import Path
from unittest.mock import patch
from datetime import timedelta
f=runpy.run_path(str(Path(__file__).with_name('accounting_financial_orchestration_check.py')),run_name='acc021_fixture');engine=f['engine'];AccountingError=f['AccountingError'];timezone=f['timezone']
class StateChecks(unittest.TestCase):
 def setUp(self):self.base=f['FinancialRehearsalChecks']();self.base.setUp()
 def state(self,p):return engine.state(self.base.company.pk,**self.base.scope,request_id=p['request_id'])
 def test_recovery_tracks_separate_steps_without_writes_or_restored_authority(self):
  p=self.base.prepare();count=f['OutboxEvent'].objects.count();r=self.state(p);self.assertEqual(r['status'],'PREPARED');self.assertEqual(count,f['OutboxEvent'].objects.count());self.assertEqual(r['next_step'],1)
  self.base.confirm(p,1);self.assertEqual(self.state(p)['next_step'],2);self.base.confirm(p,2);r=self.state(p);self.assertTrue(r['can_simulate']);self.assertFalse(r['confirmations_restored']);self.assertFalse(r['usable_as_payment_authorization']);self.base.simulate(p);self.assertEqual(self.state(p)['status'],'SIMULATED_ONLY')
 def test_expired_recovery_remains_read_only_and_cancel_retry_idempotent(self):
  p=self.base.prepare()
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=6)):
   r=self.state(p);self.assertEqual(r['status'],'EXPIRED');self.assertIsNone(r['next_step']);args={'request_id':p['request_id'],'plan_digest':p['plan_digest'],'confirmed':True};engine.cancel(self.base.company.pk,**self.base.scope,**args);self.assertTrue(engine.cancel(self.base.company.pk,**self.base.scope,**args)['replayed']);self.assertEqual(self.state(p)['status'],'CANCELLED')
 def test_orphan_confirmation_is_rejected(self):
  p=self.base.approve();engine.read(self.base.company.pk,p['request_id'],'confirmation1').delete()
  with self.assertRaises(AccountingError):self.state(p)
 def test_changed_cancellation_payload_blocks_recovery(self):
  p=self.base.prepare();engine.cancel(self.base.company.pk,**self.base.scope,request_id=p['request_id'],plan_digest=p['plan_digest'],confirmed=True);row=engine.read(self.base.company.pk,p['request_id'],'cancelled');row.payload['plan_digest']='b'*64;row.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.state(p)
 def test_request_identity_cannot_be_swapped_with_recomputed_hash(self):
  p=self.base.prepare();row=engine.read(self.base.company.pk,p['request_id'],'prepared');row.payload['intent']['request_id']=str(uuid.uuid4());row.payload['plan_digest']=engine.fingerprint(row.payload['intent']);row.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.state(p)
 def test_changed_confirmation_metadata_blocks_recovery(self):
  p=self.base.approve();row=engine.read(self.base.company.pk,p['request_id'],'confirmation2');row.domain='foreign';row.save(update_fields=['domain'])
  with self.assertRaises(AccountingError):self.state(p)
if __name__=='__main__':unittest.main(verbosity=2)
