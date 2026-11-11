"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['ACC003_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/acc003_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='acc003-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['ACC003_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
  import django;django.setup()
  from django.db import connection,connections
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from apps.core_erp.tenancy.models import Tenant
  from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
  from apps.core_erp.outbox_models import OutboxEvent
  from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
  from apps.core_erp.accounting.delivery_models import AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance
  from apps.core_erp.accounting import delivery
  os.environ['ACCOUNTING_LOCAL_PROJECTION_ENABLED']='1'
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
   for model in [AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,AccountingRatioPolicy,AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance]:create(model)
  from apps.core_erp.accounting import sql_guards
  sql_guards.install(connection)
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='acc003_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='acc003-restricted-fixture')
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
  for scenario in ['same_event','changed_payload','receipt_failure','outbox_failure','consumer_retry']:
   company=Tenant.objects.create(name='ACC003 atomic acceptance',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Scoped chart');a=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='111005',name='Cash',type='ASSET');b=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='130505',name='Receivable',type='ASSET');day=timezone.localdate();FiscalPeriod.plain_objects.create(tenant=company,period_start=day,period_end=day,status='open')
   def args(amount='10.00'):return {'tenant_id':company.pk,'entry_date':day,'description':'Atomic retry','lines_data':[{'account':a,'debit':amount},{'account':b,'credit':amount}],'actor':user,'idempotency_key':'ACC003-shared-key'}
   if scenario in ['same_event','changed_payload']:
    connections.close_all();barrier=Barrier(2)
    def attempt(amount):
     try:
      barrier.wait(timeout=10);entry=LedgerEngine.post_lines(**args(amount));return {'accepted':True,'journal_id':str(entry.pk)}
     except AccountingError:return {'accepted':False}
     finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(attempt,['10.00','11.00' if scenario=='changed_payload' else '10.00']))
    accepted=[v for v in answers if v['accepted']];assert len(accepted)==(1 if scenario=='changed_payload' else 2),answers;assert len({v['journal_id'] for v in accepted})==1;results.append({'scenario':scenario,'accepted':len(accepted),'single_effect':True})
   elif scenario in ['receipt_failure','outbox_failure']:
    manager=AccountingEventReceipt.objects if scenario=='receipt_failure' else OutboxEvent.objects
    with patch.object(manager,'create',side_effect=OSError('Synthetic interrupted transaction')):
     try:LedgerEngine.post_lines(**args())
     except OSError:pass
     else:raise AssertionError('Failure was not exercised')
    assert not JournalEntry.plain_objects.filter(tenant=company).exists();assert not LedgerEntry.plain_objects.filter(tenant=company).exists();assert not AccountingAuditLog.plain_objects.filter(tenant=company).exists();assert not AccountingEventReceipt.objects.filter(tenant=company).exists();assert not OutboxEvent.objects.filter(payload__tenant_id=str(company.pk)).exists();entry=LedgerEngine.post_lines(**args());assert LedgerEngine.post_lines(**args()).pk==entry.pk;results.append({'scenario':scenario,'whole_transaction_rolled_back_then_single_retry':True})
   else:
    entry=LedgerEngine.post_lines(**args());delivery.enqueue(company.pk);lease=delivery.claim(company.pk)
    with patch.object(AccountingProjectionReceipt.objects,'create',side_effect=OSError('Synthetic consumer interruption')):
     try:delivery.consume(company.pk,lease['id'],lease['token'])
     except OSError:pass
     else:raise AssertionError('Consumer failure was not exercised')
    assert not AccountingDailyBalance.objects.filter(tenant=company).exists();delivery.consume(company.pk,lease['id'],lease['token']);AccountingDelivery.objects.filter(pk=lease['id']).update(status='RETRY',next_attempt_at=timezone.now(),delivered_at=None);again=delivery.claim(company.pk);assert delivery.consume(company.pk,again['id'],again['token'])['applied'] is False;assert AccountingDailyBalance.objects.get(tenant=company,account=a).debit==Decimal('10.00');results.append({'scenario':scenario,'projection_atomic_and_lost_ack_effect_once':True})
   assert JournalEntry.plain_objects.filter(tenant=company,is_posted=True).count()==1;assert AccountingEventReceipt.objects.filter(tenant=company).count()==1;assert OutboxEvent.objects.filter(payload__tenant_id=str(company.pk),event_type='accounting.entry.posted.v2').count()==1
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_roles_qualified':False,'restricted_fixture_role':True,'runtime_ddl_denied':True,'acceptance_scope':'ACC003 original idempotency and transactional outbox criteria only','production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-acc003-'+uuid.uuid4().hex[:12];database='acc003_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='acc003-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'ACC003_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='acc003-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL ACC003 acceptance fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
