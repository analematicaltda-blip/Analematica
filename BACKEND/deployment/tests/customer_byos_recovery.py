"""Disposable customer-store restore contract; no real storage or key export."""
import hashlib,json,os,subprocess,tempfile,uuid
from pathlib import Path


def verify_customer_recovery(owner, company, documents, packages=None):
    from django.db import DatabaseError
    from apps.core_erp.accounting.customer_postgres_store import CustomerPostgresStore
    container=os.environ['MFA_TEST_CONTAINER']
    if os.environ.get('MFA_PG_FIXTURE')!='1' or not owner.settings_dict['NAME'].startswith('customer_vault_'):
        raise RuntimeError('Disposable customer database required.')
    env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
    target='customer_restore_'+uuid.uuid4().hex
    restored=owner.copy(alias='customer_restore_probe');restored.settings_dict['NAME']=target
    created=False
    def command(*args,**kwargs):
        return subprocess.run(['docker','--host=unix:///var/run/docker.sock','exec',*args],env=env,
            stdout=kwargs.pop('stdout',subprocess.DEVNULL),stderr=subprocess.PIPE,check=True,timeout=30,**kwargs)
    def manifest(connection):
        store=CustomerPostgresStore(connection,company)
        for document,envelope in documents.items():
            assert store.get(document)==envelope
        with connection.cursor() as cursor:
            cursor.execute('SELECT singleton,company_id,schema_version FROM public.customer_fiscal_binding ORDER BY singleton')
            binding=[list(map(str,row)) for row in cursor.fetchall()]
            cursor.execute("SELECT document_id,company_id,envelope_digest,encode(envelope_bytes,'hex'),created_at::text FROM public.customer_fiscal_envelopes ORDER BY document_id")
            rows=[list(map(str,row)) for row in cursor.fetchall()]
        assert len(rows)==len(documents)
        package_rows=[]
        if packages:
            from apps.core_erp.accounting.customer_package_store import CustomerPackageStore
            package_store=CustomerPackageStore(connection,company)
            for value in packages:assert package_store.get(value['envelope']['context']['document_id'],value['revision'])==value
            with connection.cursor() as cursor:
                cursor.execute("SELECT document_id,company_id,revision,package_digest,previous_digest,encode(package_bytes,'hex'),created_at::text FROM public.customer_fiscal_packages ORDER BY document_id,revision")
                package_rows=[list(map(str,row)) for row in cursor.fetchall()]
            assert len(package_rows)==len(packages)
        return hashlib.sha256(json.dumps([binding,rows,package_rows],separators=(',',':')).encode()).hexdigest()
    before=manifest(owner)
    try:
        with tempfile.TemporaryDirectory(prefix='customer-ciphertext-backup-') as directory:
            archive=Path(directory)/'customer.dump'
            with open(archive,'xb',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:
                command(container,'pg_dump','-U','mfa_fixture','-Fc',owner.settings_dict['NAME'],stdout=stream)
            assert archive.stat().st_mode&0o077==0
            if archive.stat().st_size>8*1024*1024:raise RuntimeError('Fixture archive exceeds bound.')
            command(container,'createdb','-U','mfa_fixture',target);created=True
            with archive.open('rb') as stream:
                command('-i',container,'pg_restore','--exit-on-error','--no-owner','--no-acl','-U','mfa_fixture','-d',target,stdin=stream)
            assert manifest(restored)==before and manifest(owner)==before
            # Restore must preserve enforcement, without re-running bootstrap.
            try:
                with restored.cursor() as cursor:cursor.execute('DELETE FROM public.customer_fiscal_envelopes')
            except DatabaseError as exc:assert 'CUSTOMER_FISCAL_IMMUTABLE' in str(exc)
            else:raise AssertionError('Restored document guard unavailable.')
            assert manifest(restored)==before
            return {'separate_database_restore':True,'ciphertext_and_binding_digest_equal':True,
                    'source_unchanged':True,'restored_guards_enforced':True,'archive_private':True,
                    'keys_exported':False,'roles_and_acls_restored':False,'production_qualified':False}
    finally:
        restored.close()
        if created:command(container,'dropdb','--force','-U','mfa_fixture',target)
