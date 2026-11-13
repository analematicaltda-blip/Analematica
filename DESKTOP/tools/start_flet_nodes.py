"""Prepare, build, start and verify both isolated Flet preview nodes."""
import argparse
from pathlib import Path
import json
import os
import subprocess
import sys

parser=argparse.ArgumentParser()
parser.add_argument('--demo-dir',type=Path,default=Path.home()/'sgacd-demo')
parser.add_argument('--proxy-ca',type=Path,help='CA de proxy para construir en entornos administrados')
args=parser.parse_args()
repo=Path(__file__).resolve().parents[2]
demo=args.demo_dir.resolve()
def run(command,**kwargs):
    subprocess.run(command,check=True,**kwargs)
run([sys.executable,str(Path(__file__).resolve().parents[2] / 'DESKTOP/tools/setup_flet_previews.py'),'--demo-dir',str(demo)])
compose=['docker','compose','-f',str(demo/'compose.json')]
if args.proxy_ca:
    cert=args.proxy_ca.resolve(strict=True)
    override=demo/'compose.flet-build.json'
    override.write_text(json.dumps({'services':{'flet-desktop':{'build':{'secrets':['proxy_ca']}}},'secrets':{'proxy_ca':{'file':str(cert)}}},indent=2))
    compose+=['-f',str(override)]
run(compose+['build','flet-desktop'])
run(compose+['up','-d','--wait','--wait-timeout','180','flet-desktop','flet-mobile'])
checker=(Path(__file__).resolve().parents[2] / 'DESKTOP/tools/flet_preview/check_session.py').read_bytes()
for name,port in [('flet-desktop',8501),('flet-mobile',8502)]:
    run(compose+['exec','-T',name,'python','-',str(port)],input=checker)
run(compose+['ps','flet-desktop','flet-mobile'])
print('\nNodos Flet listos. Mantén privados los puertos 8501 (escritorio) y 8502 (móvil).')
name=os.getenv('CODESPACE_NAME'); domain=os.getenv('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN','app.github.dev')
for label,port in [('Escritorio',8501),('Móvil',8502)]:
    print(label+': '+(f'https://{name}-{port}.{domain}' if name else f'http://127.0.0.1:{port}'))
print('Son vistas previas: su login SQLite todavía es independiente del backend web.')
