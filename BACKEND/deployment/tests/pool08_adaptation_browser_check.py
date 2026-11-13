"""Run owned browser clients against real private CRM HTTP fixture backends."""
import runpy,unittest,json,subprocess,tempfile,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
fixture=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/pool08_crm_http_check.py'),run_name='crm_browser_harness')
case=fixture['CRMHTTPChecks'];case._class_cleanups=[]
from unittest.mock import patch
from PIL import Image
from PIL import PngImagePlugin
info=PngImagePlugin.PngInfo();info.add_text('private_marker','PRIVATE_LIBRARY_METADATA')
Image.new('RGBA',(64,32),(10,40,80,180)).save('/tmp/gc015-browser-original.png',pnginfo=info)
with open('/tmp/gc015-browser-original.png','ab') as stream:stream.write(b'PRIVATE_APPENDIX')
subprocess.run(['ffmpeg','-v','error','-nostdin','-f','lavfi','-i','color=c=blue:s=160x90:r=24:d=1','-f','lavfi','-i','sine=frequency=330:duration=1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-threads','1','-shortest','-y','/tmp/gc015-browser-original.mp4'],capture_output=True,check=True,timeout=20)
env=patch.dict(os.environ,{'COMMERCIAL_QUOTE_LINK_KEY':'synthetic-quotation-test-key-32-chars-only'});env.start()
try:
 case.setUpClass()
 targets=[]
 for name in ('sga-cd','erp-tur','analematica','gateway'):
  pair=case.extra[name] if name in ('sga-cd','gateway') else case.servers[name]
  client,cred=pair
  targets.append({'name':name,'origin':str(client.base_url).rstrip('/'),'token':cred['token'],'actor':cred['actor_ref'],'provider':cred.get('provider_id'),'accounts':cred.get('sale_accounts'),'day':cred.get('day')})
 with tempfile.TemporaryDirectory(prefix='gc015-browser-') as directory:
  config=Path(directory)/'private.json'
  with open(config,'x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(targets,stream)
  result=subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/pool08_adaptation_browser.cjs'),str(config)],cwd=ROOT,env={**os.environ,'NODE_PATH':'/tmp/sgacd-full-web-deps/node_modules'},timeout=240)
  raise SystemExit(result.returncode)
finally:
 case.tearDownClass();case.doClassCleanups();env.stop()
