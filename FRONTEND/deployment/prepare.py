"""Prepare private loopback web previews; never publish source directories or credentials."""
from pathlib import Path
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import json
import os
import secrets
import shutil
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = HERE / '.runtime'
PRIVATE = HERE / 'private'

def private_file(path, data):
    with open(path, 'x', opener=lambda name, flags: os.open(name, flags, 0o600)) as stream:
        stream.write(data)

def certificate():
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    keyfile = PRIVATE / 'localhost.key'
    certfile = PRIVATE / 'localhost.crt'
    if keyfile.exists() and certfile.exists():
        return
    if keyfile.exists() or certfile.exists():
        raise RuntimeError('Certificado incompleto; conserva las claves existentes y revisa private/.')
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, 'localhost')])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=30))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost'), x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]), critical=False)
            .sign(key, hashes.SHA256()))
    private_file(keyfile, key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode())
    private_file(certfile, cert.public_bytes(serialization.Encoding.PEM).decode())

def credentials():
    import bcrypt
    path = PRIVATE / 'preview-access.json'
    if path.exists():
        result = json.loads(path.read_text())
    else:
        result = {name: {'username': 'vista_' + name, 'password': secrets.token_urlsafe(24)} for name in ['sgacd', 'analematica', 'erp', 'turismo']}
        private_file(path, json.dumps(result, indent=2) + '\n')
    for name, item in result.items():
        target = PRIVATE / (name + '.htpasswd')
        if not target.exists():
            private_file(target, item['username'] + ':' + bcrypt.hashpw(item['password'].encode(), bcrypt.gensalt(rounds=12)).decode() + '\n')
    return result

def offline_capture(destination):
    spec=importlib.util.spec_from_file_location('offline_capture_assets',HERE/'accounting_offline_assets.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.install_assets(destination)

def public_assets():
    site = RUNTIME / 'sites'
    for name in ['sgacd', 'analematica']:
        folder = site / name
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
    source = ROOT / 'FRONTEND/SGA-CD-WEB.git'
    allowed = {'.html', '.js', '.css', '.json', '.png', '.jpg', '.jpeg', '.svg', '.webp', '.ico', '.woff', '.woff2', '.webmanifest', '.mp4'}
    for parent in ['js', 'css', 'assets']:
        for path in (source / parent).rglob('*'):
            if path.is_file() and not path.is_symlink() and path.suffix.lower() in allowed:
                target = site / 'sgacd' / path.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
    for name in ['index.html', 'login.html', 'app.html', 'register.html', 'privacy.html', 'terms.html', '404.html', 'favicon.svg', 'manifest.json', 'robots.txt']:
        if (source / name).is_file():
            shutil.copy2(source / name, site / 'sgacd' / name)
    (site / 'sgacd/js/config.js').write_text('window.config = {apiBaseUrl: location.origin};\n')
    spec = importlib.util.spec_from_file_location('corporate_deploy', ROOT / 'BACKEND/ANALEMATICA-BACKEND/deployment/start.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in module.PUBLIC:
        path = ROOT / 'FRONTEND/ANALEMATICA-FRONTEND' / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Recurso corporativo no permitido: ' + name)
        target = site / 'analematica' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    offline_capture(site/'analematica/contabilidad-offline')
    offline_capture(site/'erp-capture/contabilidad-offline')
    for folder, source in [('sgacd','SGA-CD-WEB.git'),('analematica','ANALEMATICA-FRONTEND'),('erp-capture','SGA-ERP-TUR-FRONTEND/public')]:
        shutil.copytree(ROOT/'FRONTEND'/source/'commercial-offline',site/folder/'commercial-offline',dirs_exist_ok=True)
    # One canonical assistance UI is served under each site's own authenticated origin.
    for name in ['platform.html','js/platform.js','resources.html','js/resources.js','assistance.html','js/assistance.js','css/assistance.css','control.html','js/control.js','content.html','js/content.js','css/content.css']:
        path = ROOT / 'FRONTEND/ANALEMATICA-FRONTEND' / name
        target = site / 'sgacd' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

def next_projects(dependencies=None, systems=('erp','turismo')):
    source = ROOT / 'FRONTEND/SGA-TUR-FRONTEND'
    for name in systems:
        if name not in {'erp','turismo'}:raise ValueError('Proyecto web desconocido')
        dest = RUNTIME / name
        dest.mkdir(parents=True, exist_ok=True)
        for folder in ['src', 'public']:
            if (dest / folder).exists():
                shutil.rmtree(dest / folder)
            shutil.copytree(source / folder, dest / folder)
        if name == 'erp':
            offline_capture(dest/'public/contabilidad-offline')
            shutil.copytree(ROOT/'FRONTEND/SGA-ERP-TUR-FRONTEND/public/commercial-offline',dest/'public/commercial-offline',dirs_exist_ok=True)
            # Public assets are served at the ERP origin, not buried inside app routes.
            for asset in ('commercial-crm.html','commercial-quote.html','js/commercial-analytics.js','js/commercial-army.js','js/commercial-ads.js','js/commercial-inbox.js','js/commercial-publishing.js','js/commercial-mobile-messages.js','js/commercial-email-campaigns.js','js/commercial-generation.js','js/commercial-library.js','js/commercial-landings.js','js/commercial-after-sales-policy.js','js/commercial-after-sales.js','js/commercial-payments.js','js/commercial-sales.js','js/commercial-quotations.js','js/commercial-quote-recipient.js','js/commercial-pricing.js','js/commercial-opportunities.js','js/commercial-crm.js','js/commercial-crm-native.js','css/commercial-crm.css'):
                source_asset=ROOT/'FRONTEND/SGA-ERP-TUR-FRONTEND/public'/asset
                target_asset=dest/'public'/asset
                target_asset.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source_asset,target_asset)
            target = dest / 'src/app/dashboard/prestador/mi-negocio'
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(ROOT / 'FRONTEND/SGA-ERP-TUR-FRONTEND', target)
            entry=dest/'src/app/erp/cotizaciones'
            entry.mkdir(parents=True,exist_ok=True)
            (entry/'page.tsx').write_text("export {default} from '../../dashboard/prestador/mi-negocio/gestion-comercial/cotizaciones/page';\n")
            (dest / 'src/app/page.tsx').write_text('''import Dashboard from './dashboard/prestador/mi-negocio/page';
export default function Preview(){return <><div style={{background:'#142850',padding:12,color:'#ffffff',borderLeft:'3px solid #38bdf8'}}>Vista local de revisión. <a href="/erp/cotizaciones" style={{color:"#ffffff"}}>Acceso a cotizaciones</a>. Los demás procesos continúan en validación.</div><Dashboard/></>}
''')
        if name == 'turismo':
            # Institutional admin screens reuse ERP components; these are shared
            # source modules, not newly mounted ERP routes in the institutional app.
            shared=dest/'src/shared/erp'
            if shared.exists():shutil.rmtree(shared)
            shutil.copytree(ROOT/'FRONTEND/SGA-ERP-TUR-FRONTEND',shared)
        (dest / 'package.json').write_text((HERE / 'package.json').read_text())
        (dest / 'postcss.config.mjs').write_text((source / 'postcss.config.mjs').read_text())
        aliases={"@sarita/shared-ui":"src/components/shared-ui/index.ts","@":"src"}
        paths={'@/*':['./src/*'],'@sarita/shared-ui':['./src/components/shared-ui/index.ts']}
        if name=='turismo':
            aliases={'@sarita/shared-ui':'src/components/shared-ui/index.ts','@/app/dashboard/prestador/mi-negocio':'src/shared/erp','@':'src'}
            paths['@/app/dashboard/prestador/mi-negocio/*']=['./src/shared/erp/*']
        (dest / 'next.config.mjs').write_text("import path from 'node:path';\nexport default {devIndicators:false,poweredByHeader:false,experimental:{cpus:2},webpack(config){const shared="+json.dumps(aliases)+";config.resolve.alias={...config.resolve.alias,...Object.fromEntries(Object.entries(shared).map(([key,value])=>[key,path.resolve(value)]))};return config;}};\n")
        (dest / 'tsconfig.json').write_text(json.dumps({'compilerOptions': {'target':'ES2020','lib':['dom','dom.iterable','esnext'],'allowJs':True,'skipLibCheck':True,'strict':True,'noEmit':True,'esModuleInterop':True,'module':'esnext','moduleResolution':'bundler','resolveJsonModule':True,'isolatedModules':True,'jsx':'preserve','incremental':True,'plugins':[{'name':'next'}],'paths':paths},'include':['next-env.d.ts','**/*.ts','**/*.tsx','.next/types/**/*.ts'],'exclude':['node_modules']},indent=2))
        link = dest / 'node_modules'
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            raise RuntimeError('No se reemplaza un node_modules personalizado en ' + str(dest))
        link.symlink_to(str(Path(dependencies).resolve()) if dependencies else '/srv/deps/node_modules', target_is_directory=True)

def nginx():
    text = '''pid /tmp/nginx.pid;
worker_processes 1;
events { worker_connections 512; }
http {
 include /etc/nginx/mime.types;
 default_type application/octet-stream;
 server_tokens off;
 client_max_body_size 10m;
 client_body_timeout 15s;
 send_timeout 30s;
 log_format private_log '$remote_addr $request_method $uri $status';
 access_log /dev/stdout private_log;
 error_log /dev/stderr warn;
 proxy_temp_path /tmp/proxy;
 client_body_temp_path /tmp/body;
 limit_req_status 429;
 limit_req_zone $binary_remote_addr zone=views:10m rate=30r/s;
 limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
 limit_req_zone $binary_remote_addr zone=login:10m rate=10r/m;
 map $http_upgrade $connection_upgrade { default upgrade; '' close; }
 map $http_authorization $api_auth { ~*^(Bearer|Token)\\s $http_authorization; default ''; }
 resolver 127.0.0.11 valid=10s;
'''
    for index, name in enumerate(['sgacd', 'analematica', 'erp', 'turismo']):
        eval_policy = "\'unsafe-eval\'" if name in ['erp', 'turismo'] else ''
        text += f''' server {{
  listen {8440 + index} ssl;
  server_name localhost;
  ssl_certificate /private/localhost.crt;
  ssl_certificate_key /private/localhost.key;
  ssl_protocols TLSv1.2 TLSv1.3;
  add_header X-Content-Type-Options nosniff always;
  add_header X-Frame-Options DENY always;
  add_header Referrer-Policy no-referrer always;
  add_header Permissions-Policy "camera=(), geolocation=(), microphone=(self)" always;
  add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' {eval_policy}; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob: https:; media-src 'self' blob:; connect-src 'self' wss:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'" always;
  location ~ (^|/)\\. {{ return 404; }}
'''
        if name in ['sgacd','analematica']:
            proxy = f'''set $api_upstream {name}:8000;
    proxy_pass http://$api_upstream;
    proxy_set_header Authorization $api_auth;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto https;
    proxy_connect_timeout 5s;
    proxy_read_timeout 30s;'''
            text += '  location ~ ^/api/.*(login|token) { limit_req zone=login burst=3 nodelay; '+proxy+' }\n'
            text += '  location /api/ { limit_req zone=api burst=30 nodelay; '+proxy+' }\n'
        elif name=='erp' and os.environ.get('SGACD_ENABLE_ERP_API','0')=='1':
            # Opt-in only audited session/quotation routes. Never expose legacy finance APIs.
            proxy = """set $api_upstream erp-tur:8000;
    proxy_pass http://$api_upstream;
    proxy_set_header Authorization "";
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-Proto https;
    proxy_connect_timeout 5s;
    proxy_read_timeout 30s;"""
            text += '  location = /api/v1/erp-session/login/ { limit_req zone=login burst=3 nodelay; '+proxy+' }\n'
            text += '  location = /api/v1/mi-negocio/comercial/unified/crm/session/login/ { limit_req zone=login burst=3 nodelay; '+proxy+' }\n'
            text += '  location ^~ /api/v1/mi-negocio/comercial/unified/crm/quotation-media/ { client_max_body_size 256k; limit_req zone=api burst=30 nodelay; '+proxy+' }\n'
            text += '  location ~ ^/api/v1/mi-negocio/comercial/unified/quote-links/[0-9a-f-]+/[0-9a-f-]+(/media/[0-9a-f-]+)?/$ { client_max_body_size 16k; limit_req zone=api burst=30 nodelay; '+proxy+' }\n'
            text += '  location ^~ /api/v1/mi-negocio/comercial/unified/crm/ { client_max_body_size 16k; limit_req zone=api burst=30 nodelay; '+proxy+' }\n'
            text += '  location ~ ^/api/v1/(erp-session/((logout|mfa|password-reset/(request|confirm)|security-events|recovery(/issue)?|enrollment/(start|confirm|cancel))/)?|mi-negocio/comercial/(company-scopes/|service-availability/|capacity-holds/([0-9a-f-]+/release/)?|quotation-options/|quotation-preview/|quotation-drafts/([0-9a-f-]+/(withdraw/)?)?))$ { limit_req zone=api burst=30 nodelay; '+proxy+' }\n'
            text += '  location /api/ { default_type application/json; return 503 \'{"detail":"Ruta ERP pendiente de validación."}\'; }\n'
        else:
            text += '  location /api/ { default_type application/json; return 503 \'{"detail":"Backend turístico pendiente de corregir; no se simula autenticación."}\'; }\n'
        if name in ['analematica','erp']:
            capture_root='/sites/analematica' if name=='analematica' else '/sites/erp-capture'
            text += '  location = /contabilidad-offline/ { auth_basic off; absolute_redirect off; return 302 /contabilidad-offline/index.html; }\n'
            for asset in ['index.html','editor.js','editor.css','vault.js','worker.js']:
                text += '  location = /contabilidad-offline/'+asset+' { auth_basic off; root '+capture_root+'; try_files $uri =404; }\n'
            text += '  location ^~ /contabilidad-offline/ { return 404; }\n'
        if name in ['sgacd','analematica','erp']:
            commercial_root='/sites/erp-capture' if name=='erp' else '/sites/'+name
            for asset in ['index.html','editor.js','style.css','vault.js','worker.js']:
                text += '  location = /commercial-offline/'+asset+' { auth_basic off; root '+commercial_root+'; try_files $uri =404; }\n'
            text += '  location ^~ /commercial-offline/ { return 404; }\n'
        # Only the capability-link shell is public; business panels retain Basic review auth.
        if name in ['sgacd','analematica'] or (name=='erp' and os.environ.get('SGACD_ENABLE_ERP_API','0')=='1'):
            for public_asset in ['commercial-quote.html','js/commercial-quote-recipient.js','css/commercial-crm.css']:
                text += '  location = /'+public_asset+' { auth_basic off; limit_req zone=views burst=100 nodelay; '
                if name in ['sgacd','analematica']:
                    text += 'root /sites/'+name+'; try_files $uri =404;'
                else:
                    text += 'proxy_pass http://erp-web:3000; proxy_set_header Host $host; proxy_read_timeout 30s;'
                text += ' }\n'
        text += f'  location / {{ limit_req zone=views burst=100 nodelay; auth_basic "Vista local {name}"; auth_basic_user_file /private/{name}.htpasswd;\n'
        if name in ['sgacd','analematica']:
            text += f'    root /sites/{name}; index index.html; autoindex off; try_files $uri $uri/ =404;\n'
        else:
            text += f'    proxy_pass http://{name}-web:3000; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection $connection_upgrade; proxy_set_header Host $host; proxy_read_timeout 90s;\n'
        text += '  }\n }\n'
    text += '}\n'
    (RUNTIME / 'nginx.conf').write_text(text)

def compose():
    config = {'name':'sgacd-web-local','services':{},'networks':{'backends':{'external':True,'name':'${BACKEND_NETWORK:-sgacd-backends_default}'}}}
    for name in ['erp','turismo']:
        config['services'][name + '-web']={'image':'node:24-bookworm-slim','user':'1000:1000','working_dir':'/srv/project','init':True,'read_only':True,'cap_drop':['ALL'],'security_opt':['no-new-privileges:true'],'tmpfs':['/tmp:mode=1777'],'volumes':['./.runtime/'+name+':/srv/project','./node_modules:/srv/deps/node_modules:ro'],'environment':{'NEXT_TELEMETRY_DISABLED':'1','NEXT_PUBLIC_API_URL':'/api/v1','NEXT_PUBLIC_ENABLE_MOCKS':'false'},'command':['node','node_modules/next/dist/bin/next','dev','--webpack','--hostname','0.0.0.0','--port','3000']}
    config['services']['web']={'image':'nginx:alpine','user':'1000:1000','entrypoint':['nginx'],'command':['-g','daemon off;'],'init':True,'read_only':True,'cap_drop':['ALL'],'security_opt':['no-new-privileges:true'],'tmpfs':['/tmp:mode=1777','/var/cache/nginx:mode=1777'],'volumes':['./.runtime/nginx.conf:/etc/nginx/nginx.conf:ro','./.runtime/sites:/sites:ro','./private:/private:ro'],'ports':['127.0.0.1:'+str(8100+i)+':'+str(8440+i) for i in range(4)],'depends_on':['erp-web','turismo-web'],'networks':['default','backends']}
    (HERE / 'compose.yaml').write_text(json.dumps(config,indent=2)+'\n')

def main():
    RUNTIME.mkdir(mode=0o700,exist_ok=True)
    PRIVATE.mkdir(mode=0o700,exist_ok=True)
    certificate()
    access = credentials()
    public_assets()
    next_projects()
    nginx()
    compose()
    report = '# Accesos privados de revisión local\n\nEstas claves abren la vista web; no sustituyen el login de la aplicación.\nEl certificado es local autofirmado. Solo se exponen puertos en 127.0.0.1.\n\n'
    for index, (name,item) in enumerate(access.items()):
        route = '/dashboard/login' if name == 'turismo' else ('/erp/cotizaciones' if name == 'erp' else '/')
        report += f"- {name}: https://localhost:{8100+index}{route}\n  Usuario: {item['username']}\n  Clave: {item['password']}\n\n"
    target = PRIVATE / 'ACCESOS-LOCALES.md'
    if target.exists():
        target.unlink()
    private_file(target, report)
    print('Vistas preparadas. Accesos guardados exclusivamente en FRONTEND/deployment/private/ACCESOS-LOCALES.md. No se iniciaron servicios.')

if __name__ == '__main__':
    main()
