"""Node 7 corporate gateway. Copy only public assets; reuse the existing SGA database."""
import argparse,json,os,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
PUBLIC=['platform.html','js/platform.js','resources.html','js/resources.js','control.html','js/control.js','content.html','js/content.js','css/content.css','assistance.html','js/assistance.js','css/assistance.css','js/instagram.js','config/meta-public.json','js/meta-setup.js','js/meta-ads.js','css/meta-ads.css','login.html','css/console.css','js/login.js','index.html','admin.html','assets/analema-logo.svg','css/style.css','css/admin.css','js/main.js','js/admin.js','js/connection.js','agents/analematica_army.js']
def prepare(demo,port,repo):
    demo=demo.resolve();path=demo/'compose.json'
    if not 1024<=port<=65535:raise ValueError('Puerto no válido.')
    config=json.loads(path.read_text())
    if not all(key in config['services'] for key in ['backend','web']):raise ValueError('Se necesitan los servicios backend y web existentes.')
    previous=config['services'].get('analematica')
    if previous and previous.get('labels',{}).get('io.sgacd.managed')!='analematica':raise ValueError('Existe un servicio Analemática personalizado. No se sobrescribió.')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f');release=demo/'analematica'/'releases'/stamp;site=release/'site';site.mkdir(parents=True)
    for name in PUBLIC:
        source=repo/'FRONTEND/ANALEMATICA-FRONTEND'/name
        if source.is_symlink() or not source.is_file():raise ValueError('Archivo público ausente o no permitido: '+name)
        target=site/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);target.chmod(0o644)
    for directory in [site,*[p for p in site.rglob('*') if p.is_dir()]]:directory.chmod(0o755)
    nginx=release/'nginx.conf';shutil.copy2(repo/'BACKEND/ANALEMATICA-BACKEND/deployment/nginx.conf',nginx)
    backup=release/'compose.before.json';shutil.copy2(path,backup);backup.chmod(0o600)
    config['services']['analematica']={'image':config['services']['web'].get('image','nginx:alpine'),'restart':'unless-stopped','labels':{'io.sgacd.managed':'analematica'},'ports':[f'127.0.0.1:{port}:80'],'volumes':[str(site)+':/usr/share/nginx/html:ro',str(nginx)+':/etc/nginx/conf.d/default.conf:ro'],'depends_on':{'web':{'condition':'service_started'}},'healthcheck':{'test':['CMD-SHELL','wget -Y off -q -O /dev/null http://127.0.0.1/healthz && wget -Y off -q -O /dev/null http://127.0.0.1/ || exit 1'],'interval':'10s','timeout':'3s','retries':6}}
    web_networks=config['services']['web'].get('networks')
    if web_networks is not None:config['services']['analematica']['networks']=web_networks
    temporary=path.with_suffix('.analematica.tmp');temporary.write_text(json.dumps(config,indent=2)+'\n');temporary.chmod(0o600);os.replace(temporary,path)
    return release

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--demo-dir',type=Path,default=Path.home()/'sgacd-demo');parser.add_argument('--port',type=int,default=8090);parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args();repo=Path(__file__).resolve().parents[3]
    if not (args.demo_dir/'compose.json').is_file():raise SystemExit('No existe la demo SGA-CD. No se modificó ningún servicio.')
    if not args.prepare_only:
        subprocess.run([sys.executable,str(repo/'BACKEND/SGA-CD-BACKEND/scripts/update_panels.py'),'--demo-dir',str(args.demo_dir),'--start'],check=True)
    release=prepare(args.demo_dir,args.port,repo);compose=['docker','compose','-f',str(args.demo_dir.resolve()/'compose.json')]
    subprocess.run(compose+['config','--quiet'],check=True)
    if args.prepare_only:print('Nodo preparado; no se iniciaron servicios.');return
    subprocess.run(compose+['up','-d','--no-deps','--wait','--wait-timeout','90','analematica'],check=True)
    subprocess.run(compose+['exec','-T','analematica','nginx','-t'],check=True)
    print(f'Analemática: puerto {args.port}. Landing / · Ingreso del dueño /login.html · Consola central /admin.html · SGA-CD público /sga/.')
    print('Conserva la visibilidad privada en Codespaces. Respaldo de configuración:',release/'compose.before.json')
if __name__=='__main__':main()
