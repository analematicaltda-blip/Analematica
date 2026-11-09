"""Actual separate PostgreSQL versions, restricted role, HTTP and browser client."""
import base64,copy,hashlib,json,os,secrets,socket,subprocess,sys,tempfile,threading,time,uuid
from pathlib import Path
from datetime import datetime,timedelta,timezone
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
ROOT=Path(__file__).resolve().parents[3]

def run_package_contract(owner,role,password,company):
    from django.db import DatabaseError
    from apps.core_erp.accounting.customer_package_store import CustomerPackageStore,StorageConflict,initialize_customer_packages
    from apps.core_erp.accounting.customer_package_api import build_app
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.keywrap import aes_key_wrap,aes_key_unwrap
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes,hmac
    if os.environ.get('MFA_PG_FIXTURE')!='1' or not owner.settings_dict['NAME'].startswith('customer_vault_'):raise RuntimeError('Disposable customer DB required')
    initialize_customer_packages(owner,company)
    with owner.cursor() as cursor:cursor.execute('GRANT SELECT,INSERT ON public.customer_fiscal_packages TO '+owner.ops.quote_name(role))
    def connect(label):
        c=owner.copy(alias='package_'+label+'_'+uuid.uuid4().hex);c.settings_dict.update(USER=role,PASSWORD=password);return c
    @contextmanager
    def factory():
        connection=connect('api')
        try:yield CustomerPackageStore(connection,company)
        finally:connection.close()
    canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    encode=lambda v:base64.urlsafe_b64encode(v).rstrip(b'=').decode()
    decode=lambda v:base64.urlsafe_b64decode(v+'='*((-len(v))%4))
    plain=b'SYNTHETIC PRIVATE CUSTOMER PACKAGE'
    def make(document=None,revision=1,parent=None,original=None):
        document=document or str(uuid.uuid4());salt=os.urandom(16);kw=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=600000).derive(b'synthetic customer package password');mac=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt+b'fiscal-package-auth',iterations=600000).derive(b'synthetic customer package password')
        if original:dek=original[1];iv=decode(original[0]['envelope']['iv']);cipher=decode(original[0]['envelope']['ciphertext'])
        else:dek=os.urandom(32);iv=os.urandom(12);aad=json.dumps(['sgacd-fiscal-envelope-v1','AES-256-GCM+A256KW',company,document,'fiscal-document'],separators=(',',':')).encode();cipher=AESGCM(dek).encrypt(iv,plain,aad)
        p={'schema':'sgacd-fiscal-package-v1','revision':revision,'previous_digest':parent,'key_descriptor':{'kdf':'PBKDF2-SHA256','iterations':600000,'salt':encode(salt)},'envelope':{'schema':'sgacd-fiscal-envelope-v1','algorithm':'AES-256-GCM+A256KW','context':{'company_id':company,'document_id':document},'iv':encode(iv),'wrapped_key':encode(aes_key_wrap(kw,dek)),'ciphertext':encode(cipher)}};tag=hmac.HMAC(mac,hashes.SHA256());tag.update(canonical(p));p['auth_tag']=encode(tag.finalize());p['package_digest']=hashlib.sha256(canonical(p)).hexdigest();return p,dek
    connection=connect('main');store=CustomerPackageStore(connection,company)
    try:
        first,dek=make();doc=first['envelope']['context']['document_id'];assert not store.put(first)['replayed'];assert store.put(first)['replayed'];second,_=make(doc,2,first['package_digest'],(first,dek));store.put(second);assert store.get(doc)==second and store.get(doc,1)==first
        salt=decode(second['key_descriptor']['salt']);kw=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=600000).derive(b'synthetic customer package password');key=aes_key_unwrap(kw,decode(second['envelope']['wrapped_key']));aad=json.dumps(['sgacd-fiscal-envelope-v1','AES-256-GCM+A256KW',company,doc,'fiscal-document'],separators=(',',':')).encode();assert AESGCM(key).decrypt(decode(second['envelope']['iv']),decode(second['envelope']['ciphertext']),aad)==plain
        with owner.cursor() as cursor:cursor.execute("SELECT bool_and(position(%s::bytea IN package_bytes)=0) FROM public.customer_fiscal_packages",[plain]);assert cursor.fetchone()[0]
        try:store.put(make(doc,4,'a'*64,(first,dek))[0])
        except StorageConflict:pass
        else:raise AssertionError('Skipped revision accepted')
        def race(values):
            barrier=Barrier(2)
            def attempt(p):
                c=connect('race')
                try:
                    barrier.wait(timeout=10)
                    try:return CustomerPackageStore(c,company).put(p)
                    except StorageConflict:return None
                finally:c.close()
            with ThreadPoolExecutor(max_workers=2) as pool:return list(pool.map(attempt,values))
        repeated,_=make();receipts=race([repeated,repeated]);assert sorted(r['replayed'] for r in receipts)==[False,True]
        parent,key=make();store.put(parent);document=parent['envelope']['context']['document_id'];choices=[make(document,2,parent['package_digest'],(parent,key))[0] for _ in range(2)];assert sum(r is not None for r in race(choices))==1
        for sql in ['UPDATE public.customer_fiscal_packages SET revision=revision','DELETE FROM public.customer_fiscal_packages','TRUNCATE public.customer_fiscal_packages']:
            try:
                with connection.cursor() as cursor:cursor.execute(sql)
            except DatabaseError:pass
            else:raise AssertionError('Restricted customer writer mutated package')
        with owner.cursor() as cursor:cursor.execute('ALTER TABLE public.customer_fiscal_packages DISABLE TRIGGER customer_package_row_guard')
        try:store.get(doc)
        except ValueError:pass
        else:raise AssertionError('Missing guard did not block access')
        initialize_customer_packages(owner,company);assert store.get(doc)==second
        minimal_role='customer_pkg_'+uuid.uuid4().hex;minimal_password=secrets.token_urlsafe(32);minimal_q=owner.ops.quote_name(minimal_role);minimal=None
        try:
            with owner.cursor() as cursor:
                cursor.execute('CREATE ROLE '+minimal_q+' LOGIN PASSWORD %s',[minimal_password]);cursor.execute('GRANT CONNECT ON DATABASE '+owner.ops.quote_name(owner.settings_dict['NAME'])+' TO '+minimal_q);cursor.execute('GRANT USAGE ON SCHEMA public TO '+minimal_q);cursor.execute('GRANT SELECT ON public.customer_fiscal_binding TO '+minimal_q);cursor.execute('GRANT SELECT,INSERT ON public.customer_fiscal_packages TO '+minimal_q)
            minimal=owner.copy(alias='customer_minimal_role');minimal.settings_dict.update(USER=minimal_role,PASSWORD=minimal_password);minimal_store=CustomerPackageStore(minimal,company);assert minimal_store.put(second)['replayed'];assert minimal_store.get(doc)==second
            try:
                with minimal.cursor() as cursor:cursor.execute('SELECT * FROM public.customer_fiscal_envelopes')
            except DatabaseError:pass
            else:raise AssertionError('Package-only role unexpectedly reads legacy document table')
        finally:
            if minimal is not None:minimal.close()
            with owner.cursor() as cursor:cursor.execute('DROP OWNED BY '+minimal_q);cursor.execute('DROP ROLE '+minimal_q)
        # An unexpected customer INSERT trigger must not earn a false receipt.
        corrupted,_=make();corrupt_doc=corrupted['envelope']['context']['document_id']
        with owner.cursor() as cursor:
            cursor.execute("CREATE FUNCTION public.customer_package_test_rewrite() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN NEW.package_bytes=decode('00','hex'); RETURN NEW; END $$")
            cursor.execute('CREATE TRIGGER customer_package_test_rewrite BEFORE INSERT ON public.customer_fiscal_packages FOR EACH ROW EXECUTE FUNCTION public.customer_package_test_rewrite()')
        try:
            try:store.put(corrupted)
            except ValueError:pass
            else:raise AssertionError('Customer trigger mutation earned a false receipt')
            with owner.cursor() as cursor:cursor.execute('SELECT COUNT(*) FROM public.customer_fiscal_packages WHERE document_id=%s',[corrupt_doc]);assert cursor.fetchone()[0]==0
        finally:
            with owner.cursor() as cursor:
                cursor.execute('DROP TRIGGER customer_package_test_rewrite ON public.customer_fiscal_packages');cursor.execute('DROP FUNCTION public.customer_package_test_rewrite()')
        # Real ASGI routes backed by the restricted PostgreSQL writer.
        from fastapi.testclient import TestClient
        with tempfile.TemporaryDirectory(prefix='customer-package-api-') as private:
            private=Path(private);token='byos_'+secrets.token_urlsafe(32);grant_path=private/'grant.json';g={'company_id':company,'token_sha256':hashlib.sha256(token.encode()).hexdigest(),'expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'permissions':['read','append'],'allowed_origins':['https://frontend.example.test']}
            def save():grant_path.write_text(json.dumps(g));grant_path.chmod(0o600)
            save();client=TestClient(build_app(factory,grant_path));headers={'Authorization':'Bearer '+token,'Origin':g['allowed_origins'][0]}
            assert client.get('/v1/identity',headers=headers).json()['company_id']==company;assert client.post('/v1/packages',headers=headers,json=second).json()['replayed'];assert client.get('/v1/packages/'+doc,headers=headers).json()==second
            g['permissions']=['read'];save();assert client.post('/v1/packages',headers=headers,json=second).status_code==403;assert client.get('/v1/packages/'+doc,headers=headers).status_code==200;client.close()
            browser=run_browser(factory,private,company)
        # Expose only encrypted fixtures for the existing disposable restore check.
        with owner.cursor() as cursor:cursor.execute('SELECT document_id,revision FROM public.customer_fiscal_packages ORDER BY document_id,revision');keys=cursor.fetchall()
        fixtures=[store.get(str(document),revision) for document,revision in keys]
        result={'real_aead_roundtrip':True,'historical_versions_preserved':True,'replayed_write_idempotent':True,'restricted_writer_mutation_denied':True,'lost_guards_fail_closed':True,'actual_http_postgresql_and_revocation':True,'customer_insert_mutation_rolls_back':True,'browser':browser,'scenarios':[{'scenario':'customer_package_least_privilege_role','passed':True},{'scenario':'customer_package_version_chain_and_recovery','passed':True},{'scenario':'customer_package_simultaneous_retry','one_insert':True,'one_replay':True},{'scenario':'customer_package_competing_version','accepted':1,'rejected':1}],'production_qualified':False}
        return result,fixtures
    finally:connection.close()

def run_browser(factory,private,company):
    import ipaddress
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes,serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from fastapi.responses import HTMLResponse,Response
    import uvicorn
    from apps.core_erp.accounting.customer_package_api import build_app
    sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];origin='https://127.0.0.1:'+str(port);token='byos_'+secrets.token_urlsafe(32);grant=private/'browser-grant.json';grant.write_text(json.dumps({'company_id':company,'token_sha256':hashlib.sha256(token.encode()).hexdigest(),'expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'permissions':['read','append'],'allowed_origins':[origin]}));grant.chmod(0o600)
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048);subject=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'loopback-test')]);now=datetime.now(timezone.utc);cert=x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=1)).not_valid_after(now+timedelta(hours=1)).add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]),False).sign(key,hashes.SHA256());cert_path=private/'cert.pem';key_path=private/'key.pem';cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM));key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));key_path.chmod(0o600)
    app=build_app(factory,grant)
    @app.get('/')
    def page():return HTMLResponse('<script src="/fixture/fiscal-envelope-runtime.js"></script><script src="/fixture/accounting-fiscal-package.js"></script><script src="/fixture/accounting-customer-store.js"></script>')
    @app.get('/fixture/{name}')
    def asset(name:str):
        if name not in {'fiscal-envelope-runtime.js','accounting-fiscal-package.js','accounting-customer-store.js'}:raise RuntimeError('Unknown fixture asset')
        return Response((ROOT/'FRONTEND/ANALEMATICA-FRONTEND/js'/name).read_bytes(),media_type='text/javascript')
    server=uvicorn.Server(uvicorn.Config(app,ssl_certfile=str(cert_path),ssl_keyfile=str(key_path),log_level='critical',access_log=False));thread=threading.Thread(target=lambda:server.run(sockets=[sock]),daemon=True);thread.start()
    try:
        for _ in range(100):
            if server.started:break
            time.sleep(.05)
        if not server.started:raise RuntimeError('Customer HTTPS fixture did not start')
        case=private/'browser-case.json';case.write_text(json.dumps({'origin':origin,'company_id':company,'token':token}));case.chmod(0o600)
        run=subprocess.run(['node',str(ROOT/'FRONTEND/deployment/tests/customer_store_browser.cjs')],env={**os.environ,'CUSTOMER_BROWSER_CASE':str(case),'PLAYWRIGHT_MODULE':str(ROOT/'DESKTOP/asistencia-sgacd/node_modules/playwright')},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=90)
        if run.returncode:
            fd,diagnostic=tempfile.mkstemp(prefix='customer-browser-error-');os.close(fd);Path(diagnostic).write_text(run.stderr);raise RuntimeError('Customer browser contract failed; isolated diagnostic '+diagnostic)
        result=json.loads(run.stdout);assert result['passed'];return result
    finally:server.should_exit=True;thread.join(timeout=10);sock.close()
