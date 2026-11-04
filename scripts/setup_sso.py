"""Prepare an isolated backend overlay and private SSO configuration for the demo."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlparse

parser=argparse.ArgumentParser()
parser.add_argument('--demo-dir',type=Path,default=Path.home()/'sgacd-demo')
parser.add_argument('--public-origin',default='')
parser.add_argument('--start',action='store_true',help='Build and restart only backend and the two Flet previews')
args=parser.parse_args()
repo=Path(__file__).resolve().parent.parent;demo=args.demo_dir.resolve()
origin=args.public_origin.rstrip('/')
if not origin and os.getenv('CODESPACE_NAME'):
    origin='https://'+os.environ['CODESPACE_NAME']+'-8080.'+os.getenv('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN','app.github.dev')
u=urlparse(origin)
if u.scheme!='https' or not u.netloc or u.path or u.query or u.fragment or u.username:
    raise SystemExit('Indica --public-origin https://tu-direccion-del-puerto-8080 (sin ruta).')
compose_path=demo/'compose.json'
config=json.loads(compose_path.read_text())
backend=config['services'].get('backend')
if not backend:raise SystemExit('No se encontró el servicio backend de la demo.')
if not any((isinstance(v,str) and v.split(':')[1:2]==['/state']) or (isinstance(v,dict) and v.get('target')=='/state') for v in backend.get('volumes',[])):
    raise SystemExit('El backend necesita un volumen persistente en /state para las solicitudes de acceso.')
compose=['docker','compose','-f',str(compose_path)]
state=demo/'sso-base-image.txt'
if state.exists():base=state.read_text().strip()
else:
    image=subprocess.check_output(compose+['images','-q','backend'],text=True).strip()
    if not image:raise SystemExit('Primero inicia el backend existente de la demo.')
    image_id=subprocess.check_output(['docker','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
    base='sgacd-sso-base:'+image_id.split(':')[-1][:16]
    subprocess.run(['docker','tag',image_id,base],check=True)
    state.write_text(base)
context=demo/'sso-image';context.mkdir(exist_ok=True)
for source,name in [('SGA-CD-BACKEND/app/services/sso_service.py','sso_service.py'),('SGA-CD-BACKEND/app/api/v1/endpoints/sso.py','sso.py')]:
    shutil.copy2(repo/source,context/name)
(context/'register.py').write_text('''from pathlib import Path
p=Path('/opt/backend/app/api/v1/api.py')
s=p.read_text()
if 'prefix="/sso"' not in s:
    p.write_text(s+'\\nfrom app.api.v1.endpoints import sso as shared_sso\\napi_router.include_router(shared_sso.router, prefix="/sso", tags=["Single Sign-On"])\\n')
''')
(context/'Dockerfile').write_text('FROM '+base+'''
COPY sso_service.py /opt/backend/app/services/sso_service.py
COPY sso.py /opt/backend/app/api/v1/endpoints/sso.py
COPY register.py /tmp/register_sso.py
RUN python /tmp/register_sso.py
''')
env_path=demo/'sso.env'
if not env_path.exists():
    with open(env_path,'x',opener=lambda path,flags:os.open(path,flags,0o600)) as stream:
        stream.write('SSO_PUBLIC_ORIGIN='+origin+'\nSSO_STATE_DB=/state/sso/flows.sqlite3\nSSO_GOOGLE_CLIENT_ID=\nSSO_GOOGLE_CLIENT_SECRET=\nSSO_MICROSOFT_CLIENT_ID=\nSSO_MICROSOFT_CLIENT_SECRET=\nSSO_ACCOUNTS_JSON={}\n')
backend['image']='sgacd-backend-sso:demo';backend['build']={'context':'./sso-image'}
envs=backend.setdefault('env_file',[])
if isinstance(envs,str):envs=[envs];backend['env_file']=envs
if str(env_path) not in envs:envs.append(str(env_path))
for name in ['flet-desktop','flet-mobile']:
    if name in config['services']:
        config['services'][name].setdefault('environment',{})['SGACD_API_BASE_URL']='http://backend:8000'
new=json.dumps(config,indent=2)+'\n'
if json.loads(compose_path.read_text())!=config:
    backup=demo/('compose.before-sso-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
    shutil.copy2(compose_path,backup);compose_path.write_text(new)
print('Configuración privada:',env_path)
print('No se sobrescribieron credenciales existentes. Proveedores deshabilitados hasta configurarlos.')
for provider in ['google','microsoft']:print('Callback '+provider+': '+origin+'/api/v1/sso/'+provider+'/callback')
if args.start:
    targets=['backend']+[name for name in ['flet-desktop','flet-mobile'] if name in config['services']]
    builds=['backend']+(['flet-desktop'] if 'flet-desktop' in targets else [])
    subprocess.run(compose+['build']+builds,check=True)
    subprocess.run(compose+['up','-d','--no-deps','--wait','--wait-timeout','180']+targets,check=True)
    subprocess.run(compose+['ps']+targets,check=True)
else: print('Preparado. Para construir e iniciar, repite con --start.')
