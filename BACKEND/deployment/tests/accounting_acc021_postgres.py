"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['ACC021_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/acc021_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='acc021-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['ACC021_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
  import django;django.setup()
  from django.db import connection,connections
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from apps.core_erp.tenancy.models import Tenant
  from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
  from apps.core_erp.outbox_models import OutboxEvent
  from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
  from apps.turismo.models import TourismProvider,BusinessProfile,VerifiedCompanyLink
  from apps.turismo.services.company_identity import review_link,resolve_company
  from rest_framework.exceptions import APIException
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
   for model in [AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,AccountingRatioPolicy,AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance,TourismProvider,BusinessProfile,VerifiedCompanyLink]:create(model)
  from apps.core_erp.accounting import sql_guards
  sql_guards.install(connection)
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='acc021_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='acc021-restricted-fixture')
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
  operator=get_user_model()(username='synthetic-independent-reviewer',is_superuser=True,is_staff=True);get_user_model().objects.bulk_create([operator])
  def fixture(coincident=False):
   company=Tenant.objects.create(name='ACC021 authoritative mapping',tax_id=uuid.uuid4().hex,state='ACTIVE');provider=TourismProvider.objects.create(id=company.pk if coincident else uuid.uuid4(),owner=user,name='Synthetic provider',provider_type='GUIDE');BusinessProfile.objects.create(provider=provider,legal_name='Synthetic company',tax_id=company.tax_id,business_address='test',phone='test',email='fixture@example.test');return company,provider
  company,provider=fixture()
  review_link(operator=operator,provider_id=provider.pk,tenant_id=company.pk,evidence_digest='a'*64,valid_until=timezone.now()+__import__('datetime').timedelta(days=1),apply=True)
  from apps.core_erp.accounting import financial_orchestration as rehearsal
  scope={'actor':user,'provider_id':provider.pk}
  def intent():return {'schema':'sgacd-financial-rehearsal-v1','company_id':str(company.pk),'request_id':str(uuid.uuid4()),'purpose':'SUPPLIER_PAYMENT','amount':'10.00','currency':'COP','beneficiary_ref':str(uuid.uuid4()),'source_evidence_digest':'a'*64}
  def race(job):
   connections.close_all();barrier=Barrier(2)
   def attempt(index):
    try:barrier.wait(timeout=10);return job(index)
    finally:connections.close_all()
   with ThreadPoolExecutor(max_workers=2) as pool:return list(pool.map(attempt,[0,1]))
  before=JournalEntry.plain_objects.count();i=intent()
  plans=race(lambda _:rehearsal.prepare(company.pk,**scope,intent=i,confirmed=True));assert sorted(p['replayed'] for p in plans)==[False,True];p=plans[0];args={'request_id':p['request_id'],'plan_digest':p['plan_digest'],'confirmed':True};assert OutboxEvent.objects.filter(aggregate_root=p['request_id']).count()==1;results.append('concurrent_prepare_one_intent')
  rehearsal.confirm(company.pk,**scope,**args,step=1)
  confirmations=race(lambda _:rehearsal.confirm(company.pk,**scope,**args,step=2));assert sorted(r['replayed'] for r in confirmations)==[False,True];assert OutboxEvent.objects.filter(aggregate_root=p['request_id']).count()==3;results.append('concurrent_second_confirmation_single_evidence')
  def competing(index):
   try:
    if index:return rehearsal.cancel(company.pk,**scope,**args)['status']
    return rehearsal.simulate(company.pk,**scope,**args,impact_confirmation='SIMULAR 10.00 COP A '+i['beneficiary_ref'])['status']
   except AccountingError:return 'BLOCKED'
  raced=race(competing);assert 'CANCELLED' in raced;state=rehearsal.state(company.pk,**scope,request_id=p['request_id']);assert state['status']=='CANCELLED' and not state['can_simulate'];assert OutboxEvent.objects.filter(aggregate_root=p['request_id']).count() in (4,5);results.append('cancel_simulate_race_serialized_without_payment')
  retries=race(lambda _:rehearsal.cancel(company.pk,**scope,**args));assert all(r['replayed'] for r in retries);assert JournalEntry.plain_objects.count()==before;results.append('concurrent_cancel_retries_no_duplicates_or_journal')
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'restricted_fixture_role':True,'production_roles_qualified':False,'payment_executed':False,'desktop_job_created':False,'production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-acc021-'+uuid.uuid4().hex[:12];database='acc021_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='acc021-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'ACC021_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='acc021-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL ACC021 acceptance fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
