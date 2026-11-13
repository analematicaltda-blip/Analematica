"""Disposable Nginx verifies only pinned capture files bypass preview Basic auth."""
import argparse,base64,importlib.util,json,os,subprocess,tempfile,time,uuid
from pathlib import Path
from urllib.request import build_opener,ProxyHandler,Request
from urllib.error import HTTPError,URLError
import bcrypt
ROOT=Path(__file__).resolve().parents[3]
def run():
    parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
    if not args.run_local_disposable:parser.error('Explicit local disposable flag required')
    env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
    def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
    docker('info','--format','{{.ServerVersion}}');name='gc024-nginx-'+uuid.uuid4().hex[:12];started=False
    with tempfile.TemporaryDirectory(prefix='gc024-nginx-') as temp:
        base=Path(temp);spec=importlib.util.spec_from_file_location('capture_deploy',ROOT/'FRONTEND/deployment/prepare.py');deploy=importlib.util.module_from_spec(spec);spec.loader.exec_module(deploy);deploy.RUNTIME=base/'runtime';deploy.RUNTIME.mkdir();deploy.nginx();text=(deploy.RUNTIME/'nginx.conf').read_text()
        routes=[line.strip() for line in text.splitlines() if line.strip().startswith('location = /commercial-offline/')];assert len(routes)==15
        site=base/'sites';site.mkdir(mode=0o755);site.chmod(0o755);private=base/'private';private.mkdir(mode=0o755);private.chmod(0o755);password='synthetic-local-only-password';ht=private/'preview.htpasswd';ht.write_text('fixture:'+bcrypt.hashpw(password.encode(),bcrypt.gensalt(rounds=4)).decode()+'\n');ht.chmod(0o644)
        servers=[]
        for index,folder in enumerate(['sgacd','analematica','erp-capture']):
            root=site/folder;root.mkdir(mode=0o755);root.chmod(0o755);__import__('shutil').copytree(ROOT/'FRONTEND'/['SGA-CD-WEB.git','ANALEMATICA-FRONTEND','SGA-ERP-TUR-FRONTEND/public'][index]/'commercial-offline',root/'commercial-offline');[(p.chmod(0o644)) for p in (root/'commercial-offline').iterdir()];(root/'commercial-offline').chmod(0o755);(root/'admin.html').write_text('PRIVATE-ADMIN');(root/'private.json').write_text('PRIVATE-API');(root/'admin.html').chmod(0o644);(root/'private.json').chmod(0o644)
            location='\n'.join(routes[index*5:(index+1)*5]);servers.append('server {listen '+str(8080+index)+';root /sites/'+folder+';'+location+' location ^~ /commercial-offline/ {return 404;} location /api/ {auth_basic "Protected API";auth_basic_user_file /private/preview.htpasswd;try_files /private.json =404;} location / {auth_basic "Protected preview";auth_basic_user_file /private/preview.htpasswd;try_files $uri =404;} }')
        config=base/'nginx.conf';config.write_text('user nginx;worker_processes 1;pid /tmp/nginx.pid;error_log /dev/stderr warn;events {worker_connections 128;}http {include /etc/nginx/mime.types;access_log off;'+''.join(servers)+'}');config.chmod(0o644)
        client=build_opener(ProxyHandler({}));results=[]
        def request(port,path,auth=False):
            headers={'Authorization':'Basic '+base64.b64encode(('fixture:'+password).encode()).decode()} if auth else {}
            try:
                with client.open(Request('http://127.0.0.1:'+str(port)+path,headers=headers),timeout=3) as response:return response.status,response.read()
            except HTTPError as error:return error.code,error.read()
        try:
            docker('run','--pull=never','--rm','-d','--name',name,'--read-only','--tmpfs','/var/cache/nginx','--tmpfs','/var/run','--tmpfs','/tmp','-p','127.0.0.1::8080','-p','127.0.0.1::8081','-p','127.0.0.1::8082','--mount','type=bind,src='+str(site)+',dst=/sites,readonly','--mount','type=bind,src='+str(private)+',dst=/private,readonly','--mount','type=bind,src='+str(config)+',dst=/etc/nginx/nginx.conf,readonly','nginx:alpine');started=True
            for index in [0,1,2]:
                port=int(docker('port',name,str(8080+index)+'/tcp').rsplit(':',1)[1]);deadline=time.monotonic()+15
                while True:
                    try:status,body=request(port,'/commercial-offline/index.html');break
                    except (URLError,TimeoutError):
                        if time.monotonic()>deadline:
                            diagnostic=subprocess.run(['docker','--host=unix:///var/run/docker.sock','logs',name],env=env,capture_output=True,text=True,timeout=10)
                            raise RuntimeError('Local capture proxy did not become ready: '+(diagnostic.stdout+diagnostic.stderr)[-2500:])
                        time.sleep(.1)
                assert status==200 and b'html' in body,(status,body[:200])
                assert request(port,'/commercial-offline/worker.js')[0]==200
                assert request(port,'/commercial-offline/unknown.json')[0]==404
                assert request(port,'/admin.html')[0]==401
                assert request(port,'/api/private')[0]==401
                assert request(port,'/admin.html',True)==(200,b'PRIVATE-ADMIN')
                assert request(port,'/commercial-offline/../admin.html')[0]==401
                results.append({'site':['sgacd','analematica','erp'][index],'checks':7,'passed':True})
            print(json.dumps({'passed':True,'disposable':True,'nginx':'alpine','sites':results,'checks':21,'scope':'exact generated capture locations with isolated Basic-auth fixture; not full deployment/TLS/production','production_ready':False}))
        finally:
            if started:docker('stop','--time','2',name)
if __name__=='__main__':run()
