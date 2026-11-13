"""Add and start the private Node 6 without changing existing demo services."""
import argparse
from datetime import datetime, timezone
from getpass import getpass
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--demo-dir',type=Path,default=Path.home()/'sgacd-demo')
parser.add_argument('--set-gemini-key',action='store_true')
parser.add_argument('--set-youtube-oauth',action='store_true')
parser.add_argument('--prepare-only',action='store_true')
parser.add_argument('--proxy-ca',type=Path)
args=parser.parse_args();repo=Path(__file__).resolve().parents[2];demo=args.demo_dir.resolve()
config_file=demo/'compose.json'
if not config_file.exists():raise SystemExit('No se encontró compose.json de la demo existente.')
config=json.loads(config_file.read_text());private=demo/'node6';private.mkdir(exist_ok=True,mode=0o700)
env=private/'node6.env'
if not env.exists():
    with open(env,'x',opener=lambda path,flags:os.open(path,flags,0o600)) as stream:
        stream.write('NODE6_TOKEN='+secrets.token_urlsafe(48)+'\nGEMINI_API_KEY=\nGEMINI_TEXT_MODEL=gemini-2.5-flash\nGEMINI_IMAGE_MODEL=gemini-2.5-flash-image\nCOLIBRI_BASE_URL=\nCOLIBRI_API_KEY=\nYOUTUBE_CLIENT_ID=\nYOUTUBE_CLIENT_SECRET=\nYOUTUBE_REFRESH_TOKEN=\n')
# Import a managed environment credential only when the private configuration is blank.
values=dict(line.split('=',1) for line in env.read_text().splitlines() if '=' in line and not line.startswith('#'))
managed=os.getenv('GEMINI_API_KEY','')
if managed and not values.get('GEMINI_API_KEY'):
    if '\n' in managed or '\r' in managed:raise SystemExit('La credencial del entorno no es válida.')
    values['GEMINI_API_KEY']=managed
    env.write_text('\n'.join(name+'='+value for name,value in values.items())+'\n')
env.chmod(0o600)
if args.set_gemini_key or args.set_youtube_oauth:
    values=dict(line.split('=',1) for line in env.read_text().splitlines() if '=' in line and not line.startswith('#'))
    if args.set_gemini_key:
        value=getpass('Clave Gemini API nueva (entrada oculta): ').strip()
        if not value:raise SystemExit('No se guardó una clave vacía.')
        values['GEMINI_API_KEY']=value
    if args.set_youtube_oauth:
        for name in ['YOUTUBE_CLIENT_ID','YOUTUBE_CLIENT_SECRET','YOUTUBE_REFRESH_TOKEN']:
            value=getpass(name+' (entrada oculta): ').strip()
            if not value:raise SystemExit('No se guardaron credenciales incompletas.')
            values[name]=value
    if any('\n' in value or '\r' in value for value in values.values()):raise SystemExit('Valor no válido.')
    env.write_text('\n'.join(name+'='+value for name,value in values.items())+'\n');env.chmod(0o600)
service={'image':'sgacd-node6:demo','build':{'context':str(Path(__file__).resolve().parents[2] / 'BACKEND/infra/node6')},'init':True,'env_file':[str(env)],'ports':['127.0.0.1:8606:8606'],'volumes':['node6_state:/state'],'mem_limit':'768m','cpus':1.0,'pids_limit':128,'cap_drop':['ALL'],'security_opt':['no-new-privileges:true'],'restart':'unless-stopped','healthcheck':{'test':['CMD','python','-c',"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8606/health',timeout=5)"],'interval':'5s','timeout':'10s','retries':20,'start_period':'20s'}}
if 'node6' in config['services'] and config['services']['node6']!=service:raise SystemExit('El nodo 6 ya tiene otra configuración; se conservó.')
previous=json.loads(json.dumps(config));config['services']['node6']=service;config.setdefault('volumes',{}).setdefault('node6_state',{})
if config!=previous:
    backup=demo/('compose.before-node6-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json');shutil.copy2(config_file,backup)
    config_file.write_text(json.dumps(config,indent=2)+'\n')
# Import this fragment through Matrix's supported MCP registration; do not edit its source or managed projection.
fragment=private/'matrix-mcp.json'
bridge=json.loads(fragment.read_text()) if fragment.exists() else {'mcpServers':{}}
bridge.setdefault('mcpServers',{})['sgacd-node6']={'command':'python3','args':[str(Path(__file__).resolve().parents[2] / 'BACKEND/tools/node6_mcp_stdio.py'),'--env-file',str(env),'--url','http://127.0.0.1:8606']}
fragment.write_text(json.dumps(bridge,indent=2)+'\n')
print('Nodo 6 preparado. Credenciales privadas:',env)
print('Matrix MCP: fragmento preparado en',private/'matrix-mcp.json','; requiere registro en el cliente.')
if args.prepare_only:raise SystemExit(0)
compose=['docker','compose','-f',str(config_file)]
if args.proxy_ca:
    cert=args.proxy_ca.resolve(strict=True);override=private/'build-ca.json'
    override.write_text(json.dumps({'services':{'node6':{'build':{'secrets':['node6_ca']}}},'secrets':{'node6_ca':{'file':str(cert)}}}))
    # Compose can set the mounted secret ID independently of its top-level name.
    data=json.loads(override.read_text());data['services']['node6']['build']['secrets']=[{'source':'node6_ca','target':'proxy_ca'}]
    data['services']['node6']['volumes']=[str(cert)+':/run/node6-proxy-ca.pem:ro']
    data['services']['node6']['environment']={'REQUESTS_CA_BUNDLE':'/run/node6-proxy-ca.pem'}
    override.write_text(json.dumps(data))
    compose+=['-f',str(override)]
subprocess.run(compose+['build','node6'],check=True)
subprocess.run(compose+['up','-d','--no-deps','--wait','--wait-timeout','180','node6'],check=True)
subprocess.run(compose+['ps','node6'],check=True)
print('Puerto 8606: mantenlo privado. No se descargaron pesos LLM ni se publicaron videos.')
