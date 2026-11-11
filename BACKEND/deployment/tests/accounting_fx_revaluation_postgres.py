"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['FX_REVALUATION_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/fx_revaluation_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='fx-revaluation-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['FX_REVALUATION_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
  import django;django.setup()
  from django.db import connection,connections
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from apps.core_erp.tenancy.models import Tenant
  from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
  from apps.core_erp.outbox_models import OutboxEvent
  from apps.core_erp.fx.models import Currency,FXRateTable
  from apps.core_erp.accounting import fx_revaluation as fx,reviewed_fx
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
   for model in [AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,Currency,FXRateTable]:create(model)
  user=get_user_model()(username='synthetic-fx-reviewer',role='BUSINESS_OWNER');get_user_model().objects.bulk_create([user])
  for code in ('USD','COP'):Currency.objects.create(code=code,name='Synthetic '+code,symbol=code)
  results=[]
  for scenario in ['same_review','competing_reviews','proof_failure']:
   company=Tenant.objects.create(name='Synthetic FX race',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Synthetic FX chart')
   asset=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='111099',name='Synthetic USD',type='ASSET');gain=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='421099',name='Synthetic gain',type='REVENUE');loss=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='530599',name='Synthetic loss',type='EXPENSE')
   FiscalPeriod.plain_objects.create(tenant=company,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open');day=timezone.localdate().isoformat()
   terms={'base_currency':'USD','target_currency':'COP','rate':'4000.000000','source_reference':'synthetic-pg:fx','source_version':'1','observed_at':timezone.now().isoformat(),'valid_from':day,'valid_until':day,'evidence_digest':'a'*64}
   entry=JournalService.create_entry(str(company.pk),timezone.localdate(),'Synthetic PG USD',[{'account':asset,'debit':'10.00'},{'account':gain,'credit':'10.00'}],created_by=user,currency='USD');r=reviewed_fx.review(company.pk,actor=user,entry_id=str(entry.pk),terms=terms,expected_revision=0,confirmed=True);reviewed_fx.confirm(company.pk,actor=user,entry_id=str(entry.pk),review_id=r['review_id'],confirmed=True)
   arguments={'actor':user,'account_id':str(asset.pk),'currency':'USD','as_of':day,'terms':{**terms,'rate':'4200.000000','source_version':'2'},'gain_account_id':str(gain.pk),'loss_account_id':str(loss.pk),'monetary_classification':'MONETARY_DECLARED','confirmed':True}
   first=fx.review(company.pk,request_id=str(uuid.uuid4()),**arguments)
   if scenario=='proof_failure':
    original=OutboxEvent.objects.create
    def create_event(**kw):
     if kw.get('event_type')==fx.POSTED:raise RuntimeError('Synthetic evidence failure')
     return original(**kw)
    with patch.object(OutboxEvent.objects,'create',side_effect=create_event):
     try:fx.confirm(company.pk,actor=user,review_id=first['review_id'],confirmed=True)
     except RuntimeError:pass
     else:raise AssertionError('Proof failure did not abort posting')
    assert JournalEntry.plain_objects.filter(tenant=company,is_posted=True).count()==1
    applied=fx.confirm(company.pk,actor=user,review_id=first['review_id'],confirmed=True);assert applied['difference_cop']=='2000.00'
    results.append({'scenario':scenario,'rollback_then_retry_single_effect':True});continue
   second=first if scenario=='same_review' else fx.review(company.pk,request_id=str(uuid.uuid4()),**arguments)
   connections.close_all();barrier=Barrier(2)
   def attempt(review):
    try:
     barrier.wait(timeout=10);result=fx.confirm(company.pk,actor=user,review_id=review['review_id'],confirmed=True)
     return {'accepted':True,'journal_id':result['journal_id'],'replayed':result['replayed']}
    except AccountingError:return {'accepted':False}
    finally:connections.close_all()
   with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(attempt,[first,second]))
   accepted=[a for a in answers if a['accepted']]
   if scenario=='same_review':assert len(accepted)==2 and len({a['journal_id'] for a in accepted})==1 and sum(a['replayed'] for a in accepted)==1
   else:assert len(accepted)==1
   assert OutboxEvent.objects.filter(event_type=fx.POSTED,payload__company_id=str(company.pk)).count()==1
   assert AccountingEventReceipt.objects.filter(tenant=company,event_id__startswith=fx.PREFIX).count()==1
   assert JournalEntry.plain_objects.filter(tenant=company,is_posted=True).count()==2
   assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid']
   results.append({'scenario':scenario,'accepted':len(accepted),'single_adjustment_receipt_and_proof':True,'ledger_integrity':True})
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_roles_qualified':False,'rate_source_authenticity_verified':False,'production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-fx-revaluation-'+uuid.uuid4().hex[:12];database='fx_revaluation_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='fx-revaluation-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'FX_REVALUATION_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='fx-revaluation-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL FX fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
