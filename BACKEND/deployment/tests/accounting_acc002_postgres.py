"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['ACC002_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/acc002_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='acc002-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['ACC002_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
  import django;django.setup()
  from django.db import connection,connections
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from apps.core_erp.tenancy.models import Tenant
  from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
  from apps.core_erp.outbox_models import OutboxEvent
  from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
  from apps.core_erp.accounting import chunked_opening as engine
  from apps.core_erp.accounting.journal_service import JournalService
  from apps.core_erp.accounting.exceptions import AccountingError
  from apps.core_erp.accounting.ledger_engine import LedgerEngine
  from concurrent.futures import ThreadPoolExecutor
  from threading import Barrier
  from unittest.mock import patch
  from datetime import date
  assert connection.vendor=='postgresql';created=set();visiting=set()
  with connection.schema_editor() as editor:
   def create(model):
    model=model._meta.concrete_model
    if model in created or model in visiting:return
    visiting.add(model)
    for field in model._meta.local_fields:
     if field.is_relation and field.remote_field and field.remote_field.model is not model:create(field.remote_field.model)
    for field in model._meta.local_many_to_many:create(field.remote_field.model)
    editor.create_model(model);created.add(model);visiting.remove(model)
   for model in [AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,AccountingRatioPolicy]:create(model)
  from apps.core_erp.accounting import sql_guards
  sql_guards.install(connection)
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='acc002_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='acc002-restricted-fixture')
  runtime_role(None,connection)
  with connection.cursor() as cursor:
   cursor.execute('SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user');identity=cursor.fetchone()
   assert identity==(role,False,False),identity
  try:
   with transaction.atomic():
    with connection.cursor() as cursor:cursor.execute('CREATE TABLE public.forbidden_fixture_ddl (id integer)')
  except DatabaseError:pass
  else:raise AssertionError('Runtime role unexpectedly has DDL rights')
  from decimal import Decimal
  user=get_user_model()(username='synthetic-opening-reviewer',role='BUSINESS_OWNER');get_user_model().objects.bulk_create([user]);results=[]
  from decimal import Decimal
  from apps.core_erp.accounting.posting_write import permits
  import copy
  company=Tenant.objects.create(name='ACC002 synthetic guards',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Scoped chart');a=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='1105',name='Cash',type='ASSET');b=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='4105',name='Income',type='REVENUE');day=timezone.localdate();period=FiscalPeriod.plain_objects.create(tenant=company,period_start=day,period_end=day,status='open')
  def draft():return JournalService.create_entry(str(company.pk),day,'New UUID acceptance',[{'account':a,'debit':'10.00'},{'account':b,'credit':'10.00'}],created_by=user)
  entry=draft();assert isinstance(entry.pk,uuid.UUID);assert LedgerEntry.plain_objects.filter(journal_entry=entry).count()==2;results.append({'scenario':'new_uuid_header_lines','created_without_missing_object_error':True})
  stale=JournalEntry.plain_objects.get(pk=entry.pk);line=LedgerEntry.plain_objects.select_related('journal_entry').filter(journal_entry=entry).first();assert not line.journal_entry.is_posted
  journal=LedgerEngine.post_entry(entry.pk,tenant_id=company.pk,actor=user);original=journal.system_hash
  def model_blocked(operation):
   try:operation()
   except PermissionError:pass
   else:raise AssertionError('Expected model guard rejection')
  stale._validated_post=True;model_blocked(stale.save);model_blocked(line.save);model_blocked(line.delete);results.append({'scenario':'stale_header_and_cached_parent','save_and_delete_blocked':True})
  forged=JournalEntry(tenant=company,period=period,date=day,is_posted=True);forged._validated_post=True;model_blocked(forged.save);assert not permits(journal);results.append({'scenario':'forged_reusable_flag','blocked_and_capability_reset':True})
  clone=copy.copy(line);clone.pk=uuid.uuid4();clone._state=copy.copy(line._state);clone._state.adding=True
  def sql_blocked(operation):
   try:
    with transaction.atomic():operation()
   except DatabaseError as exc:assert 'ACCOUNTING_' in str(exc)
   else:raise AssertionError('Expected database immutability guard')
  for operation in [lambda:JournalEntry.plain_objects.filter(pk=entry.pk).update(is_posted=False),lambda:JournalEntry.plain_objects.filter(pk=entry.pk)._raw_delete('default'),lambda:LedgerEntry.plain_objects.filter(pk=line.pk).update(description='Blocked'),lambda:LedgerEntry.plain_objects.filter(pk=line.pk)._raw_delete('default'),lambda:LedgerEntry.plain_objects.bulk_create([clone]),lambda:LedgerEntry.plain_objects.bulk_update([line],['description'])]:sql_blocked(operation)
  results.append({'scenario':'queryset_bulk_and_delete','database_guards_enforced_with_runtime_write_role':True})
  journal.refresh_from_db();assert journal.system_hash==original;assert LedgerEntry.plain_objects.filter(journal_entry=journal).count()==2
  reversal=LedgerEngine.reverse_entry(journal.pk,tenant_id=company.pk,actor=user);assert reversal.pk!=journal.pk and reversal.is_posted;assert LedgerEngine.post_entry(journal.pk,tenant_id=company.pk,actor=user).pk==journal.pk;assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid'];results.append({'scenario':'normal_post_replay_and_reversal','original_preserved':True})
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_roles_qualified':False,'restricted_fixture_role':True,'runtime_ddl_denied':True,'acceptance_scope':'ACC002 original UUID and posted ORM guard criteria only','production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-acc002-'+uuid.uuid4().hex[:12];database='acc002_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='acc002-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'ACC002_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='acc002-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL ACC002 acceptance fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
