"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['ACC004_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/acc004_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='acc004-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['ACC004_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
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
  role='acc004_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='acc004-restricted-fixture')
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
  cases=[(scenario,mode) for scenario in ['close_vs_post','close_vs_reverse'] for mode in ['simultaneous','close_first','ledger_first']]+[(scenario,'simultaneous') for scenario in ['duplicate_reversal','disjoint_accounts','account_deactivate_vs_post','reversal_failure']]
  cases += [('account_identity_vs_post',mode) for mode in ['simultaneous','close_first','ledger_first']]
  for scenario,mode in cases:
   company=Tenant.objects.create(name='ACC004 concurrency acceptance',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Scoped chart');accounts=[Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code=code,name='Synthetic '+code,type=kind) for code,kind in [('1105','ASSET'),('4105','REVENUE'),('1106','ASSET'),('4106','REVENUE')]];day=timezone.localdate();period=FiscalPeriod.plain_objects.create(tenant=company,period_start=day,period_end=day,status='open')
   def args(index=0):
    left,right=accounts[index*2:index*2+2]
    return {'tenant_id':company.pk,'entry_date':day,'description':'ACC004 ordered posting','lines_data':[{'account':right,'credit':'10.00'},{'account':left,'debit':'10.00'}],'actor':user,'idempotency_key':'ACC004-'+str(index)}
   original=LedgerEngine.post_lines(**args()) if scenario in ['close_vs_reverse','duplicate_reversal','reversal_failure'] else None
   if scenario=='reversal_failure':
    create=AccountingAuditLog.objects.create
    def fail(**kw):
     if kw.get('action')=='REVERSE':raise OSError('Synthetic reversal interrupted')
     return create(**kw)
    with patch.object(AccountingAuditLog.objects,'create',side_effect=fail):
     try:LedgerEngine.reverse_entry(original.pk,tenant_id=company.pk,actor=user)
     except OSError:pass
     else:raise AssertionError('Reversal failure was not exercised')
    assert JournalEntry.plain_objects.filter(tenant=company).count()==1;assert OutboxEvent.objects.filter(payload__tenant_id=str(company.pk)).count()==1;assert LedgerEngine.reverse_entry(original.pk,tenant_id=company.pk,actor=user).is_posted;results.append({'scenario':scenario,'rollback_then_one_reversal':True});continue
   connections.close_all();barrier=Barrier(2)
   from threading import Event
   from contextlib import contextmanager
   from apps.core_erp.accounting.validation import lock_company
   gate=Event()
   @contextmanager
   def ordered_transaction(index):
    if mode=='simultaneous':yield;return
    with transaction.atomic():
     if index==(1 if mode=='close_first' else 0):lock_company(company.pk);gate.set()
     else:assert gate.wait(10)
     yield
   def attempt(index):
    ordered=[]
    def inspect(execute,sql,params,many,context):
     if 'FROM "core_erp_account"' in sql and 'FOR UPDATE' in sql:
      assert 'ORDER BY "core_erp_account"."id" ASC' in sql
      ordered.append(True)
     return execute(sql,params,many,context)
    try:
     barrier.wait(timeout=10)
     with ordered_transaction(index),connection.execute_wrapper(inspect):
      if index and scenario in ['close_vs_post','close_vs_reverse']:
       if mode=='close_first':FiscalPeriod.plain_objects.select_for_update().filter(pk=period.pk).update(status='closed')
       else:
        row=FiscalPeriod.plain_objects.get(pk=period.pk);row.status='closed';row.save()
       return {'accepted':True,'operation':'close'}
      if index and scenario=='account_identity_vs_post':
       Account.plain_objects.filter(pk=accounts[0].pk).update(code='REVIEWED-NEW-CODE');return {'accepted':True,'operation':'change_identity'}
      if index and scenario=='account_deactivate_vs_post':
       Account.plain_objects.select_for_update().filter(pk=accounts[0].pk).update(is_active=False);return {'accepted':True,'operation':'deactivate'}
      if scenario in ['close_vs_reverse','duplicate_reversal']:entry=LedgerEngine.reverse_entry(original.pk,tenant_id=company.pk,actor=user)
      else:entry=LedgerEngine.post_lines(**args(index if scenario=='disjoint_accounts' else 0))
      assert ordered
      return {'accepted':True,'operation':'ledger','journal_id':str(entry.pk),'ordered_account_locks':len(ordered)}
    except (AccountingError,PermissionError):return {'accepted':False}
    finally:connections.close_all()
   with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(attempt,[0,1]))
   accepted=[v for v in answers if v['accepted'] and v.get('operation')=='ledger'];count=JournalEntry.plain_objects.filter(tenant=company,is_posted=True).count()
   if scenario=='duplicate_reversal':assert len(accepted)==1 and count==2,answers
   elif scenario=='disjoint_accounts':assert len(accepted)==2 and count==2,answers
   elif scenario=='account_identity_vs_post':
    assert count==1 and len(accepted)==1,answers
    changed=Account.plain_objects.get(pk=accounts[0].pk).code=='REVIEWED-NEW-CODE'
    if mode=='ledger_first':assert not changed and not answers[1]['accepted'],answers
    if mode=='close_first':assert changed and answers[1]['accepted'],answers
   elif scenario=='account_deactivate_vs_post':assert count in [0,1] and not Account.plain_objects.get(pk=accounts[0].pk).is_active,answers
   else:
    closed=FiscalPeriod.plain_objects.get(pk=period.pk);assert closed.status=='closed';assert count in ([1,2] if original else [0,1]),answers
    if accepted:assert JournalEntry.plain_objects.get(pk=accepted[0]['journal_id']).posted_at<=closed.updated_at
   if mode=='close_first' and scenario!='account_identity_vs_post':assert len(accepted)==0,answers
   if mode=='ledger_first':assert len(accepted)==1,answers
   assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid'];assert OutboxEvent.objects.filter(payload__tenant_id=str(company.pk),event_type='accounting.entry.posted.v2').count()==count;results.append({'scenario':scenario,'ordering':mode,'posted':count,'valid_serial_outcome':True,'no_deadlock':True,'accepted_ledger_operations':len(accepted)})
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_roles_qualified':False,'restricted_fixture_role':True,'runtime_ddl_denied':True,'acceptance_scope':'ACC004 period/post/reversal races and consistent account locking criteria only','production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-acc004-'+uuid.uuid4().hex[:12];database='acc004_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='acc004-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'ACC004_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='acc004-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL ACC004 acceptance fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
