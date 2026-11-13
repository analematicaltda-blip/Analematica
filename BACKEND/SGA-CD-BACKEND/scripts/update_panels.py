"""Install first-party panels as additive read-only overlays on the existing demo.
Never rebuild the database, alter Flet/offline state, or copy worker credentials to web.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BACKEND_FILES=['api/v1/endpoints/platform.py','services/platform/__init__.py','services/platform/registry.py','api/v1/endpoints/resources.py','services/resources/__init__.py','services/resources/catalog.py','services/resources/security.py','services/resources/provider_catalog.json','api/v1/endpoints/assistance_control.py','services/assistance/control.py','services/assistance/control_crypto.py','services/assistance/control_policy.json','models/assistance.py','api/v1/endpoints/assistance.py','services/assistance/__init__.py','services/assistance/engine.py','services/assistance/duet.py','services/assistance/schema.py','services/assistance/catalog.json','services/assistance/policy.txt','api/v1/endpoints/meta_webhooks.py','services/instagram_service.py','api/v1/endpoints/instagram.py','models/advertising.py','services/advertising_schema.py','services/meta_ads_graph.py','services/meta_ads_service.py','api/v1/endpoints/meta_ads.py','api/v1/endpoints/meta.py','services/corporate_policy.py','services/corporate_commands.py','models/corporate.py','api/v1/endpoints/corporate.py','models/workspace.py','services/workspace_service.py','services/workspace_guard.py','services/workspace_schema.py','api/v1/endpoints/workspace.py','services/plan_capability_service.py','crud/tenancy.py','schemas/tenancy.py','models/campaigns.py','services/campaign_service.py','services/campaign_schema.py','services/campaign_worker.py','api/v1/endpoints/campaigns.py','api/v1/endpoints/admin.py','models/institutional.py','services/role_contracts.py','services/institutional_service.py','services/institutional_schema.py','api/v1/endpoints/institutional.py']

def run(argv,**kw):return subprocess.run(argv,check=True,**kw)
def ensure_web_running(compose):
 # The web service may have been stopped before this update (or by Codespaces).
 # Start only it; keep database/Flet volumes and already-running services intact.
 try:
  run(compose+['up','-d','--no-deps','--wait','--wait-timeout','90','web'])
 except subprocess.CalledProcessError:
  raise SystemExit('No se pudo iniciar el servicio web. Revisa docker compose -f '+compose[3]+' logs --tail 60 web. No se eliminaron volúmenes.') from None
 run(compose+['exec','-T','web','nginx','-t'])
 run(compose+['exec','-T','web','nginx','-s','reload'])

def install(args):
 repo=Path(__file__).resolve().parents[3];demo=args.demo_dir.resolve();path=demo/'compose.json'
 if not path.exists():raise SystemExit('No se encontró compose.json. No se modificó la demo.')
 config=json.loads(path.read_text());backend=config['services'].get('backend')
 if not backend:raise SystemExit('No existe el backend de la demo.')
 compose=['docker','compose','-f',str(path)]
 container=subprocess.check_output(compose+['ps','-q','backend'],text=True).strip()
 if not container:raise SystemExit('Primero inicia el backend existente.')
 run(['docker','exec',container,'python','-c','import requests,cryptography.fernet; import app.models.user'],stdout=subprocess.DEVNULL)
 run([sys.executable,str(repo/'FRONTEND/SGA-CD-WEB.git/scripts/publish.py'),'--demo-dir',str(demo),'--check'])
 stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f');backup=demo/('workspace-backup-'+stamp);backup.mkdir(mode=0o700)
 shutil.copy2(path,backup/'compose.json');(backup/'compose.json').chmod(0o600)
 overlay=demo/'workspace-overlays'/stamp
 overlay.mkdir(parents=True,mode=0o755)
 # Read the actual running files, retaining existing SSO, routers and runtime fixes.
 for relative in ['api/v1/api.py','main.py']:
  saved=backup/relative;saved.parent.mkdir(parents=True,exist_ok=True)
  run(['docker','cp',container+':/opt/backend/app/'+relative,str(saved)],stdout=subprocess.DEVNULL)
  source=saved.read_text()
  if relative=='api/v1/api.py' and 'SGACD_WORKSPACE_ROUTER' not in source and 'prefix="/workspace"' not in source and "prefix='/workspace'" not in source:
   source+='\n# SGACD_WORKSPACE_ROUTER\nfrom app.api.v1.endpoints import workspace as integrated_workspace\napi_router.include_router(integrated_workspace.router, prefix="/workspace", tags=["Role workspaces"])\n'
  if relative=='api/v1/api.py' and 'prefix="/platform"' not in source:
   source+='\nfrom app.api.v1.endpoints import platform\napi_router.include_router(platform.router,prefix="/platform",tags=["Shared platform"])\n'
  if relative=='api/v1/api.py' and 'SGACD_ASSISTANCE_ROUTER' not in source and 'prefix="/assistance"' not in source:
   source+='\n# SGACD_ASSISTANCE_ROUTER\nfrom app.api.v1.endpoints import assistance as platform_assistance\napi_router.include_router(platform_assistance.router, prefix="/assistance", tags=["User assistance"])\n'
  if relative=='main.py' and 'WorkspaceLegacyGuard' not in source:
   source+='\n# SGACD_WORKSPACE_GUARD\nfrom app.services.workspace_guard import WorkspaceLegacyGuard\napp.add_middleware(WorkspaceLegacyGuard)\n'
  target=overlay/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source)
 for relative in BACKEND_FILES:
  target=overlay/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/'BACKEND/SGA-CD-BACKEND/app'/relative,target);target.chmod(0o644)
 for relative in BACKEND_FILES+['api/v1/api.py','main.py']:
  target='/opt/backend/app/'+relative;new=str(overlay/relative)+':'+target+':ro';volumes=backend.setdefault('volumes',[])
  def destination(value):return value.split(':')[1] if isinstance(value,str) and ':' in value else value.get('target') if isinstance(value,dict) else None
  existing=[value for value in volumes if destination(value)==target]
  for mount in existing:
   source=Path(mount.split(':')[0] if isinstance(mount,str) else mount.get('source','')).resolve()
   if not any(source.is_relative_to(root) for root in [demo/'workspace-overlay',demo/'workspace-overlays']):raise SystemExit('Ya existe un montaje distinto en '+target+'. Se conservó compose.json; revisa '+str(backup))
  volumes[:]=[mount for mount in volumes if destination(mount)!=target]
  volumes.append(new)
 # Reuse a previously configured Node 6; only prepare it when absent.
 if 'node6' not in config['services']:
  run([sys.executable,str(repo/'BACKEND/tools/start_node6.py'),'--demo-dir',str(demo),'--prepare-only'])
  node_config=json.loads(path.read_text());config['services']['node6']=node_config['services']['node6'];config['volumes']=node_config.get('volumes',config.get('volumes',{}))
 node=config['services']['node6'];envs=node.get('env_file',[]);envs=[envs] if isinstance(envs,str) else envs
 values={}
 for item in envs:
  envpath=Path(item if isinstance(item,str) else item['path']);envpath=envpath if envpath.is_absolute() else demo/envpath
  if envpath.exists():
   for line in envpath.read_text().splitlines():
    if line.startswith('NODE6_TOKEN='):values['NODE6_TOKEN']=line.split('=',1)[1]
 token=values.get('NODE6_TOKEN')
 if not token or any(c in token for c in '\r\n'):raise SystemExit('NODE6_TOKEN no está configurado en el archivo privado del nodo.')
 private=demo/'workspace.env'
 private_values=dict(line.split('=',1) for line in private.read_text().splitlines() if '=' in line and not line.startswith('#')) if private.exists() else {}
 private_values.setdefault('CAMPAIGN_DELIVERY_ENABLED','0')
 if private_values['CAMPAIGN_DELIVERY_ENABLED'] not in ['0','1']:raise SystemExit('Modo de campañas no válido; utiliza 0 para preparación sin envíos.')
 node.setdefault('environment',{})['NODE6_CAMPAIGNS_ENABLED']=private_values['CAMPAIGN_DELIVERY_ENABLED']
 private_values.update(NODE6_URL='http://node6:8606',NODE6_TOKEN=token)
 with open(private,'w',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:stream.write('\n'.join(key+'='+value for key,value in private_values.items())+'\n')
 private.chmod(0o600)
 backend_env=backend.setdefault('env_file',[])
 if isinstance(backend_env,str):backend_env=[backend_env];backend['env_file']=backend_env
 if str(private) not in backend_env:backend_env.append(str(private))
 # Explicit environment values take precedence over env_file: preserve all except managed pair.
 if isinstance(backend.get('environment'),dict):
  for key in ['NODE6_URL','NODE6_TOKEN','CAMPAIGN_DELIVERY_ENABLED']:backend['environment'].pop(key,None)
 elif isinstance(backend.get('environment'),list):backend['environment']=[line for line in backend['environment'] if line.split('=',1)[0] not in ['NODE6_URL','NODE6_TOKEN','CAMPAIGN_DELIVERY_ENABLED']]
 for filename in ['engine.py','main.py','youtube.py','adaptation.py','social.py','campaign_dispatch.py']:
  copied=overlay/'node6'/filename;copied.parent.mkdir(exist_ok=True);shutil.copy2(repo/'BACKEND/infra/node6'/filename,copied);copied.chmod(0o644)
  target='/app/infra/node6/'+filename;value=str(copied)+':'+target+':ro';volumes=node.setdefault('volumes',[])
  for mount in volumes:
   if destination(mount)==target:
    source=Path(mount.split(':')[0] if isinstance(mount,str) else mount.get('source','')).resolve()
    if not any(source.is_relative_to(root) for root in [demo/'workspace-overlay',demo/'workspace-overlays',repo/'BACKEND/infra/node6']):raise SystemExit('Montaje Node 6 personalizado; no se sustituyó.')
  volumes[:]=[mount for mount in volumes if destination(mount)!=target]
  volumes.append(value)
 # The scheduler uses the same backend code, credentials and DB, with no listening port.
 import copy
 scheduler=copy.deepcopy(backend)
 for key in ['ports','expose','container_name','depends_on']:scheduler.pop(key,None)
 scheduler['command']=['python','-m','app.services.campaign_worker']
 scheduler['restart']='unless-stopped'
 scheduler['healthcheck']={'test':['CMD','python','-c',"from pathlib import Path; import time; p=Path('/tmp/sgacd-campaign-heartbeat'); assert p.exists() and time.time()-p.stat().st_mtime<600"],'interval':'30s','timeout':'5s','retries':5,'start_period':'30s'}
 scheduler.setdefault('labels',{})['io.sgacd.managed']='campaign-scheduler'
 previous_scheduler=config['services'].get('campaign-scheduler')
 if previous_scheduler and previous_scheduler.get('labels',{}).get('io.sgacd.managed')!='campaign-scheduler':raise SystemExit('Ya existe un planificador personalizado; se conservó compose.json.')
 config['services']['campaign-scheduler']=scheduler
 path.write_text(json.dumps(config,indent=2)+'\n');path.chmod(0o600)
 print('Respaldo privado:',backup)
 print('Integración preparada; conserva usuarios, credenciales, volúmenes y bases Flet.')
 if not args.start:return
 if subprocess.run(['docker','image','inspect',node.get('image','sgacd-node6:demo')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:run(compose+['build','node6'])
 run(compose+['up','-d','--no-deps','--force-recreate','--wait','--wait-timeout','180','node6','backend'])
 run(compose+['exec','-T','backend','python','-m','app.services.workspace_schema'])
 run(compose+['exec','-T','backend','python','-m','app.services.campaign_schema'])
 run(compose+['exec','-T','backend','python','-m','app.services.institutional_schema'])
 run(compose+['exec','-T','backend','python','-m','app.services.assistance.schema'])
 run(compose+['exec','-T','backend','python','-m','app.services.assistance.control_crypto'])
 run(compose+['up','-d','--no-deps','--force-recreate','--wait','--wait-timeout','180','campaign-scheduler'])
 run([sys.executable,str(repo/'FRONTEND/SGA-CD-WEB.git/scripts/publish.py'),'--demo-dir',str(demo)])
 ensure_web_running(compose)
 run(compose+['ps','backend','node6','web','campaign-scheduler'])
 print('Actualización aplicada. Abre el puerto 8080 y recarga con Ctrl+Shift+R. Los accesos están en app.html#/ROL/inicio.')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--demo-dir',type=Path,default=Path.home()/'sgacd-demo');parser.add_argument('--start',action='store_true');install(parser.parse_args())
if __name__=='__main__':main()
