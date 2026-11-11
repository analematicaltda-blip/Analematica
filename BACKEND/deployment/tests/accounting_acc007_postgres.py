"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['ACC007_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/acc007_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='acc007-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['ACC007_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
  import django;django.setup()
  from django.db import connection,connections
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from apps.core_erp.tenancy.models import Tenant
  from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
  from apps.core_erp.outbox_models import OutboxEvent
  from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
  from apps.core_erp.fx.models import Currency,FXRateTable
  from apps.core_erp.accounting import reviewed_fx
  from apps.core_erp.fx.fx_engine import FXEngine
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
   for model in [AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,AccountingRatioPolicy,AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance,Currency,FXRateTable]:create(model)
  from apps.core_erp.accounting import sql_guards
  sql_guards.install(connection)
  from apps.core_erp.accounting import sql_guard_hardening,sql_identity_guards
  sql_guard_hardening.install(connection);sql_identity_guards.install(connection)
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='acc007_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='acc007-restricted-fixture')
  runtime_role(None,connection)
  with connection.cursor() as cursor:
   cursor.execute('SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user');identity=cursor.fetchone()
   assert identity==(role,False,False),identity
  try:
   with transaction.atomic():
    with connection.cursor() as cursor:cursor.execute('CREATE TABLE public.forbidden_fixture_ddl (id integer)')
  except DatabaseError:pass
  else:raise AssertionError('Runtime role unexpectedly has DDL rights')
  from apps.core_erp.accounting.sql_guard_health import inspect_guards
  from decimal import Decimal
  user=get_user_model()(username='synthetic-guard-reviewer',role='BUSINESS_OWNER');get_user_model().objects.bulk_create([user]);results=[]
  company=Tenant.objects.create(name='ACC007 SQL protection',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Scoped chart');a=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='1105',name='Cash',type='ASSET');b=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='4105',name='Income',type='REVENUE');day=timezone.localdate();FiscalPeriod.plain_objects.create(tenant=company,period_start=day,period_end=day,status='open')
  args=dict(tenant_id=company.pk,entry_date=day,description='SQL guard acceptance',lines_data=[{'account':a,'debit':'10.00'},{'account':b,'credit':'10.00'}],actor=user,idempotency_key=uuid.uuid4().hex)
  entry=LedgerEngine.post_lines(**args);line=LedgerEntry.plain_objects.filter(journal_entry=entry).first();original_hash=entry.system_hash
  assert inspect_guards(connection)['ready'],inspect_guards(connection)
  def rejected(sql,params=None):
   try:
    with transaction.atomic():
     with connection.cursor() as cursor:cursor.execute(sql,params)
   except DatabaseError:pass
   else:raise AssertionError('Protected SQL unexpectedly accepted: '+sql)
  for table,identifier,changes in [('core_erp_journalentry',entry.pk,[('id',uuid.uuid4()),('is_posted',False),('currency','USD'),('description','changed')]),('core_erp_ledgerentry',line.pk,[('id',uuid.uuid4()),('amount_base',Decimal('0.01')),('currency','USD'),('account_id',b.pk)]),('core_erp_account',a.pk,[('id',uuid.uuid4()),('code','changed'),('type','LIABILITY'),('chart_of_accounts_id',uuid.uuid4()),('tenant_id',uuid.uuid4())])]:
   for field,value in changes:rejected('UPDATE '+table+' SET '+field+'=%s WHERE id=%s',[value,identifier])
   rejected('DELETE FROM '+table+' WHERE id=%s',[identifier]);results.append({'scenario':table+'_immutable_columns','mutations_blocked':len(changes)+1})
  for table in ['core_erp_journalentry','core_erp_ledgerentry']:
   rejected('TRUNCATE '+table+' CASCADE');results.append({'scenario':table+'_truncate_denied'})
  with connection.cursor() as cursor:cursor.execute('UPDATE core_erp_account SET name=%s,is_active=%s WHERE id=%s',['Visible rename',False,a.pk])
  assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid'];assert LedgerEngine.post_lines(**args).pk==entry.pk
  results.append({'scenario':'nonfinancial_metadata_and_replay','original_hash_retained':True})
  # Independent sessions race a raw account edit against normal posting.
  for iteration in range(3):
   c=Tenant.objects.create(name='SQL race',tax_id=uuid.uuid4().hex,state='ACTIVE');ch=ChartOfAccounts.plain_objects.create(tenant=c,name='Race chart');left=Account.plain_objects.create(tenant=c,chart_of_accounts=ch,code='A',name='Race cash',type='ASSET');right=Account.plain_objects.create(tenant=c,chart_of_accounts=ch,code='B',name='Race income',type='REVENUE');FiscalPeriod.plain_objects.create(tenant=c,period_start=day,period_end=day,status='open');gate=Barrier(2);connections.close_all()
   def race(index):
    try:
     gate.wait(timeout=10)
     if index==0:return LedgerEngine.post_lines(tenant_id=c.pk,entry_date=day,description='Race',lines_data=[{'account':left,'debit':'1.00'},{'account':right,'credit':'1.00'}],actor=user,idempotency_key=uuid.uuid4().hex).is_posted
     try:
      with transaction.atomic():
       with connection.cursor() as cursor:cursor.execute('UPDATE core_erp_account SET code=%s WHERE id=%s',['NEW',left.pk])
      return True
     except DatabaseError:return False
    finally:connections.close_all()
   with ThreadPoolExecutor(max_workers=2) as pool:outcomes=list(pool.map(race,[0,1]))
   assert outcomes[0] and LedgerEngine.validate_ledger_integrity(c.pk)['is_valid'],outcomes
  results.append({'scenario':'concurrent_raw_account_edit_and_post','iterations':3,'financial_hash_valid':True})
  # A temporary shadow parent must not suppress the real parent guard.
  with connection.cursor() as cursor:cursor.execute('CREATE TEMP TABLE core_erp_journalentry (id uuid,is_posted boolean)');cursor.execute('INSERT INTO pg_temp.core_erp_journalentry VALUES (%s,false)',[entry.pk])
  rejected('UPDATE public.core_erp_ledgerentry SET amount_base=%s WHERE id=%s',[Decimal('0.02'),line.pk]);results.append({'scenario':'temporary_parent_shadow_denied'})
  with connection.cursor() as cursor:cursor.execute('DROP TABLE pg_temp.core_erp_journalentry')
  # Tampering is a setup-owner operation; runtime itself has no trigger DDL.
  rejected('ALTER TABLE core_erp_journalentry DISABLE TRIGGER accounting_row_guard_v1');results.append({'scenario':'runtime_cannot_disable_triggers'})
  with connection.cursor() as cursor:
   cursor.execute('RESET ROLE')
   cursor.execute("CREATE OR REPLACE FUNCTION core_accounting_header_guard_v1() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RETURN NEW; END $$")
   cursor.execute('SET ROLE '+role)
  report=inspect_guards(connection);assert not report['ready'] and 'accounting_sql_guard_body_changed' in report['checks'],report
  assert not inspect_guards(connection)['ready'];results.append({'scenario':'replaced_function_body_detected_without_repair'})
  with connection.cursor() as cursor:cursor.execute('RESET ROLE')
  sql_guards.install(connection);sql_guard_hardening.install(connection)
  with patch.object(sql_identity_guards,'statements',side_effect=RuntimeError('Synthetic SQL guard migration failure')):
   try:sql_identity_guards.install(connection)
   except RuntimeError:pass
   else:raise AssertionError('Guard migration failure was not exercised')
  assert inspect_guards(connection)['ready'];results.append({'scenario':'failed_reinstall_rolls_back_guard_drops'})
  sql_guards.install(connection);sql_guard_hardening.install(connection);sql_identity_guards.install(connection)
  with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  assert inspect_guards(connection)['ready'];assert JournalEntry.plain_objects.get(pk=entry.pk).system_hash==original_hash
  assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid'];results.append({'scenario':'guard_reinstall_preserves_history'})
  from apps.core_erp.accounting.db_privileges import inspect_privileges
  privileges=inspect_privileges(connection);assert privileges['guarded_tables_checked']==4 and privileges['read_only'] and not privileges['ready']
  results.append({'scenario':'account_in_readonly_role_audit','guarded_tables_checked':4,'production_qualification_not_inferred_from_set_role':True})
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_roles_qualified':False,'restricted_fixture_role':True,'runtime_ddl_denied':True,'acceptance_scope':'ACC007 canonical hash and installed SQL DML guards; not production role qualification','production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-acc007-'+uuid.uuid4().hex[:12];database='acc007_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='acc007-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'ACC007_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='acc007-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL ACC007 acceptance fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
