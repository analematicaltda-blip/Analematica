"""Real browser -> HTTP -> owned inbox; synthetic source and no outbound dispatch."""
import runpy,json,subprocess,tempfile,os,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
f=runpy.run_path(str(Path(__file__).with_name('pool08_inbox_http_check.py')),run_name='inbox_browser_setup');case=f['Checks'];case._class_cleanups=[]
try:
 case.setUpClass();targets=[]
 for name in ['sga-cd','erp-tur','analematica','gateway']:
  client,cred=case.extra[name] if name in ('sga-cd','gateway') else case.servers[name];prefix='/api/v1/mi-negocio/comercial/unified/crm/' if name=='erp-tur' else '/api/v1/commercial-unified/crm/';suffix='' if name=='sga-cd' else '/';query={} if name=='sga-cd' else {'provider_id':cred['provider_id']};ctx,event,signature,ref=f['seed'](client,prefix,suffix,query,'analematica' if name=='gateway' else name)
  contact=f['unwrap'](client.post(prefix+'commands'+suffix,params=query,json={'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Cliente de prueba '+name,'email':uuid.uuid4().hex+'@example.test','origin':'INBOX_BROWSER','phone':'+573'+str(uuid.uuid4().int%1000000000).zfill(9),'responsible_ref':ctx['actor_ref']}}))['contact_id'];targets.append({'name':name,'origin':str(client.base_url).rstrip('/'),'token':cred['token'],'provider':cred.get('provider_id'),'contact_id':contact,'thread_id':ref,'actor_ref':ctx['actor_ref']})
 with tempfile.TemporaryDirectory(prefix='inbox-browser-') as d:
  cfg=Path(d)/'private.json'
  with open(cfg,'x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(targets,stream)
  raise SystemExit(subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/pool08_inbox_browser.cjs'),str(cfg)],cwd=ROOT,env={**os.environ,'NODE_PATH':'/tmp/sgacd-full-web-deps/node_modules'},timeout=240).returncode)
finally:case.tearDownClass();case.doClassCleanups()
