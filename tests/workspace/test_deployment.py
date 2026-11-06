"""Updater safety: fake Docker interface, real temporary configuration/files."""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('workspace_installer',ROOT/'scripts/integrate_workspace.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
class DeploymentTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.demo=Path(self.temp.name)
  (self.demo/'node.env').write_text('NODE6_TOKEN=test-interservice-token-not-real\nGEMINI_API_KEY=test-provider-never-copy\n')
  self.original={'name':'test','services':{'backend':{'image':'existing-backend','environment':{'SECRET_KEY':'preserved-test-key'},'volumes':['state:/state']},'web':{'image':'nginx','ports':['127.0.0.1:8080:80']},'flet-mobile':{'image':'existing-flet','volumes':['mobile_offline:/offline']},'flet-desktop':{'image':'existing-flet','volumes':['desktop_offline:/offline']},'node6':{'image':'existing-node6','env_file':['node.env'],'volumes':['node6_state:/state']}},'volumes':{'state':{},'mobile_offline':{},'desktop_offline':{},'node6_state':{}}}
  (self.demo/'compose.json').write_text(json.dumps(self.original));(self.demo/'offline-sentinel.sqlite').write_bytes(b'offline-data-must-remain')
 def tearDown(self):self.temp.cleanup()
 def fake_run(self,argv,**kwargs):
  if argv[:2]==['docker','cp']:
   target=Path(argv[-1]);target.parent.mkdir(parents=True,exist_ok=True);target.write_text('api_router=APIRouter()\n' if argv[-2].endswith('/api.py') else 'app=FastAPI()\n')
  return subprocess.CompletedProcess(argv,0)
 def execute(self):
  with patch.object(installer.subprocess,'run',side_effect=self.fake_run),patch.object(installer.subprocess,'check_output',return_value='test-backend\n'),contextlib.redirect_stdout(io.StringIO()):installer.install(argparse.Namespace(demo_dir=self.demo,start=False))
 def test_campaign_schema_resolves_dependencies_in_a_fresh_process(self):
  import os,sys
  environment={**os.environ,'PYTHONPATH':str(ROOT/'BACKEND/SGA-CD-BACKEND'),'DATABASE_URL':'sqlite://','SECRET_KEY':'schema-test-only-not-real'}
  code="from app.services import campaign_schema; from app.models.campaigns import Campaign; from sqlalchemy.schema import CreateTable; from sqlalchemy.dialects import postgresql; assert 'workspace_assets' in Campaign.metadata.tables; str(CreateTable(Campaign.__table__).compile(dialect=postgresql.dialect()))"
  subprocess.run([sys.executable,'-c',code],env=environment,check=True,capture_output=True)
 def test_preserves_services_offline_state_and_keeps_secrets_out_of_overlay(self):
  for _ in range(2):
   self.execute();config=json.loads((self.demo/'compose.json').read_text())
   for service in ['web','flet-mobile','flet-desktop']:self.assertEqual(config['services'][service],self.original['services'][service])
   self.assertEqual(config['volumes'],self.original['volumes']);self.assertEqual(config['services']['backend']['environment']['SECRET_KEY'],'preserved-test-key')
  self.assertEqual((self.demo/'offline-sentinel.sqlite').read_bytes(),b'offline-data-must-remain')
  private=self.demo/'workspace.env';self.assertEqual(private.stat().st_mode&0o777,0o600);self.assertNotIn('test-provider-never-copy',private.read_text())
  for p in (self.demo/'workspace-overlays').rglob('*.py'):self.assertNotIn('test-interservice-token-not-real',p.read_text())
  self.assertEqual(len(list(self.demo.glob('workspace-backup-*'))),2)
 def test_refuses_to_replace_custom_backend_mount(self):
  config=json.loads((self.demo/'compose.json').read_text());config['services']['backend']['volumes'].append('/custom/main.py:/opt/backend/app/main.py:ro');path=self.demo/'compose.json';path.write_text(json.dumps(config));before=path.read_bytes()
  with self.assertRaises(SystemExit):self.execute()
  self.assertEqual(path.read_bytes(),before)
if __name__=='__main__':unittest.main()
