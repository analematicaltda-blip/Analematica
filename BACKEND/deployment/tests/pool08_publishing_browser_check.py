"""Desktop/mobile publication calendar against real disposable HTTP backends."""
import runpy,json,subprocess,tempfile,os
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
f=runpy.run_path(str(Path(__file__).with_name('pool08_publishing_http_check.py')),run_name='publishing_browser_setup');case=f['Checks'];case._class_cleanups=[]
try:
 case.setUpClass();targets=[]
 for name in ['sga-cd','erp-tur','analematica','gateway']:
  client,cred=case.extra[name] if name in ('sga-cd','gateway') else case.servers[name];prefix='/api/v1/mi-negocio/comercial/unified/crm/' if name=='erp-tur' else '/api/v1/commercial-unified/crm/';suffix='' if name=='sga-cd' else '/';query={} if name=='sga-cd' else {'provider_id':cred['provider_id']};asset=f['seed'](client,prefix,suffix,query);targets.append({'name':name,'origin':str(client.base_url).rstrip('/'),'token':cred['token'],'provider':cred.get('provider_id'),'asset_id':asset['item_id']})
 with tempfile.TemporaryDirectory(prefix='publishing-browser-') as d:
  cfg=Path(d)/'private.json'
  with open(cfg,'x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(targets,stream)
  raise SystemExit(subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/pool08_publishing_browser.cjs'),str(cfg)],cwd=ROOT,env={**os.environ,'NODE_PATH':'/tmp/sgacd-full-web-deps/node_modules'},timeout=240).returncode)
finally:case.tearDownClass();case.doClassCleanups()
