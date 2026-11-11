"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['ACC006_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/acc006_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='acc006-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['ACC006_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
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
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='acc006_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='acc006-restricted-fixture')
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
  from decimal import Decimal,localcontext,Inexact
  from datetime import timedelta
  for code in ['USD','COP']:Currency.objects.create(code=code,name='Synthetic '+code,symbol=code,is_active=True)
  for scenario in ['unreviewed_catalogue','invalid_quotes','concurrent_confirmation','inactive_currency','historical_reversal','reference_versions']:
   company=Tenant.objects.create(name='ACC006 FX acceptance',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Scoped chart');a=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='1105',name='Cash USD',type='ASSET');b=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='4105',name='Income',type='REVENUE');day=timezone.localdate();FiscalPeriod.plain_objects.create(tenant=company,period_start=day,period_end=day,status='open');entry=JournalService.create_entry(str(company.pk),day,'FX draft with explicit source',[{'account':a,'debit':'10.00'},{'account':b,'credit':'10.00'}],created_by=user,currency='USD');terms={'base_currency':'USD','target_currency':'COP','rate':'4000.123456','source_reference':'synthetic-pg-source','source_version':uuid.uuid4().hex,'observed_at':timezone.now().isoformat(),'valid_from':day.isoformat(),'valid_until':day.isoformat(),'evidence_digest':'a'*64}
   args={'actor':user,'entry_id':str(entry.pk),'terms':terms,'expected_revision':0,'confirmed':True}
   if scenario=='unreviewed_catalogue':
    FXRateTable.objects.create(base_currency=Currency.objects.get(code='USD'),target_currency=Currency.objects.get(code='COP'),rate='4000.000000',effective_from=timezone.now()-timedelta(days=1),version=1)
    try:LedgerEngine.post_entry(entry.pk,tenant_id=company.pk,actor=user)
    except AccountingError:pass
    else:raise AssertionError('Legacy unreviewed row authorized posting')
    assert not JournalEntry.plain_objects.get(pk=entry.pk).is_posted;results.append({'scenario':scenario,'blocked_without_effect':True});continue
   if scenario=='invalid_quotes':
    for changes in [{'rate':4000.0},{'rate':'0.000000'},{'source_reference':''},{'target_currency':'USD'},{'valid_until':(day-timedelta(days=1)).isoformat()},{'observed_at':(timezone.now()+timedelta(days=1)).isoformat()}]:
     try:reviewed_fx.review(company.pk,**{**args,'terms':{**terms,**changes}})
     except AccountingError:pass
     else:raise AssertionError('Invalid FX quote accepted')
    assert reviewed_fx.latest(company,str(entry.pk)) is None
   if scenario=='reference_versions':
    before=FXRateTable.objects.order_by('-version').first().version;connections.close_all();barrier=Barrier(2)
    def update(value):
     try:barrier.wait(timeout=10);return FXEngine.update_rate('USD','COP',value).version
     finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:versions=list(pool.map(update,['4000.123456','4001.000000']))
    assert sorted(versions)==[before+1,before+2];results.append({'scenario':scenario,'two_unique_serial_versions':True});continue
   with localcontext() as ctx:
    ctx.prec=3;ctx.traps[Inexact]=True
    review=reviewed_fx.review(company.pk,**args)
   confirm={'actor':user,'entry_id':str(entry.pk),'review_id':review['review_id'],'confirmed':True}
   if scenario=='concurrent_confirmation':
    connections.close_all();barrier=Barrier(2)
    def apply(index):
     try:barrier.wait(timeout=10);return reviewed_fx.confirm(company.pk,**confirm)
     finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(apply,[0,1]))
    assert len({v['journal_id'] for v in answers})==1 and sum(v['replayed'] for v in answers)==1
   else:
    if scenario=='inactive_currency':
     Currency.objects.filter(code='USD').update(is_active=False)
     try:reviewed_fx.confirm(company.pk,**confirm)
     except AccountingError:pass
     else:raise AssertionError('Inactive currency posted')
     assert not JournalEntry.plain_objects.get(pk=entry.pk).is_posted;Currency.objects.filter(code='USD').update(is_active=True)
    with localcontext() as ctx:
     ctx.prec=3;ctx.traps[Inexact]=True
     reviewed_fx.confirm(company.pk,**confirm)
   entry.refresh_from_db();assert entry.exchange_rate==Decimal('4000.123456');assert {r.amount_base for r in LedgerEntry.plain_objects.filter(journal_entry=entry)}=={Decimal('40001.23')}
   if scenario=='historical_reversal':
    FXEngine.update_rate('USD','COP','5000.000000');original=entry.system_hash;reverse=LedgerEngine.reverse_entry(entry.pk,tenant_id=company.pk,actor=user);assert reverse.exchange_rate==entry.exchange_rate and JournalEntry.plain_objects.get(pk=entry.pk).system_hash==original
   assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid'];results.append({'scenario':scenario,'reviewed_exact_valuation_and_replay_valid':True})
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_roles_qualified':False,'restricted_fixture_role':True,'runtime_ddl_denied':True,'acceptance_scope':'ACC006 original valid-source/validity/currency/no-fallback criteria only','production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-acc006-'+uuid.uuid4().hex[:12];database='acc006_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='acc006-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'ACC006_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='acc006-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL ACC006 acceptance fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
