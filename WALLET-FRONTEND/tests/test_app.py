import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import AsyncMock,patch
from uuid import uuid4
from sgacd_wallet_ui import WalletApp
from sgacd_wallet_offline import WalletLocalError,Workspace
from sgacd_vault import SensitiveDisplay,VaultError

class Page:
 def __init__(self,web=False):self.web=web;self.controls=[];self.overlay=[];self.window=SimpleNamespace();self.tasks=[]
 def add(self,*controls):self.controls.extend(controls)
 def update(self):pass
 def run_task(self,callback):self.tasks.append(callback)

class UIChecks(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
 def app(self,mode='desktop',web=False):
  app=WalletApp(Page(web),mode,storage=self.temp.name);self.addCleanup(app.close);return app
 def open(self,app):app.password.value='synthetic-local-passphrase';app.action(lambda:app.open_local(True))
 def test_native_desktop_can_create_notes_without_financial_login(self):
  app=self.app();self.open(app);self.assertIsNotNone(app.workspace)
  app.nav('Apuntes');app.note_title.value='Synthetic note';app.note_content.value='Private offline content';app.action(lambda:app.workspace.add_note(app.note_title.value,app.note_content.value))
  self.assertEqual(len(app.workspace.snapshot()['notes']),1)
 def test_editing_in_ui_resets_both_local_reviews(self):
  app=self.app();self.open(app);identifier=app.workspace.add_draft(str(uuid4()),str(uuid4()),'10','COP');draft=app.workspace.snapshot()['drafts'][0]
  for stage in [1,2]:app.workspace.acknowledge(identifier,app.workspace.actor_id,draft['digest'],stage)
  app.nav('Borradores');app.edit_draft(app.workspace.snapshot()['drafts'][0]);app.amount.value='11';app.action(app.save_draft)
  edited=app.workspace.snapshot()['drafts'][0];self.assertEqual(edited['acks'],[]);self.assertEqual(edited['fields']['amount'],'11.00')
 def test_web_cannot_unlock_even_when_native_mode_is_requested(self):
  app=self.app('desktop',web=True);self.assertFalse(app.local_allowed);self.assertFalse(hasattr(app,'password'))
  with self.assertRaises(WalletLocalError):app.open_local(True)
  self.assertFalse(app.path.exists())
 def test_forced_web_transport_cannot_use_native_cache_when_client_claims_native(self):
  import os
  with patch.dict(os.environ,{'FLET_FORCE_WEB_SERVER':'true'}):app=self.app('desktop',web=False)
  self.assertFalse(app.local_allowed)
  with self.assertRaises(WalletLocalError):app.open_local(True)
  self.assertFalse(app.path.exists())
 def test_web_team_and_pending_pages_are_available_without_secret_inputs(self):
  app=self.app('web',web=True)
  for section in ['Equipo','Producción']:app.nav(section);self.assertTrue(app.page.controls)
  self.assertIsNone(app.workspace);self.assertFalse(hasattr(app,'password'))
 def test_background_and_blur_lock_and_clear_fields(self):
  app=self.app();self.open(app);app.nav('Apuntes');app.note_content.value='must leave current form'
  app.lifecycle(SimpleNamespace(state='AppLifecycleState.PAUSED'))
  self.assertIsNone(app.workspace);self.assertFalse(app.note_content.value)
  app.lifecycle(SimpleNamespace(state='AppLifecycleState.RESUMED'))
  app.password.value='synthetic-local-passphrase';app.action(lambda:app.open_local(False));self.assertIsNotNone(app.workspace)
  app.window_event(SimpleNamespace(data='blur'));self.assertIsNone(app.workspace)
 def test_background_during_unlock_does_not_resurrect_session(self):
  app=self.app();self.open(app);app.close();app.render();app.password.value='synthetic-local-passphrase';original=Workspace.unlock
  def closing_unlock(*args):
   workspace=original(*args);app.close();return workspace
  with patch.object(Workspace,'unlock',side_effect=closing_unlock),self.assertRaises(WalletLocalError):app.open_local(False)
  self.assertIsNone(app.workspace)
 def test_close_does_not_reveal_or_reset_private_workspace(self):
  app=self.app();self.open(app);app.disconnect(None);self.assertFalse(app._alive);self.assertIsNone(app.workspace);self.assertTrue(app.path.exists())

class MobileChecks(unittest.IsolatedAsyncioTestCase):
 async def test_mobile_requires_native_screen_guard_before_password(self):
  with tempfile.TemporaryDirectory() as root:
   app=WalletApp(Page(),'mobile',storage=root);self.addCleanup(app.close)
   self.assertFalse(app.screen_ready);self.assertFalse(hasattr(app,'password'))
   with self.assertRaises(WalletLocalError):app.open_local(True)
   app.screen.protect=AsyncMock(side_effect=VaultError('Unavailable'));await app.activate_screen(None)
   self.assertFalse(app.screen_ready);self.assertFalse(hasattr(app,'password'))
   app.screen.protect=AsyncMock(return_value=True);await app.activate_screen(None)
   self.assertTrue(app.screen_ready);self.assertTrue(hasattr(app,'password'))
 async def test_screen_only_channel_cannot_return_identity_or_content(self):
  guard=SensitiveDisplay();guard.invoke_method_async=AsyncMock(return_value=json.dumps({'ok':True,'protocol':1,'status':'protected'}))
  self.assertTrue(await guard.protect());self.assertEqual(guard.invoke_method_async.call_args.args,('protect_display',{}))
  for value in [{'ok':True,'protocol':True,'status':'protected'},{'ok':True,'protocol':1,'status':'protected','key':'secret'},{'ok':True,'protocol':1,'status':'authenticated'}]:
   guard.invoke_method_async.return_value=json.dumps(value)
   with self.assertRaises(VaultError):await guard.protect()
if __name__=='__main__':unittest.main()
