"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['ACC008_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/acc008_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='acc008-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['ACC008_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
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
  from apps.comercial.models import Lead,Opportunity
  from apps.turismo.models import BusinessProfile,VerifiedCompanyLink
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
   for model in [AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,AccountingRatioPolicy,AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance,Currency,FXRateTable,Opportunity,BusinessProfile,VerifiedCompanyLink]:create(model)
  from apps.comercial.models import Lead,Opportunity
  from apps.turismo.models import BusinessProfile,VerifiedCompanyLink,TourismProvider
  from apps.turismo.services.company_identity import review_link
  from apps.domain_business.comercial.services import crm_fiscal as crm
  from apps.core_erp.accounting.invoice_queue import EVENT_TYPE
  from apps.core_erp.accounting import sql_guards
  sql_guards.install(connection)
  from apps.core_erp.accounting import sql_guard_hardening,sql_identity_guards
  sql_guard_hardening.install(connection);sql_identity_guards.install(connection)
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='acc008_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='acc008-restricted-fixture')
  runtime_role(None,connection)
  with connection.cursor() as cursor:
   cursor.execute('SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user');identity=cursor.fetchone()
   assert identity==(role,False,False),identity
  try:
   with transaction.atomic():
    with connection.cursor() as cursor:cursor.execute('CREATE TABLE public.forbidden_fixture_ddl (id integer)')
  except DatabaseError:pass
  else:raise AssertionError('Runtime role unexpectedly has DDL rights')
  from datetime import timedelta
  from rest_framework.exceptions import APIException
  owner=get_user_model()(username='synthetic-crm-owner',role='BUSINESS_OWNER');reviewer=get_user_model()(username='synthetic-crm-reviewer',is_active=True,is_superuser=True,is_staff=True);get_user_model().objects.bulk_create([owner,reviewer]);results=[]
  for scenario in ['binding_race','fiscal_review_race','request_race','source_change_race','request_failure_retry','processed_is_not_fiscal_acceptance','reviewer_revocation']:
   company=Tenant.objects.create(name='CRM contract acceptance',tax_id=uuid.uuid4().hex,state='ACTIVE');provider=TourismProvider.objects.create(owner=owner,name='Synthetic CRM',provider_type='GUIDE');BusinessProfile.objects.create(provider=provider,legal_name='Synthetic',tax_id=company.tax_id,business_address='test',phone='test',email='test@example.test');review_link(operator=reviewer,provider_id=provider.pk,tenant_id=company.pk,evidence_digest='a'*64,valid_until=timezone.now()+timedelta(days=1),apply=True)
   lead=Lead.objects.create(name='Synthetic',email=uuid.uuid4().hex+'@example.test');source=Opportunity.objects.create(lead=lead,stage=Opportunity.Stage.WON,estimated_revenue='100.00');items=[{'item_id':str(uuid.uuid4()),'net':'100.00','tax':'0.00','tax_category':'EXCLUDED','policy_reference':'synthetic-reviewed:1'}]
   if scenario=='request_race':
    from apps.comercial.engines.funnel_engine import FunnelEngine
    source.delete();source=FunnelEngine.create_opportunity(lead,'PRO','100.00');source=FunnelEngine.transition_stage(source,Opportunity.Stage.WON)
   binding=dict(operator=reviewer,provider_id=provider.pk,opportunity_id=source.pk,evidence_digest='b'*64,valid_until=timezone.now()+timedelta(days=1),apply=True)
   base=dict(actor=owner,provider_id=provider.pk,opportunity_id=source.pk)
   def review():return crm.review_crm_invoice(**base,items=items,evidence_digest='c'*64,expected_revision=0,confirmed=True)
   if scenario!='binding_race':crm.bind_crm_source(**binding)
   if scenario in ['binding_race','fiscal_review_race']:
    connections.close_all();barrier=Barrier(2)
    def attempt(index):
     try:
      barrier.wait(timeout=10)
      return crm.bind_crm_source(**binding) if scenario=='binding_race' else review()
     except APIException:return None
     finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(attempt,[0,1]))
    assert sum(x is not None for x in answers)==1,answers
    event=crm.BIND_EVENT if scenario=='binding_race' else crm.REVIEW_EVENT
    assert OutboxEvent.objects.filter(event_type=event,aggregate_root=str(source.pk)).count()==1;results.append({'scenario':scenario,'one_persisted_result':True});continue
   reviewed=review();req={**base,'review_id':reviewed['review_id'],'confirmed':True}
   if scenario in ['request_race','source_change_race']:
    connections.close_all();barrier=Barrier(2)
    def request(index):
     try:
      barrier.wait(timeout=10)
      if scenario=='source_change_race' and index==1:Opportunity.objects.filter(pk=source.pk).update(stage=Opportunity.Stage.LOST);return None
      try:return crm.request_crm_invoice(**req)
      except APIException:return None
     finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(request,[0,1]))
    if scenario=='request_race':assert sorted(x['replayed'] for x in answers)==[False,True] and len({x['outbox_id'] for x in answers})==1,answers
    count=OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(source.pk)).count();assert count<=1
    if scenario=='source_change_race':assert Opportunity.objects.get(pk=source.pk).stage==Opportunity.Stage.LOST
    results.append({'scenario':scenario,'requests':count,'no_duplicate_or_fabricated_confirmation':True});continue
   if scenario=='request_failure_retry':
    create=OutboxEvent.objects.create
    def fail(**kwargs):
     if kwargs.get('event_type')==EVENT_TYPE:raise OSError('Synthetic outbox failure')
     return create(**kwargs)
    with patch.object(OutboxEvent.objects,'create',side_effect=fail):
     try:crm.request_crm_invoice(**req)
     except OSError:pass
     else:raise AssertionError('Storage failure not exercised')
    assert not OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(source.pk)).exists();assert OutboxEvent.objects.filter(pk=reviewed['review_id']).exists();crm.request_crm_invoice(**req);results.append({'scenario':scenario,'review_preserved_and_retry_single_request':True});continue
   if scenario=='processed_is_not_fiscal_acceptance':
    result=crm.request_crm_invoice(**req);OutboxEvent.objects.filter(pk=result['outbox_id']).update(status='PROCESSED');again=crm.request_crm_invoice(**req);assert again['status']=='REQUEST_ONLY' and all(again[k] is False for k in crm.FLAGS);results.append({'scenario':scenario,'no_payment_fiscal_or_publication_claim':True});continue
   get_user_model().objects.filter(pk=reviewer.pk).update(is_superuser=False)
   try:crm.request_crm_invoice(**req)
   except APIException:pass
   else:raise AssertionError('Revoked reviewer accepted')
   assert not OutboxEvent.objects.filter(event_type=EVENT_TYPE,aggregate_root=str(source.pk)).exists();results.append({'scenario':scenario,'source_authority_rechecked':True})
  # Independent reviewers may themselves own another company. Never lock the
  # joined owner implicitly before locking the explicit reviewer in reverse order.
  owners=[get_user_model()(username='cross-owner-'+uuid.uuid4().hex,role='BUSINESS_OWNER',is_active=True,is_superuser=True) for _ in range(2)];get_user_model().objects.bulk_create(owners);bindings=[]
  for index in range(2):
   c=Tenant.objects.create(name='Cross-company source',tax_id=uuid.uuid4().hex,state='ACTIVE');p=TourismProvider.objects.create(owner=owners[index],name='Cross source',provider_type='GUIDE');BusinessProfile.objects.create(provider=p,legal_name='Synthetic',tax_id=c.tax_id,business_address='test',phone='test',email='test@example.test');review_link(operator=owners[1-index],provider_id=p.pk,tenant_id=c.pk,evidence_digest='a'*64,valid_until=timezone.now()+timedelta(days=1),apply=True);lead=Lead.objects.create(name='Synthetic',email=uuid.uuid4().hex+'@example.test');source=Opportunity.objects.create(lead=lead,stage='won',estimated_revenue='1.00');bindings.append(dict(operator=owners[1-index],provider_id=p.pk,opportunity_id=source.pk,evidence_digest='b'*64,valid_until=timezone.now()+timedelta(days=1),apply=True))
  connections.close_all();barrier=Barrier(2)
  def cross(index):
   try:barrier.wait(timeout=10);return crm.bind_crm_source(**bindings[index])['binding_recorded']
   finally:connections.close_all()
  with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(cross,[0,1]))
  assert answers==[True,True];results.append({'scenario':'cross_company_binding_race','both_independent_reviews_persisted':True,'no_deadlock':True})
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_roles_qualified':False,'restricted_fixture_role':True,'runtime_ddl_denied':True,'acceptance_scope':'ACC008 persisted CRM ownership and invoice request state contracts; not fiscal issuance','production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-acc008-'+uuid.uuid4().hex[:12];database='acc008_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='acc008-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'ACC008_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='acc008-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL ACC008 acceptance fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
