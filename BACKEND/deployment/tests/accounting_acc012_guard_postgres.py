"""Disposable PostgreSQL probes for conditional worker-safety guard bypasses."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['ACC012_GUARD_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/acc012_guard_'):raise RuntimeError('Disposable local database required.')
 from django.conf import settings
 settings.configure(INSTALLED_APPS=[],DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':parsed.path[1:],'USER':parsed.username,'PASSWORD':parsed.password,'HOST':parsed.hostname,'PORT':parsed.port}},SECRET_KEY='synthetic-disposable-test-only',REST_FRAMEWORK={})
 import django;django.setup()
 from django.db import connection
 from rest_framework.exceptions import ValidationError
 import importlib.util
 spec=importlib.util.spec_from_file_location('safety_guards',ROOT/'BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/sg_sst/worker_data_guards.py');guards=importlib.util.module_from_spec(spec);spec.loader.exec_module(guards)
 with connection.cursor() as c:
  for table in guards.TABLES:c.execute('CREATE TABLE '+table+' (id integer PRIMARY KEY, evidence text)');c.execute('INSERT INTO '+table+" VALUES (1,'preserved')")
 guards.install(connection);guards.require(connection);results=[]
 table=guards.TABLES[0];name='safety_immutable_'+table;function='safety_guard_'+table
 def replace(condition='',arguments=''):
  with connection.cursor() as c:
   c.execute('DROP TRIGGER '+name+' ON '+table)
   c.execute('CREATE TRIGGER '+name+' BEFORE UPDATE OR DELETE ON '+table+' FOR EACH ROW '+condition+' EXECUTE FUNCTION '+function+'('+arguments+')')
 def reject():
  try:guards.require(connection)
  except ValidationError:return
  raise AssertionError('Weakened guard passed readiness')
 replace('WHEN (false)');reject();results.append('conditional_false_trigger_rejected')
 # The false condition really permits SQL updates: detection must refuse service.
 with connection.cursor() as c:c.execute('UPDATE '+table+" SET evidence='tampered' WHERE id=1")
 replace(arguments="'unexpected'");reject();results.append('unexpected_trigger_arguments_rejected')
 replace();guards.require(connection)
 with connection.cursor() as c:
  try:c.execute('UPDATE '+table+" SET evidence='blocked' WHERE id=1")
  except Exception:pass
  else:raise AssertionError('Installed guard did not reject update')
 results.append('normal_guard_blocks_updates')
 with connection.cursor() as c:
  try:c.execute('TRUNCATE '+table)
  except Exception:pass
  else:raise AssertionError('Worker evidence truncation allowed')
 results.append('truncate_blocked')
 # Qualification detects a removed statement guard without auto-repair.
 with connection.cursor() as c:c.execute('DROP TRIGGER safety_truncate_'+table+' ON '+table)
 reject();results.append('missing_truncate_guard_detected')
 # Upgrade an existing populated database using the actual reversible migration.
 import importlib
 path=ROOT/'BACKEND/deployment/fresh_migrations/sg_sst/0002_prevent_evidence_truncate.py'
 spec=importlib.util.spec_from_file_location('truncate_migration',path);migration=importlib.util.module_from_spec(spec);spec.loader.exec_module(migration)
 with connection.cursor() as c:
  for other in guards.TABLES[1:]:c.execute('DROP TRIGGER safety_truncate_'+other+' ON '+other)
 from types import SimpleNamespace
 editor=SimpleNamespace(connection=connection)
 migration.forward(None,editor);guards.require(connection)
 with connection.cursor() as c:c.execute('SELECT count(*) FROM '+table);assert c.fetchone()[0]==1
 migration.backward(None,editor);reject();migration.forward(None,editor);guards.require(connection)
 results.append('populated_migration_roundtrip_preserves_rows');connection.close()
 print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-acc012_guard-'+uuid.uuid4().hex[:12];database='acc012_guard_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='acc012_guard-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'ACC012_GUARD_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='acc012_guard-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL ACC012_GUARD acceptance fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
