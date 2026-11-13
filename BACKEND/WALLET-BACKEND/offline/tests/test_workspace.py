import copy
import hashlib
import json
from pathlib import Path
import socket
import sqlite3
import tempfile
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch
from uuid import uuid4
from sgacd_wallet_offline import Workspace,WalletLocalError
from sgacd_wallet_offline.army import catalog,review_draft
from sgacd_wallet_offline.readiness import all_items
PASS='synthetic-long-passphrase'

class WorkspaceChecks(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'vault.sqlite3'
  self.store=Workspace.create(self.path,PASS);self.addCleanup(self.store.close)
 def draft(self):return self.store.add_draft(str(uuid4()),str(uuid4()),'12.30','COP')
 def test_notes_and_drafts_survive_unlock_without_plaintext_on_disk(self):
  self.store.add_note('private synthetic note','sensitive synthetic content');identifier=self.draft();before=self.store.snapshot();self.store.close()
  raw=self.path.read_bytes();self.assertNotIn(b'sensitive synthetic content',raw);self.assertNotIn(b'12.30',raw)
  reopened=Workspace.unlock(self.path,PASS);self.addCleanup(reopened.close);self.assertEqual(reopened.snapshot(),before)
  self.assertEqual(self.path.stat().st_mode&0o077,0)
 def test_wrong_passphrase_and_recreate_do_not_replace_workspace(self):
  self.store.add_note('original','retain original');before=self.store.snapshot()
  with self.assertRaises(WalletLocalError):Workspace.unlock(self.path,'wrong-but-long-passphrase')
  with self.assertRaises(WalletLocalError):Workspace.create(self.path,PASS)
  self.assertEqual(self.store.snapshot(),before)
 def test_tampered_ciphertext_or_generation_is_rejected(self):
  self.store.close()
  with sqlite3.connect(self.path) as db:
   cipher=db.execute('SELECT cipher FROM vault').fetchone()[0];changed=bytes([cipher[0]^1])+cipher[1:];db.execute('UPDATE vault SET cipher=?',(changed,))
  with self.assertRaises(WalletLocalError):Workspace.unlock(self.path,PASS)
 def test_ciphertext_cannot_be_rebound_to_other_generation(self):
  self.store.close()
  with sqlite3.connect(self.path) as db:db.execute('UPDATE vault SET generation=generation+1')
  with self.assertRaises(WalletLocalError):Workspace.unlock(self.path,PASS)
 def test_nonce_changes_on_each_update(self):
  with sqlite3.connect(self.path) as db:first=db.execute('SELECT nonce FROM vault').fetchone()[0]
  self.store.add_note('a','b')
  with sqlite3.connect(self.path) as db:second=db.execute('SELECT nonce FROM vault').fetchone()[0]
  self.assertNotEqual(first,second)
 def test_two_reviews_same_actor_and_digest_never_become_payment_proof(self):
  identifier=self.draft();draft=self.store.snapshot()['drafts'][0]
  with self.assertRaises(WalletLocalError):self.store.acknowledge(identifier,self.store.actor_id,draft['digest'],2)
  with self.assertRaises(WalletLocalError):self.store.acknowledge(identifier,str(uuid4()),draft['digest'],1)
  self.store.acknowledge(identifier,self.store.actor_id,draft['digest'],1)
  with self.assertRaises(WalletLocalError):self.store.server_review_payload(identifier)
  self.store.acknowledge(identifier,self.store.actor_id,draft['digest'],2)
  payload=self.store.server_review_payload(identifier)
  self.assertEqual(set(payload),{'source','destination','amount','currency','idempotency_key'})
  self.assertNotIn('device_proof',payload);self.assertNotIn('confirmation',payload)
 def test_edit_resets_both_reviews_and_idempotency(self):
  identifier=self.draft();draft=self.store.snapshot()['drafts'][0]
  for stage in [1,2]:self.store.acknowledge(identifier,self.store.actor_id,draft['digest'],stage)
  self.store.edit_draft(identifier,draft['fields']['source'],draft['fields']['destination'],'13','COP')
  edited=self.store.snapshot()['drafts'][0]
  self.assertEqual(edited['acks'],[]);self.assertNotEqual(edited['idempotency_key'],draft['idempotency_key'])
  with self.assertRaises(WalletLocalError):self.store.acknowledge(identifier,self.store.actor_id,draft['digest'],1)
 def test_expired_local_reviews_do_not_prepare_server_payload(self):
  identifier=self.draft();draft=self.store.snapshot()['drafts'][0]
  with patch('sgacd_wallet_offline.workspace.time.time',return_value=draft['expires_at']):
   with self.assertRaises(WalletLocalError):self.store.acknowledge(identifier,self.store.actor_id,draft['digest'],1)
 def test_concurrent_workspace_cannot_overwrite_newer_data(self):
  second=Workspace.unlock(self.path,PASS);self.addCleanup(second.close);self.store.add_note('first','retain')
  with self.assertRaisesRegex(WalletLocalError,'CONCURRENT'):second.add_note('stale','must not replace')
  reopened=Workspace.unlock(self.path,PASS);self.addCleanup(reopened.close);self.assertEqual(len(reopened.snapshot()['notes']),1)
 def test_locked_workspace_and_invalid_amounts_fail(self):
  for amount in ['NaN','Infinity','-1','0','1.001','10000000000000000']:
   with self.subTest(amount=amount),self.assertRaises(WalletLocalError):self.store.add_draft(str(uuid4()),str(uuid4()),amount,'COP')
  self.store.close()
  with self.assertRaises(WalletLocalError):self.store.add_note('a','b')
 def test_symlink_and_short_pin_are_rejected(self):
  with self.assertRaises(WalletLocalError):Workspace.create(Path(self.temp.name)/'pin.sqlite3','123456')
  link=Path(self.temp.name)/'link.sqlite3';link.symlink_to(self.path)
  with self.assertRaises(WalletLocalError):Workspace.unlock(link,PASS)
 def test_offline_army_has_no_payment_or_approval_capability_and_no_network(self):
  with patch.object(socket,'socket',side_effect=AssertionError('No network allowed')):
   identifier=self.draft();draft=self.store.snapshot()['drafts'][0];report=review_draft(draft,self.store.actor_id)
   self.assertFalse(report['settled']);self.assertFalse(report['automatic_dispatch'])
   self.assertTrue(report['requires_two_hardware_approvals']);self.assertEqual(len(catalog()),8)
   self.assertTrue(all(not agent['can_approve'] and not agent['can_execute_payments'] for agent in catalog()))
   self.store.add_note('offline','works without internet')
  self.assertNotIn(draft['fields']['destination'],json.dumps(report))
 def test_unlock_does_not_create_missing_files_or_modify_foreign_database_mode(self):
  missing=Path(self.temp.name)/'missing.sqlite3'
  with self.assertRaises(WalletLocalError):Workspace.unlock(missing,PASS)
  self.assertFalse(missing.exists())
  other=Path(self.temp.name)/'foreign.sqlite3'
  with sqlite3.connect(other) as db:db.execute('PRAGMA journal_mode=WAL');db.execute('CREATE TABLE untouched(value TEXT)')
  other.chmod(0o600)
  with self.assertRaises(WalletLocalError):Workspace.unlock(other,PASS)
  with sqlite3.connect(other) as db:self.assertEqual(db.execute('PRAGMA journal_mode').fetchone()[0],'wal')
 def test_flet_worker_threads_share_workspace_safely(self):
  with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda index:self.store.add_note('thread '+str(index),'synthetic content'),range(8)))
  self.assertEqual(len(self.store.snapshot()['notes']),8)
  with ThreadPoolExecutor(max_workers=1) as pool:pool.submit(self.store.close).result()
  with self.assertRaises(WalletLocalError):self.store.snapshot()
 def test_production_registry_retains_acceptance_and_evidence(self):
  entries=all_items();self.assertGreaterEqual(len(entries),18);self.assertEqual(len({x['id'] for x in entries}),len(entries))
  self.assertTrue(all(x['acceptance'] and x['owner'] and x['evidence'] for x in entries))
if __name__=='__main__':unittest.main()
