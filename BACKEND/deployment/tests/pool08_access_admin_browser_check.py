"""Actual owned entry pages, native HTTP and gateway, controlled transport failures."""
import runpy,json,subprocess,tempfile,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='workspace_browser_setup');case=f['CRMHTTPChecks'];case._class_cleanups=[]
try:
 case.setUpClass();targets=[]
 for name in ('sga-cd','erp-tur','analematica','gateway'):
  client,cred=case.extra[name] if name in ('sga-cd','gateway') else case.servers[name];targets.append({'name':name,'origin':str(client.base_url).rstrip('/'),'token':cred['token'],'other_token':cred['other_token'],'staff_token':cred['staff_token'],'staff_ref':cred['staff_ref'],'provider':cred.get('provider_id')})
 with tempfile.TemporaryDirectory(prefix='gc023-workspace-') as d:
  cfg=Path(d)/'private.json'
  with open(cfg,'x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(targets,stream)
  raise SystemExit(subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/pool08_access_admin_browser.cjs'),str(cfg)],cwd=ROOT,env={**os.environ,'NODE_PATH':'/tmp/sgacd-full-web-deps/node_modules'},timeout=360).returncode)
finally:case.tearDownClass();case.doClassCleanups()
