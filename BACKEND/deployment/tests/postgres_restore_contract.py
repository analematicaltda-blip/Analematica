"""Backup/restore drill only for the explicitly marked temporary PostgreSQL fixture."""
import hashlib,json,os,secrets,subprocess,tempfile,uuid
from contextlib import closing
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit


def run():
    if os.environ.get('MFA_PG_FIXTURE')!='1':raise RuntimeError('Isolated fixture required')
    container=os.environ['MFA_TEST_CONTAINER']
    if not container or any(char not in '0123456789abcdef' for char in container):raise RuntimeError('Invalid fixture container')
    source=os.environ['MFA_TEST_DATABASE_URL']
    parsed=urlsplit(source)
    if parsed.hostname!='127.0.0.1' or parsed.path!='/mfa_fixture':raise RuntimeError('Private test database required')
    import psycopg2
    from psycopg2 import sql
    from cryptography.fernet import Fernet,InvalidToken
    from apps.common.mfa_adapter import EncryptedMFAAdapter,PREFIX
    from django.contrib.sessions.backends.db import SessionStore
    env={key:value for key,value in os.environ.items() if key not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
    def docker(*args,data=None):
        return subprocess.run(['docker','--host=unix:///var/run/docker.sock',*args],env=env,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=30).stdout
    def inventory(url):
        with closing(psycopg2.connect(url)) as connection,connection.cursor() as cursor:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
            names=[row[0] for row in cursor.fetchall()];summary={}
            for name in names:
                cursor.execute(sql.SQL('SELECT row_to_json(t)::text FROM {} AS t').format(sql.Identifier('public',name)))
                rows=sorted(row[0] for row in cursor.fetchall())
                summary[name]={'rows':len(rows),'digest':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()}
            cursor.execute("SELECT count(*) FROM pg_constraint WHERE contype='f' AND NOT convalidated")
            assert cursor.fetchone()[0]==0
            return summary
    before=inventory(source);name='restore_'+uuid.uuid4().hex
    destination=urlunsplit((parsed.scheme,parsed.netloc,'/'+name,parsed.query,parsed.fragment))
    created=False
    try:
        # The archive is held in memory and encrypted before writing to local disk.
        archive=docker('exec',container,'pg_dump','-U','mfa_fixture','-d','mfa_fixture','--format=custom','--no-owner','--no-acl')
        key=Fernet.generate_key();cipher=Fernet(key);sealed=cipher.encrypt(archive)
        with tempfile.TemporaryDirectory(prefix='pg-restore-private-') as private:
            path=Path(private)/'snapshot.encrypted'
            with open(path,'xb',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:stream.write(sealed)
            assert path.stat().st_mode&0o777==0o600
            tampered=bytearray(sealed);tampered[len(tampered)//2]^=1
            try:cipher.decrypt(bytes(tampered))
            except InvalidToken:pass
            else:raise AssertionError('Tampered archive was accepted')
            restored_archive=cipher.decrypt(path.read_bytes())
            assert hashlib.sha256(restored_archive).digest()==hashlib.sha256(archive).digest()
            docker('exec',container,'createdb','-U','mfa_fixture',name);created=True
            docker('exec','-i',container,'pg_restore','-U','mfa_fixture','-d',name,'--no-owner','--no-acl','--single-transaction','--exit-on-error',data=restored_archive)
            restored=inventory(destination)
            assert restored==before,'Restored inventory differs from source'
            assert inventory(source)==before,'Source was modified by the drill'
            decrypted=0;decoded_sessions=0
            with closing(psycopg2.connect(destination)) as connection,connection.cursor() as cursor:
                cursor.execute('SELECT data FROM mfa_authenticator')
                for (data,) in cursor.fetchall():
                    if isinstance(data,str):data=json.loads(data)
                    for field in ('secret','seed'):
                        if field in data:
                            assert data[field].startswith(PREFIX)
                            assert len(EncryptedMFAAdapter().decrypt(data[field]))>=16
                            decrypted+=1
                cursor.execute('SELECT session_data FROM django_session')
                for (value,) in cursor.fetchall():
                    decoded=SessionStore().decode(value)
                    assert decoded and '_auth_user_id' in decoded or decoded and 'erp_pending_mfa' in decoded
                    decoded_sessions+=1
            assert decrypted>0 and decoded_sessions>0
            return {'restored_to_new_database':True,'source_unchanged':True,'table_count':len(restored),'row_count':sum(table['rows'] for table in restored.values()),'all_table_rows_match':True,'foreign_keys_validated':True,'encrypted_archive_private_permissions':True,'tampered_archive_rejected':True,'mfa_material_decrypted_with_original_key':decrypted,'sessions_decoded_with_original_key':decoded_sessions,'archive_sha256':hashlib.sha256(archive).hexdigest(),'keys_saved_in_archive':False}
    finally:
        if created:docker('exec',container,'dropdb','-U','mfa_fixture',name)
