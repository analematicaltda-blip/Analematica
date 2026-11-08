"""Control row-lock races in a separate database inside the isolated PG container."""
import json,os,secrets,subprocess,sys,tempfile,uuid
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit


def worker():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from fastapi import HTTPException
    root=Path(__file__).resolve().parents[3]
    sys.path[:0]=[str(root/'BACKEND/SGA-CD-BACKEND'),str(root/'BACKEND/SGA-CD-BACKEND/tests')]
    os.environ['SECRET_KEY']=secrets.token_urlsafe(32)
    import test_assistance  # Register the same model graph as isolated HTTP tests.
    from app.models.base import Base
    from app.models.user import Usuario,Role,RolesEnum,user_roles_association
    from app.models.tenancy import Inquilino
    from app.models.assistance import ControlPairing,ControlDevice,ControlJob,ControlApproval
    from app.services.assistance import control,control_crypto
    from app.services.assistance.engine import Actor
    engine=create_engine(os.environ['DATABASE_URL'],connect_args={'options':'-c lock_timeout=10000 -c statement_timeout=10000'})
    assert engine.dialect.name=='postgresql'
    tables=[model.__table__ for model in (Inquilino,Usuario,Role,ControlPairing,ControlDevice,ControlJob,ControlApproval)]+[user_roles_association]
    Base.metadata.create_all(engine,tables=tables)
    Session=sessionmaker(bind=engine,expire_on_commit=False)
    results=[]
    with tempfile.TemporaryDirectory(prefix='control-pg-private-') as private:
        os.environ['ASSISTANCE_CONTROL_KEY_DIR']=private;control_crypto.initialize()
        with Session() as db:
            db.add(Inquilino(id=1,nombre_empresa='Synthetic control tenant',activo=True));db.commit()
            db.add(Usuario(id=1,inquilino_id=1,nombre_usuario='synthetic-control',password_hash='synthetic-unused-hash',rol=RolesEnum.admin_empresa,activo=True));db.commit()
        who=Actor(1,1)
        def device(db):
            row=ControlDevice(id=str(uuid.uuid4()),user_id=1,tenant_id=1,name='Synthetic executor',kind='desktop',token_hash=control.digest(secrets.token_urlsafe(32)),scopes='["meta"]',revoked=0)
            db.add(row);db.commit();return row
        def job(db,dev,ready=False):
            value=control.create_job(db,who,dev.id,'meta','principal','browser_snapshot',{},'Isolated concurrent protocol check')
            if ready:
                for stage in (1,2):value=control.approve(db,who,value['id'],stage,value['digest'],value['confirmation_phrase'])
            return value
        for scenario in ('duplicate_approval','duplicate_begin','duplicate_result','revoke_vs_begin'):
            with Session() as db:
                dev=device(db);value=job(db,dev,ready=scenario!='duplicate_approval');device_id=dev.id
                lease=json.loads(control.begin(db,dev,value['id'])['payload'])['lease_id'] if scenario=='duplicate_result' else None
            barrier=Barrier(2)
            def attempt(index):
                with Session() as db:
                    barrier.wait(timeout=10)
                    try:
                        if scenario=='duplicate_approval':control.approve(db,who,value['id'],1,value['digest'],value['confirmation_phrase'])
                        elif scenario=='duplicate_result':control.report(db,db.get(ControlDevice,device_id),value['id'],lease,'not_delivered',{'synthetic_contract':True})
                        elif scenario=='revoke_vs_begin' and index==1:control.revoke(db,who,device_id)
                        else:control.begin(db,db.get(ControlDevice,device_id),value['id'])
                        return True
                    except HTTPException as error:
                        db.rollback();assert error.status_code==409;return False
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(attempt,index) for index in (0,1)];outcomes=[future.result(timeout=20) for future in futures]
            with Session() as db:
                row=db.get(ControlJob,value['id'])
                if scenario=='duplicate_approval':
                    assert sum(outcomes)==1 and row.approvals==1
                    assert db.query(ControlApproval).filter_by(job_id=row.id).count()==1
                elif scenario=='duplicate_begin':assert sum(outcomes)==1 and row.status=='leased'
                elif scenario=='duplicate_result':assert sum(outcomes)==1 and row.status=='not_delivered' and not json.loads(control_crypto.decrypt(row.result))['provider_success_verified']
                else:
                    assert outcomes[1] and db.get(ControlDevice,device_id).revoked
                    assert row.status in {'cancelled','stop_requested'} and row.stop_requested
                    try:control.checkpoint(db,db.get(ControlDevice,device_id),row.id,row.lease_id or '0'*48)
                    except HTTPException as error:assert error.status_code==409
                    else:raise AssertionError('Revoked device passed checkpoint')
                results.append({'scenario':scenario,'completed':sum(outcomes),'checkpoint_after_revocation_denied':scenario=='revoke_vs_begin'})
    engine.dispose();print(json.dumps({'postgresql':True,'scope':'Independent SQLAlchemy sessions/threads; no real executor','results':results}),flush=True)


def run():
    if os.environ.get('MFA_PG_FIXTURE')!='1':raise RuntimeError('Isolated PG fixture required')
    container=os.environ['MFA_TEST_CONTAINER'];parsed=urlsplit(os.environ['MFA_TEST_DATABASE_URL'])
    if parsed.hostname!='127.0.0.1' or parsed.path!='/mfa_fixture':raise RuntimeError('Private source required')
    name='control_'+uuid.uuid4().hex;created=False
    env={key:value for key,value in os.environ.items() if key not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
    def docker(*args):return subprocess.run(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=15)
    try:
        docker('exec',container,'createdb','-U','mfa_fixture',name);created=True
        env['DATABASE_URL']=urlunsplit(('postgresql+psycopg2',parsed.netloc,'/'+name,parsed.query,parsed.fragment));env['PYTHONDONTWRITEBYTECODE']='1'
        result=subprocess.run([sys.executable,__file__,'--worker'],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
        if result.returncode:
            # Fixture stderr is local-only; do not expose database URLs or tokens.
            descriptor,filename=tempfile.mkstemp(prefix='control-pg-error-');os.close(descriptor);log=Path(filename);log.write_text(result.stderr)
            raise RuntimeError('Control PostgreSQL contract failed; inspect private diagnostic '+str(log))
        return json.loads(result.stdout.splitlines()[-1])
    finally:
        if created:docker('exec',container,'dropdb','--force','-U','mfa_fixture',name)
if __name__=='__main__':
    if '--worker' in sys.argv and os.environ.get('MFA_PG_FIXTURE')=='1':worker()
    else:raise SystemExit('Run through the isolated mfa_postgres_check fixture.')
