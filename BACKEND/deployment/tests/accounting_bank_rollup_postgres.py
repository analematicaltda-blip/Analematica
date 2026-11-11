"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['BANK_ROLLUP_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/bank_rollup_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='bank-rollup-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['BANK_ROLLUP_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
  import django;django.setup()
  from django.db import connection,connections
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from apps.core_erp.tenancy.models import Tenant
  from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
  from apps.core_erp.outbox_models import OutboxEvent
  from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
  from apps.core_erp.accounting import bank_period_rollup as engine,bank_grouped as grouped,ratios
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
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='bank_rollup_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='bank-rollup-restricted-fixture')
  runtime_role(None,connection)
  with connection.cursor() as cursor:
   cursor.execute('SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user');identity=cursor.fetchone()
   assert identity==(role,False,False),identity
  try:
   with transaction.atomic():
    with connection.cursor() as cursor:cursor.execute('CREATE TABLE public.forbidden_fixture_ddl (id integer)')
  except DatabaseError:pass
  else:raise AssertionError('Runtime role unexpectedly has DDL rights')
  user=get_user_model()(username='synthetic-bank-reviewer',role='BUSINESS_OWNER');get_user_model().objects.bulk_create([user])
  results=[]
  for scenario in ['same_review','confirm_vs_release','proof_failure']:
   company=Tenant.objects.create(name='Synthetic bank rollup race',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Synthetic bank chart')
   cash=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='111005',name='Synthetic cash',type='ASSET');income=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='410005',name='Synthetic income',type='REVENUE');liability=Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code='210005',name='Synthetic liability',type='LIABILITY')
   FiscalPeriod.plain_objects.create(tenant=company,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open');day=timezone.localdate().isoformat()
   ratios.configure(company.pk,actor=user,mapping={'cash_equivalents':[str(cash.pk)],'temporary_investments':[],'immediate_receivables':[],'current_liabilities':[str(liability.pk)]},evidence_digest='a'*64,expected_revision=0,confirmed=True)
   journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=timezone.localdate(),description='Synthetic bank receipt',actor=user,idempotency_key='synthetic-cash',lines_data=[{'account':cash,'debit':'10.00'},{'account':income,'credit':'10.00'}]);line=LedgerEntry.plain_objects.get(journal_entry=journal,account=cash);ids=[]
   for name,amount in [('first','6.00'),('second','4.00')]:
    text='transaction_id,date,direction,amount,currency\n'+name+','+day+',IN,'+amount+',COP\n';r=grouped.review(company.pk,actor=user,account_id=str(cash.pk),csv_text=text,groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':str(line.pk),'amount':amount}]}],evidence_digest='b'*64,expected_revision=0,confirmed=True);ids.append(grouped.confirm(company.pk,actor=user,statement_id=r['statement_id'],review_id=r['review_id'],confirmed=True)['reconciliation_id'])
   terms={'since':day,'until':day,'opening':'0.00','closing':'10.00','statement_complete':True,'evidence_digest':'c'*64};review=engine.review(company.pk,actor=user,account_id=str(cash.pk),reconciliation_ids=ids,period=terms,expected_revision=0,confirmed=True)
   if scenario=='proof_failure':
    create_event=OutboxEvent.objects.create
    def fail(**kw):
     if kw.get('event_type')==engine.APPLIED:raise RuntimeError('Synthetic rollup proof failure')
     return create_event(**kw)
    with patch.object(OutboxEvent.objects,'create',side_effect=fail):
     try:engine.confirm(company.pk,actor=user,review_id=review['review_id'],confirmed=True)
     except RuntimeError:pass
     else:raise AssertionError('Rollup proof failure did not abort')
    assert not OutboxEvent.objects.filter(event_type=engine.APPLIED,payload__company_id=str(company.pk)).exists()
    assert engine.confirm(company.pk,actor=user,review_id=review['review_id'],confirmed=True)['period_reconciled'];results.append({'scenario':scenario,'rollback_then_retry_single_confirmation':True})
   else:
    release=grouped.review_release(company.pk,actor=user,reconciliation_id=ids[0],reason_code='WRONG_MATCH',evidence_digest='d'*64,confirmed=True) if scenario=='confirm_vs_release' else None
    connections.close_all();barrier=Barrier(2)
    def attempt(action):
     try:
      barrier.wait(timeout=10)
      if action=='release':grouped.confirm_release(company.pk,actor=user,review_id=release['review_id'],confirmed=True);return {'accepted':True,'released':True}
      a=engine.confirm(company.pk,actor=user,review_id=review['review_id'],confirmed=True);return {'accepted':True,'confirmation_id':a['confirmation_id'],'replayed':a['replayed']}
     except AccountingError:return {'accepted':False}
     finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(attempt,['confirm','release' if release else 'confirm']))
    if release:
     assert answers[1]['accepted'],answers
     state=engine.state(company.pk,actor=user,account_id=str(cash.pk),since=day,until=day);assert state['source_current'] is False and (state['applied'] is None or state['applied']['period_reconciled'] is False)
     results.append({'scenario':scenario,'release_always_invalidates_current_qualification':True,'confirmation_won_race':answers[0]['accepted']})
    else:
     assert all(a['accepted'] for a in answers) and len({a['confirmation_id'] for a in answers})==1 and sum(a['replayed'] for a in answers)==1,answers
     results.append({'scenario':scenario,'single_confirmation_and_replay':True})
   assert JournalEntry.plain_objects.filter(tenant=company,is_posted=True).count()==1
   assert OutboxEvent.objects.filter(event_type=engine.APPLIED,payload__company_id=str(company.pk)).count()<=1
   assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid']
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'scenarios':results,'production_roles_qualified':False,'restricted_fixture_role':True,'runtime_ddl_denied':True,'bank_source_authenticity_verified':False,'production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-bank-rollup-'+uuid.uuid4().hex[:12];database='bank_rollup_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='bank-rollup-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'BANK_ROLLUP_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='bank-rollup-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL bank rollup fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
