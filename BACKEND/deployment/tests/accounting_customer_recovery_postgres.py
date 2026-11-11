"""Explicit local-only PostgreSQL fault injection; never uses configured ERP DBs."""
import argparse,subprocess,os,tempfile,secrets,uuid,json,time,sys,runpy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'BACKEND/ANALEMATICA-BACKEND'))

def run():
    parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true',required=True);parser.parse_args()
    env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
    def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True).strip()
    name='sgacd-byos-recovery-'+uuid.uuid4().hex[:12];database='customer_vault_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);owner=None;started=False
    with tempfile.TemporaryDirectory(prefix='byos-recovery-') as directory:
        private=Path(directory);private.chmod(0o700);cfg=private/'postgres.env';cfg.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');cfg.chmod(0o600)
        try:
            docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(cfg),'postgres:16-alpine');started=True
            deadline=time.monotonic()+45
            while True:
                try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
                except subprocess.CalledProcessError:
                    if time.monotonic()>deadline:raise RuntimeError('Local disposable PostgreSQL did not become ready')
                    time.sleep(0.2)
            port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1])
            from django.conf import settings
            settings.configure(USE_TZ=True,DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':database,'USER':'fixture_owner','PASSWORD':password,'HOST':'127.0.0.1','PORT':port,'OPTIONS':{'connect_timeout':5}}})
            from django.db import connections,DatabaseError
            from core_erp.accounting.customer_package_store import CustomerPackageStore,StorageOutcomeUnknown,package_receipt,initialize_customer_packages,StorageConflict
            owner=connections['default'];company=str(uuid.uuid4());initialize_customer_packages(owner,company)
            role='pkg_'+uuid.uuid4().hex[:12];role_password=secrets.token_urlsafe(32);quoted=owner.ops.quote_name(role)
            with owner.cursor() as cursor:
                cursor.execute('CREATE ROLE '+quoted+' LOGIN PASSWORD %s',[role_password]);cursor.execute('GRANT CONNECT ON DATABASE '+owner.ops.quote_name(database)+' TO '+quoted);cursor.execute('GRANT USAGE ON SCHEMA public TO '+quoted);cursor.execute('GRANT SELECT ON public.customer_fiscal_binding TO '+quoted);cursor.execute('GRANT SELECT,INSERT ON public.customer_fiscal_packages TO '+quoted)
            make=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/accounting_customer_package_check.py'),run_name='package_fixture')['package']
            def connection():
                c=owner.copy(alias='customer_'+uuid.uuid4().hex);c.settings_dict.update(USER=role,PASSWORD=role_password);return c
            results=[]
            for after_commit in (False,True):
                value=make(company);doc=value['envelope']['context']['document_id'];c=connection();store=CustomerPackageStore(c,company);commit=c.commit
                def lost_ack():
                    if after_commit:commit()
                    raise DatabaseError('Synthetic lost commit acknowledgement')
                try:
                    with patch.object(c,'commit',side_effect=lost_ack):
                        try:store.put(value)
                        except StorageOutcomeUnknown:pass
                        else:raise AssertionError('Unknown write returned a definitive result')
                    assert c.connection is None
                finally:c.close()
                fresh=connection()
                try:
                    active=CustomerPackageStore(fresh,company)
                    if after_commit:
                        receipt=package_receipt(active,doc,1,value['package_digest']);assert receipt['stored'];assert active.put(value)['replayed']
                    else:
                        try:package_receipt(active,doc,1,value['package_digest'])
                        except LookupError:pass
                        else:raise AssertionError('Uncommitted version was acknowledged')
                        assert active.put(value)['replayed'] is False
                    receipt=package_receipt(active,doc,1,value['package_digest']);assert not receipt['authenticated_ciphertext_verified'] and not receipt['fiscal_accepted']
                    assert active.get(doc,1)==value
                    try:package_receipt(active,doc,1,'f'*64)
                    except StorageConflict:pass
                    else:raise AssertionError('Different expected digest was acknowledged')
                    with fresh.cursor() as cursor:
                        cursor.execute('SELECT count(*) FROM public.customer_fiscal_packages WHERE company_id=%s AND document_id=%s',[company,doc]);assert cursor.fetchone()[0]==1
                        cursor.execute('SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user');assert cursor.fetchone()==(False,False,False)
                    results.append({'scenario':'ack_lost_after_commit' if after_commit else 'disconnect_before_commit','fresh_exact_version_read':True,'same_package_retry_single_row':True,'digest_conflict_denied':True,'restricted_role':True})
                finally:fresh.close()
            # Legacy regression imports apps.core_erp; isolate that compatibility
            # namespace to this standalone fixture, without changing app imports.
            import types,importlib
            namespace=types.ModuleType('apps');namespace.__path__=[]
            sys.modules['apps']=namespace
            sys.modules['apps.core_erp']=importlib.import_module('core_erp')
            os.environ['MFA_PG_FIXTURE']='1'
            contract=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/customer_package_contract.py'),run_name='customer_regression')['run_package_contract']
            regression,_=contract(owner,role,role_password,company)
            print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'opaque_synthetic_packages':True,'scenarios':results,'existing_postgres_regression':regression,'production_ready':False}))
        finally:
            if owner is not None:owner.close()
            if started:docker('stop','--time','2',name)
if __name__=='__main__':run()
