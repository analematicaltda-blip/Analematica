"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['PURCHASE_RETURNS_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/purchase_returns_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='purchase-returns-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['PURCHASE_RETURNS_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
  import django;django.setup()
  from django.db import connection,connections
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from apps.core_erp.tenancy.models import Tenant
  from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
  from apps.core_erp.outbox_models import OutboxEvent
  from apps.prestadores.mi_negocio.gestion_contable.compras import native_purchase as native,purchase_item_returns as engine
  from apps.prestadores.mi_negocio.gestion_contable.compras.models import Proveedor,FacturaCompra
  from apps.turismo.models import TourismProvider,BusinessProfile,VerifiedCompanyLink
  from apps.turismo.services.company_identity import review_link
  from apps.core_erp.accounting import tax_policies
  from apps.core_erp.accounting.ledger_engine import LedgerEngine
  from apps.core_erp.accounting.exceptions import AccountingError
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
   for model in [AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,Proveedor,FacturaCompra,VerifiedCompanyLink,BusinessProfile]:create(model)
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='purchase_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='purchase-return-restricted-fixture')
  runtime_role(None,connection)
  with connection.cursor() as cursor:
   cursor.execute('SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user');identity=cursor.fetchone()
   assert identity==(role,False,False),identity
  try:
   with transaction.atomic():
    with connection.cursor() as cursor:cursor.execute('CREATE TABLE public.forbidden_fixture_ddl (id integer)')
  except DatabaseError:pass
  else:raise AssertionError('Runtime role unexpectedly has DDL rights')
  user=get_user_model()(username='synthetic-purchase-owner',role='BUSINESS_OWNER');operator=get_user_model()(username='synthetic-identity-reviewer',is_active=True,is_superuser=True,is_staff=True);get_user_model().objects.bulk_create([user,operator])
  from datetime import timedelta
  results=[]
  for scenario in ['same_review','competing_capacity','same_correction','competing_corrections','return_vs_full_reversal','proof_failure']:
   company=Tenant.objects.create(name='Synthetic purchase race',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Synthetic purchase chart')
   provider=TourismProvider.objects.create(owner=user,name='Synthetic race provider',provider_type='GUIDE')
   BusinessProfile.objects.create(provider=provider,legal_name='Synthetic company',tax_id=company.tax_id,business_address='fixture',phone='fixture',email='fixture@example.test')
   review_link(operator=operator,provider_id=provider.pk,tenant_id=company.pk,evidence_digest='a'*64,valid_until=timezone.now()+timedelta(days=1),apply=True)
   def account(code,kind):return Account.plain_objects.create(tenant=company,chart_of_accounts=chart,code=code,name='Synthetic '+kind,type=kind)
   expense=account('510001','EXPENSE');other=account('510002','EXPENSE');vat=account('135001','ASSET');ret=account('236001','LIABILITY');payable=account('220001','LIABILITY')
   day=timezone.localdate().isoformat();FiscalPeriod.plain_objects.create(tenant=company,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open')
   policy={'code':'PURCHASE_PG','jurisdiction':'CO','currency':'COP','valid_from':'2026-01-01','valid_until':'2026-12-31','rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'INPUT','kind':'INPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']},{'code':'RET','kind':'WITHHOLDING','rate_bps':250,'applies_to':['TAXABLE']}]}
   r=tax_policies.review_policy(company.pk,actor=user,policy=policy,evidence_digest='a'*64,expected_revision=0,confirmed=True);tax_policies.record_policy(company.pk,actor=user,review_id=r['review_id'],confirmed=True)
   scope={'actor':user,'provider_id':provider.pk};supplier=native.record_supplier(**scope,request_id=str(uuid.uuid4()),name='Synthetic supplier',identification='PG-'+uuid.uuid4().hex[:12].upper(),evidence_digest='a'*64,confirmed=True)
   capture=native.record_invoice(**scope,request_id=str(uuid.uuid4()),supplier_id=supplier['supplier_id'],number='SYNTHETIC-PG',issue_date=day,due_date=None,subtotal='100.00',tax='11.40',gross='111.40',document_digest=uuid.uuid4().hex*2,evidence_digest='b'*64,confirmed=True)
   first_id,second_id=str(uuid.uuid4()),str(uuid.uuid4());items=[{'item_id':first_id,'net':'60.00','tax_category':'TAXABLE','policy_code':policy['code'],'policy_revision':1,'basis_account_id':str(expense.pk),'tax_accounts':{'INPUT':str(vat.pk),'RET':str(ret.pk)}},{'item_id':second_id,'net':'40.00','tax_category':'EXCLUDED','policy_code':policy['code'],'policy_revision':1,'basis_account_id':str(other.pk),'tax_accounts':{}}]
   review=native.review_purchase(**scope,invoice_id=capture['invoice_id'],selection=items,settlement_account_id=str(payable.pk),economic_fact='GOODS_OR_SERVICES_RECEIVED',evidence_digest='c'*64,expected_revision=0,confirmed=True);native.post_purchase(**scope,invoice_id=capture['invoice_id'],review_id=review['review_id'],confirmed=True)
   scope['invoice_id']=capture['invoice_id']
   def review_return():return engine.review(**scope,return_id=str(uuid.uuid4()),selection=[{'item_id':first_id,'net':'40.00'}],entry_date=day,document_digest=uuid.uuid4().hex*2,evidence_digest='d'*64,expected_revision=0,confirmed=True)
   first=review_return();action=engine.post
   if scenario=='proof_failure':
    original=OutboxEvent.objects.create
    def create_event(**kw):
     if kw.get('event_type')==engine.POSTED:raise RuntimeError('Synthetic evidence failure')
     return original(**kw)
    with patch.object(OutboxEvent.objects,'create',side_effect=create_event):
     try:engine.post(**scope,review_id=first['review_id'],confirmed=True)
     except RuntimeError:pass
     else:raise AssertionError('Proof failure did not abort posting')
    assert JournalEntry.plain_objects.filter(tenant=company,is_posted=True).count()==1
    assert engine.state(**scope)['revision']==0
    applied=engine.post(**scope,review_id=first['review_id'],confirmed=True);assert applied['revision']==1
    results.append({'scenario':scenario,'rollback_then_retry_single_effect':True});continue
   if scenario in ['same_correction','competing_corrections']:
    engine.post(**scope,review_id=first['review_id'],confirmed=True)
    def review_correction():return engine.review_void(**scope,return_id=first['return_id'],request_id=str(uuid.uuid4()),entry_date=day,reason_code='DATA_ENTRY_ERROR',evidence_digest='e'*64,expected_revision=1,confirmed=True)
    first=review_correction();second=first if scenario=='same_correction' else review_correction();action=engine.post_void
   elif scenario=='return_vs_full_reversal':
    second=native.review_purchase_reversal(**scope,reason_code='CORRECTION',evidence_digest='f'*64,confirmed=True)
   else:second=first if scenario=='same_review' else review_return()
   connections.close_all();barrier=Barrier(2)
   def attempt(task):
    index,review=task
    try:
     barrier.wait(timeout=10);operation=native.reverse_purchase if scenario=='return_vs_full_reversal' and index==1 else action
     result=operation(**scope,review_id=review['review_id'],confirmed=True)
     return {'accepted':True,'journal_id':result['journal_id'],'replayed':result.get('replayed',False)}
    except AccountingError:return {'accepted':False}
    finally:connections.close_all()
   with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(attempt,enumerate([first,second])))
   accepted=[a for a in answers if a['accepted']]
   if scenario in ['same_review','same_correction']:assert len(accepted)==2 and len({a['journal_id'] for a in accepted})==1 and sum(a['replayed'] for a in accepted)==1,answers
   else:assert len(accepted)==1,answers
   state=engine.state(**scope);original_reversed=state['original_reversed'];active=[e for e in state['returns'] if not e.get('reversed',False)]
   if scenario in ['same_correction','competing_corrections']:assert len(active)==0 and state['items'][0]['returned']['net']=='0.00'
   elif original_reversed:assert not active
   else:assert len(active)==1
   assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid']
   results.append({'scenario':scenario,'accepted':len(accepted),'single_effect':True,'ledger_integrity':True})
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'restricted_fixture_role':True,'runtime_ddl_denied':True,'scenarios':results,'production_roles_qualified':False,'supplier_identity_independently_verified':False,'production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-purchase-returns-'+uuid.uuid4().hex[:12];database='purchase_returns_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='purchase-returns-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'PURCHASE_RETURNS_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='purchase-returns-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL purchase fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
