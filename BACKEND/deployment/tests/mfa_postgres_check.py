"""Isolated PostgreSQL row-lock contract: never connects to a project database.
Includes isolated service races and a two-process HTTP/password/session/CSRF contract.
"""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

# Fork-only Linux contract: initialize Django once, close every SQL connection
# before forking, then let each worker establish its own PostgreSQL connection.
_PROCESS_BARRIER=None

def process_attempt(payload):
    import hashlib
    from types import SimpleNamespace
    from unittest.mock import patch
    from django.db import connections
    from apps.prestadores.mi_negocio.web_mfa import verify
    from apps.prestadores.mi_negocio.web_recovery import issue
    try:
        connections.close_all()
        _PROCESS_BARRIER.wait(timeout=10)
        with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=payload['moment']):
            if payload['mode']=='issue':
                from django.contrib.auth import get_user_model,BACKEND_SESSION_KEY
                user=get_user_model().objects.get(pk=payload['user_id'])
                request=SimpleNamespace(user=user,session={BACKEND_SESSION_KEY:'django.contrib.auth.backends.ModelBackend'})
                result=issue(request,payload['password'],payload['code'])
                digest=hashlib.sha256(json.dumps(sorted(result[2])).encode()).hexdigest() if result else None
            else:
                request=SimpleNamespace(session=payload['session'])
                result=verify(request,payload['challenge_id'],payload['code'],recovery=payload['mode']=='recovery')
                digest=None
        return {'accepted':result is not None,'pid':os.getpid(),'codes_digest':digest}
    finally:connections.close_all()


def worker():
    import hashlib
    from concurrent.futures import ThreadPoolExecutor
    from datetime import timedelta
    from threading import Barrier
    from types import SimpleNamespace
    from unittest.mock import patch
    sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
    from init_local import initialize
    with tempfile.TemporaryDirectory(prefix='mfa-pg-keys-') as private:
        initialize(private)
        config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
        config['DATABASE_URL']=os.environ['MFA_TEST_DATABASE_URL']
        os.environ.update(config,BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=10000 -c lock_timeout=10000')
        for name in ('OPENAI_API_KEY','GEMINI_API_KEY','OLLAMA_ENDPOINT'):os.environ.pop(name,None)
        import django
        django.setup()
        from django.db import connection,connections
        from django.test import override_settings
        from django.core.cache.backends.dummy import DummyCache
        class ReplayBlindCache(DummyCache):
            def add(self,*args,**kwargs):return True
        # Deliberately no replay cache: the SQL counter must be sufficient.
        import types
        cache_module=types.ModuleType('mfa_pg_test_cache');cache_module.ReplayBlindCache=ReplayBlindCache;sys.modules[cache_module.__name__]=cache_module
        override=override_settings(CACHES={'default':{'BACKEND':'mfa_pg_test_cache.ReplayBlindCache'}},CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}},EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',ERP_RECOVERY_CODES_ENABLED=True);override.enable()
        from api.models import CustomUser,Entity
        from apps.core_erp.models import EventAuditLog
        from django.contrib.sessions.models import Session
        from allauth.account.models import EmailAddress
        from allauth.mfa.models import Authenticator
        from allauth.mfa.totp.internal.auth import TOTP,generate_totp_secret,hotp_value,format_hotp_value
        from apps.turismo.models import ErpSecurityEvent,ErpLoginChallenge,ErpTotpUsage
        from apps.prestadores.mi_negocio.web_mfa import enrollment_version,verify
        from django.utils import timezone
        assert connection.vendor=='postgresql'
        created=set();visiting=set()
        with connection.schema_editor() as editor:
            def create(model):
                model=model._meta.concrete_model
                if model in created or model in visiting:return
                visiting.add(model)
                for field in model._meta.local_fields:
                    if field.is_relation and field.remote_field and field.remote_field.model is not model:create(field.remote_field.model)
                for field in model._meta.local_many_to_many:create(field.remote_field.model)
                editor.create_model(model);created.add(model);visiting.remove(model)
            for model in (Session,EmailAddress,Entity,EventAuditLog,ErpSecurityEvent,CustomUser,Authenticator,ErpLoginChallenge,ErpTotpUsage):create(model)
        results=[]
        for same_challenge in (False,True):
            user=CustomUser(username='synthetic-pg-'+uuid.uuid4().hex,role='BUSINESS_OWNER');user.set_password(secrets.token_urlsafe(24));CustomUser.objects.bulk_create([user])
            secret=generate_totp_secret();factor=TOTP.activate(user,secret).instance
            version=enrollment_version(user)[0];moment=time.time();code=format_hotp_value(hotp_value(secret,int(moment)//30))
            requests=[];challenges=[]
            for index in range(1 if same_challenge else 2):
                binding=secrets.token_urlsafe(32)
                challenge=ErpLoginChallenge.objects.create(user=user,factor=factor,backend='django.contrib.auth.backends.ModelBackend',binding_digest=hashlib.sha256(binding.encode()).hexdigest(),password_version=user.get_session_auth_hash(),factor_version=version,expires_at=timezone.now()+timedelta(seconds=120))
                requests.append(SimpleNamespace(session={'erp_pending_mfa':{'id':str(challenge.pk),'binding':binding}}));challenges.append(challenge.pk)
            if same_challenge:requests*=2;challenges*=2
            barrier=Barrier(2)
            def attempt(index):
                try:
                    barrier.wait(timeout=10)
                    return verify(requests[index],challenges[index],code) is not None
                finally:connections.close_all()
            with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=moment),ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(attempt,index) for index in (0,1)]
                outcomes=[future.result(timeout=20) for future in futures]
            assert sum(outcomes)==1,outcomes
            assert ErpTotpUsage.objects.get(factor=factor).last_counter==int(moment)//30
            assert ErpLoginChallenge.objects.filter(pk__in=challenges,consumed_at__isnull=False).count()==1
            results.append({'scenario':'same_challenge' if same_challenge else 'different_sessions_same_code','accepted':1,'rejected':1})
        from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
        from apps.prestadores.mi_negocio.web_recovery import issue
        from django.contrib.auth import BACKEND_SESSION_KEY
        # Separate PostgreSQL connections race for a single backup code; cache is still blind.
        for same_challenge in (False,True):
            user=CustomUser(username='synthetic-recovery-'+uuid.uuid4().hex,role='BUSINESS_OWNER');user.set_password(secrets.token_urlsafe(24));CustomUser.objects.bulk_create([user])
            factor=TOTP.activate(user,generate_totp_secret()).instance
            backup=RecoveryCodes.activate(user);code=backup.get_unused_codes()[0]
            version=enrollment_version(user)[0];requests=[];challenges=[]
            for index in range(1 if same_challenge else 2):
                binding=secrets.token_urlsafe(32)
                challenge=ErpLoginChallenge.objects.create(user=user,factor=factor,backend='django.contrib.auth.backends.ModelBackend',binding_digest=hashlib.sha256(binding.encode()).hexdigest(),password_version=user.get_session_auth_hash(),factor_version=version,expires_at=timezone.now()+timedelta(seconds=120))
                requests.append(SimpleNamespace(session={'erp_pending_mfa':{'id':str(challenge.pk),'binding':binding}}));challenges.append(challenge.pk)
            if same_challenge:requests*=2;challenges*=2
            barrier=Barrier(2)
            def recover(index):
                try:
                    barrier.wait(timeout=10)
                    return verify(requests[index],challenges[index],code,recovery=True) is not None
                finally:connections.close_all()
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes=[future.result(timeout=20) for future in [pool.submit(recover,index) for index in (0,1)]]
            assert sum(outcomes)==1,outcomes
            backup.instance.refresh_from_db();assert backup.instance.data['used_mask']==1
            assert ErpSecurityEvent.objects.filter(actor_id=user.pk,kind='recovery_used').count()==1
            assert ErpLoginChallenge.objects.filter(pk__in=challenges,consumed_at__isnull=False).count()==1
            assert ErpTotpUsage.objects.get(factor=factor).last_counter==-1
            results.append({'scenario':'recovery_same_challenge' if same_challenge else 'recovery_different_sessions_same_code','accepted':1,'rejected':1})
        user=CustomUser(username='synthetic-issue-'+uuid.uuid4().hex,role='BUSINESS_OWNER');password=secrets.token_urlsafe(24);user.set_password(password);CustomUser.objects.bulk_create([user])
        secret=generate_totp_secret();factor=TOTP.activate(user,secret).instance
        old=RecoveryCodes.activate(user).get_unused_codes()
        moment=time.time();code=format_hotp_value(hotp_value(secret,int(moment)//30));barrier=Barrier(2)
        def emit():
            try:
                request=SimpleNamespace(user=user,session={BACKEND_SESSION_KEY:'django.contrib.auth.backends.ModelBackend'})
                barrier.wait(timeout=10)
                return issue(request,password,code)
            finally:connections.close_all()
        with patch('apps.prestadores.mi_negocio.web_recovery.time.time',return_value=moment),ThreadPoolExecutor(max_workers=2) as pool:
            outcomes=[future.result(timeout=20) for future in [pool.submit(emit) for _ in (0,1)]]
        accepted=[result for result in outcomes if result is not None]
        assert len(accepted)==1
        assert ErpSecurityEvent.objects.filter(actor_id=user.pk,kind='recovery_rotated').count()==1
        backup=RecoveryCodes(Authenticator.objects.get(user=user,type='recovery_codes'))
        assert backup.get_unused_codes()==accepted[0][2]
        assert not backup.validate_code(old[0])
        assert ErpTotpUsage.objects.get(factor=factor).last_counter==int(moment)//30
        assert Authenticator.objects.filter(user=user,type='totp').count()==1
        assert Authenticator.objects.filter(user=user,type='recovery_codes').count()==1
        results.append({'scenario':'issuance_different_sessions_same_totp','accepted':1,'rejected':1,'previous_codes_invalid':True})
        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing
        context=multiprocessing.get_context('fork')
        global _PROCESS_BARRIER
        process_results=[]
        for mode,same_challenge in (('totp',False),('totp',True),('recovery',False),('recovery',True),('issue',False)):
            user=CustomUser(username='synthetic-process-'+uuid.uuid4().hex,role='BUSINESS_OWNER');password=secrets.token_urlsafe(24);user.set_password(password);CustomUser.objects.bulk_create([user])
            secret=generate_totp_secret();factor=TOTP.activate(user,secret).instance
            moment=time.time();code=format_hotp_value(hotp_value(secret,int(moment)//30))
            backup=RecoveryCodes.activate(user) if mode in ('recovery','issue') else None
            previous=backup.get_unused_codes() if backup else []
            if mode=='recovery':code=previous[0]
            payloads=[];challenge_ids=[];version=enrollment_version(user)[0]
            if mode=='issue':
                payloads=[{'mode':mode,'user_id':user.pk,'password':password,'code':code,'moment':moment} for _ in (0,1)]
            else:
                for _ in range(1 if same_challenge else 2):
                    binding=secrets.token_urlsafe(32)
                    challenge=ErpLoginChallenge.objects.create(user=user,factor=factor,backend='django.contrib.auth.backends.ModelBackend',binding_digest=hashlib.sha256(binding.encode()).hexdigest(),password_version=user.get_session_auth_hash(),factor_version=version,expires_at=timezone.now()+timedelta(seconds=120))
                    challenge_ids.append(challenge.pk)
                    payloads.append({'mode':mode,'code':code,'moment':moment,'challenge_id':challenge.pk,'session':{'erp_pending_mfa':{'id':str(challenge.pk),'binding':binding}}})
                if same_challenge:payloads*=2
            _PROCESS_BARRIER=context.Barrier(2)
            connections.close_all()  # Never inherit a live libpq connection across fork.
            with ProcessPoolExecutor(max_workers=2,mp_context=context) as pool:
                futures=[pool.submit(process_attempt,payload) for payload in payloads]
                outcomes=[future.result(timeout=25) for future in futures]
            assert len({outcome['pid'] for outcome in outcomes})==2
            accepted=[outcome for outcome in outcomes if outcome['accepted']]
            assert len(accepted)==1,outcomes
            if mode=='issue':
                import hashlib as digest_hash
                fresh=RecoveryCodes(Authenticator.objects.get(user=user,type='recovery_codes'))
                assert digest_hash.sha256(json.dumps(sorted(fresh.get_unused_codes())).encode()).hexdigest()==accepted[0]['codes_digest']
                assert not fresh.validate_code(previous[0])
                assert ErpSecurityEvent.objects.filter(actor_id=user.pk,kind='recovery_rotated').count()==1
            else:
                assert ErpLoginChallenge.objects.filter(pk__in=challenge_ids,consumed_at__isnull=False).count()==1
            if mode=='recovery':
                backup.instance.refresh_from_db();assert backup.instance.data['used_mask']==1
                assert ErpSecurityEvent.objects.filter(actor_id=user.pk,kind='recovery_used').count()==1
            expected=-1 if mode=='recovery' else int(moment)//30
            assert ErpTotpUsage.objects.get(factor=factor).last_counter==expected
            process_results.append({'scenario':mode+('_same_challenge' if same_challenge else '_different_sessions_same_code'),'distinct_processes':2,'accepted':1,'rejected':1})
        from mfa_http_contract import run as run_http_contract
        http_results=run_http_contract(context)
        from capacity_postgres_contract import run as run_capacity_contract
        def create_capacity_model(model):
            nonlocal editor
            with connection.schema_editor() as editor:
                create(model)
        capacity_results=run_capacity_contract(context,create_capacity_model)
        from password_reset_postgres_contract import run as run_password_contract
        password_reset_result=run_password_contract(context)
        from control_postgres_contract import run as run_control_contract
        control_result=run_control_contract()
        from accounting_postgres_contract import run as run_accounting_contract
        accounting_result=run_accounting_contract()
        from postgres_restore_contract import run as run_restore_contract
        restore_result=run_restore_contract()
        connections.close_all();override.disable()
        print(json.dumps({'postgresql':True,'replay_cache_enforced':False,'results':results,'process_results':process_results,'http_results':http_results,'restore':restore_result,'capacity_results':capacity_results,'password_reset_result':password_reset_result,'control_result':control_result,'accounting_result':accounting_result}),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--worker',action='store_true');args=parser.parse_args()
    if args.worker:
        if os.environ.get('MFA_PG_FIXTURE')!='1':raise RuntimeError('Private fixture marker required')
        worker();return
    env={key:value for key,value in os.environ.items() if key not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
    def docker(*command):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*command],env=env,text=True).strip()
    container=None
    with tempfile.TemporaryDirectory(prefix='mfa-pg-private-') as private:
        password=secrets.token_hex(32);path=Path(private)/'postgres.env'
        with open(path,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:stream.write('POSTGRES_USER=mfa_fixture\nPOSTGRES_DB=mfa_fixture\nPOSTGRES_PASSWORD='+password+'\n')
        try:
            container=docker('run','--rm','-d','--user','70:70','--read-only','--cap-drop=ALL','--security-opt','no-new-privileges:true','--memory','256m','--tmpfs','/var/lib/postgresql/data:rw,uid=70,gid=70,mode=0700,size=128m','--tmpfs','/var/run/postgresql:rw,uid=70,gid=70,mode=0770','--tmpfs','/tmp:mode=1777','-p','127.0.0.1::5432','--env-file',str(path),os.environ.get('MFA_TEST_POSTGRES_IMAGE','postgres:16-alpine@sha256:aa6cb33cf4c19c765cefcf48d96176258800870a9a1e930ad126200f9d825139'),'postgres','-c','shared_buffers=16MB','-c','max_connections=16')
            ready=False
            for attempt in range(50):
                probe=subprocess.run(['docker','--host=unix:///var/run/docker.sock','exec',container,'pg_isready','-h','127.0.0.1','-U','mfa_fixture','-d','mfa_fixture'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                if probe.returncode==0:ready=True;break
                time.sleep(.1)
            if not ready:raise RuntimeError('Temporary PostgreSQL not ready')
            port=docker('port',container,'5432/tcp').rsplit(':',1)[1]
            child_env={**os.environ,'MFA_PG_FIXTURE':'1','MFA_TEST_CONTAINER':container,'MFA_TEST_DATABASE_URL':'postgresql://mfa_fixture:'+password+'@127.0.0.1:'+port+'/mfa_fixture','PYTHONDONTWRITEBYTECODE':'1'}
            subprocess.run([sys.executable,__file__,'--worker'],cwd=ROOT,env=child_env,check=True,timeout=210)
        finally:
            if container:
                subprocess.run(['docker','--host=unix:///var/run/docker.sock','stop',container],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=15)
if __name__=='__main__':main()
