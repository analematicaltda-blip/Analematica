"""Add isolated Flet web previews to the existing Codespaces demo."""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import argparse

repo = Path(__file__).resolve().parent.parent
package = Path(__file__).resolve().parent / "flet_preview"
parser = argparse.ArgumentParser()
parser.add_argument('--demo-dir', type=Path, default=Path.home() / 'sgacd-demo')
args = parser.parse_args()
demo = args.demo_dir.resolve()
config_file = demo / 'compose.json'
if not config_file.exists() or not (repo/'SGA-CD-APP.git/main.py').exists():
    raise SystemExit('Ejecuta desde /workspaces/SGA-CD con la demo ya configurada.')
config = json.loads(config_file.read_text())
original = json.loads(json.dumps(config))
for name, folder, port in [('flet-desktop','SGA-CD-APP.git',8501),('flet-mobile','SGA-CD-APK.git',8502)]:
    service = {
        'image': 'sgacd-flet-preview:0.25.2',
        'init': True,
        'environment': {
            'SGACD_FLET_CLIENT':'/client',
            'FLET_SERVER_PORT':str(port),
            'FLET_SERVER_IP':'0.0.0.0',
            'FLET_FORCE_WEB_SERVER':'true',
            'FLET_APP_STORAGE_DATA':'/state'
        },
        'volumes':[f'{repo/folder}:/client:ro',f'{name}_state:/state'],
        'ports':[f'127.0.0.1:{port}:{port}'],
        'mem_limit':'768m',
        'healthcheck':{
            'test':['CMD','python','-c',f"import urllib.request; urllib.request.urlopen('http://127.0.0.1:{port}/',timeout=5)"],
            'interval':'5s','timeout':'10s','start_period':'30s','retries':20
        },
        'restart':'unless-stopped'
    }
    if name=='flet-desktop': service['build']={'context':'./flet-image'}
    existing_api = config['services'].get(name,{}).get('environment',{}).get('SGACD_API_BASE_URL')
    if existing_api:
        service['environment']['SGACD_API_BASE_URL'] = existing_api
    if name in config['services'] and config['services'][name] != service:
        raise SystemExit(f'{name} tiene otra configuración. Se conservó sin cambios.')
    config['services'][name]=service
    config.setdefault('volumes',{}).setdefault(f'{name}_state',{})
context = demo / 'flet-image'
context.mkdir(exist_ok=True)
for file in ['run_preview.py', 'requirements-preview.txt']:
    shutil.copy2(package/file, context/file)
(context/'Dockerfile').write_text('''FROM python:3.12-slim
COPY requirements-preview.txt /tmp/requirements-preview.txt
RUN --mount=type=secret,id=proxy_ca if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; pip install --no-cache-dir -r /tmp/requirements-preview.txt
COPY run_preview.py /opt/run_preview.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /state
CMD ["python", "/opt/run_preview.py"]
''')
backup=demo/('compose.before-flet-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
if config != original:
    shutil.copy2(config_file,backup)
    config_file.write_text(json.dumps(config,indent=2))
else:
    print('Los nodos ya estaban configurados; se conservaron sus servicios y volúmenes.')
print('Previsualizaciones preparadas: escritorio 8501, móvil 8502.')
print('Mantén ambos puertos privados. El acceso Google/Microsoft requiere configurar SSO; los módulos locales conservan su SQLite.')
