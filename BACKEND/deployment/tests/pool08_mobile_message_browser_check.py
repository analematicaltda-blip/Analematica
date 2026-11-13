"""Real HTTP email campaign UI, synthetic recipients only and no message dispatch."""
import runpy,json,subprocess,tempfile,os,uuid
from pathlib import Path
from unittest.mock import patch
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parents[3]
f=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/pool08_crm_http_check.py'),run_name='campaign_browser_setup');case=f['CRMHTTPChecks'];case._class_cleanups=[];env=patch.dict(os.environ,{'GC017_MOBILE_FIXTURE':'1'});env.start()
try:
 case.setUpClass();targets=[]
 for name in ['sga-cd','erp-tur','analematica','gateway']:
  client,cred=case.extra[name] if name in ('sga-cd','gateway') else case.servers[name];prefix='/api/v1/mi-negocio/comercial/unified/crm/' if name=='erp-tur' else '/api/v1/commercial-unified/crm/';suffix='' if name=='sga-cd' else '/';query={} if name=='sga-cd' else {'provider_id':cred['provider_id']}
  ctx=client.get(prefix+'context'+suffix,params=query).json();ctx=ctx.get('data',ctx);data={'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Contacto '+name,'email':uuid.uuid4().hex+'@example.test','origin':'BROWSER_MOBILE','phone':'+573'+str(uuid.uuid4().int%1000000000).zfill(9),'responsible_ref':ctx['actor_ref']}};r=client.post(prefix+'commands'+suffix,params=query,json=data);assert r.status_code==200;r=r.json();ref=r.get('data',r)['contact_id'];r=client.post(prefix+'commands'+suffix,params=query,json={'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':ref,'expected_revision':1,'data':{'channel':'EMAIL','purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}});assert r.status_code==200
  for channel,revision in [('SMS',2),('MMS',3),('WHATSAPP',4)]:
   rr=client.post(prefix+'commands'+suffix,params=query,json={'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':ref,'expected_revision':revision,'data':{'channel':channel,'purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}});assert rr.status_code==200
  from PIL import Image
  import io,base64,hashlib
  image=io.BytesIO();Image.new('RGB',(32,32),(17,48,75)).save(image,format='PNG');metadata={'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':{'title':'Activo móvil sintético','classification':'MARKETING','brand':{'name':'Empresa','tagline':'Prueba','template':'SQUARE'},'rights':{'holder':'Fixture','license':'OWNED','reference':'Fuente creada en prueba','valid_until':None,'public_web':True}}};asset=client.post(prefix+'library-upload'+suffix,params=query,content=image.getvalue(),headers={'Content-Type':'image/png','X-Library-Metadata':base64.b64encode(json.dumps(metadata).encode()).decode()});assert asset.status_code==200;asset=asset.json();asset=asset.get('data',asset)['item_id']
  for op,revision,data in [('approve',1,{'rights_confirmed':True,'privacy_reviewed':True}),('publish',2,{'confirmed':True})]:
   rr=client.post(prefix+'library-commands'+suffix,params=query,json={'request_id':str(uuid.uuid4()),'operation':op,'item_id':asset,'expected_revision':revision,'data':data});assert rr.status_code==200
  targets.append({'name':name,'origin':str(client.base_url).rstrip('/'),'token':cred['token'],'provider':cred.get('provider_id'),'contact_id':ref,'asset_id':asset})
 with tempfile.TemporaryDirectory(prefix='mobile-browser-') as d:
  cfg=Path(d)/'private.json'
  with open(cfg,'x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(targets,stream)
  raise SystemExit(subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/pool08_mobile_message_browser.cjs'),str(cfg)],cwd=ROOT,env={**os.environ,'NODE_PATH':'/tmp/sgacd-full-web-deps/node_modules'},timeout=240).returncode)
finally:case.tearDownClass();case.doClassCleanups();env.stop()
