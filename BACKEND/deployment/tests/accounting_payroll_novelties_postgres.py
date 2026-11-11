"""Explicit, disposable loopback PostgreSQL races; never uses a project database."""
import argparse,json,os,secrets,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def worker():
 from urllib.parse import urlsplit
 parsed=urlsplit(os.environ['PAYROLL_NOVELTIES_TEST_URL'])
 if parsed.hostname!='127.0.0.1' or not parsed.path.startswith('/payroll_novelties_'):raise RuntimeError('Disposable local database required.')
 sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
 from init_local import initialize
 with tempfile.TemporaryDirectory(prefix='payroll-novelties-settings-') as private:
  initialize(private);config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
  os.environ.update(config,DATABASE_URL=os.environ['PAYROLL_NOVELTIES_TEST_URL'],BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
  import django;django.setup()
  from django.db import connection,connections
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from apps.core_erp.tenancy.models import Tenant
  from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
  from apps.core_erp.outbox_models import OutboxEvent
  from apps.prestadores.mi_negocio.gestion_contable.nomina import reviewed_payroll as engine,reviewed_novelties as novelty,models as payroll
  from apps.turismo.models import TourismProvider,BusinessProfile,VerifiedCompanyLink
  from apps.turismo.services.company_identity import review_link
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
   for model in [AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,VerifiedCompanyLink,BusinessProfile]+[getattr(payroll,n) for n in ('Empleado','Contrato','Planilla','ConceptoNomina','NovedadNomina','DetalleLiquidacion','Ausencia','IncapacidadLaboral')]:create(model)
  # DDL is setup-only. Every application connection uses the same restricted role,
  # including the independent connections used by competing threads.
  from django.db.backends.signals import connection_created
  from django.db import DatabaseError,transaction
  role='payroll_runtime_fixture'
  with connection.cursor() as cursor:
   cursor.execute('CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS')
   cursor.execute('GRANT USAGE ON SCHEMA public TO '+role)
   cursor.execute('GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO '+role)
   cursor.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO '+role)
  def runtime_role(sender,connection,**kwargs):
   with connection.cursor() as cursor:cursor.execute('SET ROLE '+role)
  connection_created.connect(runtime_role,weak=False,dispatch_uid='payroll-novelty-restricted-fixture')
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
  from types import SimpleNamespace
  import runpy
  helper=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/payroll_fixture.py'))['install']
  native_intake=os.environ.get('NATIVE_PAYROLL_SOURCE_TEST')=='1';compensation=os.environ.get('PAYROLL_SOURCE_EARNINGS_FIXTURE')=='1'
  native_correction=os.environ.get('NATIVE_PAYROLL_CORRECTION_TEST')=='1'
  results=[]
  scenarios=['capture_same_request','capture_same_reference','capture_reference_failure'] if native_intake else ['same_review','competing_payrolls','claim_failure']
  if native_correction:scenarios=['correction_same_request','correction_competing_revisions','correction_head_failure']
  for scenario in scenarios:
   company=Tenant.objects.create(name='Synthetic payroll race',tax_id=uuid.uuid4().hex,state='ACTIVE');chart=ChartOfAccounts.plain_objects.create(tenant=company,name='Synthetic payroll chart')
   provider=TourismProvider.objects.create(owner=user,name='Synthetic source provider',provider_type='GUIDE')
   BusinessProfile.objects.create(provider=provider,legal_name='Synthetic company',tax_id=company.tax_id,business_address='fixture',phone='fixture',email='fixture@example.test')
   review_link(operator=operator,provider_id=provider.pk,tenant_id=company.pk,evidence_digest='a'*64,valid_until=timezone.now()+timedelta(days=1),apply=True)
   period=FiscalPeriod.plain_objects.create(tenant=company,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open')
   args=helper(SimpleNamespace(tenant=company,provider=provider,chart=chart,period=period,user=user),create)
   args['policy'].update(code='SOURCE_PG',novelty_mode=novelty.MODE)
   concept=payroll.ConceptoNomina.objects.create(codigo=uuid.uuid4().hex[:10],descripcion='Synthetic PG source',tipo='DEDUCCION')
   if native_correction:
    from apps.prestadores.mi_negocio.gestion_contable.nomina import native_novelty as native
    source=native.record(actor=user,provider_id=provider.pk,payroll_id=args['payroll_id'],request_id=str(uuid.uuid4()),employee_id=args['workers'][0]['employee_id'],concept_id=concept.pk,event_date=timezone.localdate().isoformat(),amount='25.00',source_reference='synthetic:pg:'+scenario,evidence_digest='a'*64,authorization_digest='b'*64,confirmed=True)
    params={'actor':user,'provider_id':provider.pk,'payroll_id':args['payroll_id'],'request_id':str(uuid.uuid4()),'novelty_id':source['novelty_id'],'expected_revision':0,'event_date':timezone.localdate().isoformat(),'amount':'30.00','reason_code':'DATA_ENTRY_ERROR','evidence_digest':'c'*64,'authorization_digest':'d'*64,'confirmed':True}
    if scenario=='correction_head_failure':
     with patch.object(OutboxEvent.objects,'update_or_create',side_effect=RuntimeError('Synthetic head failure')):
      try:native.correct(**params)
      except RuntimeError:pass
      else:raise AssertionError('Head failure did not abort correction')
     assert payroll.NovedadNomina.objects.get(pk=source['novelty_id']).valor==25
     assert not OutboxEvent.objects.filter(event_type=native.CORRECTED,aggregate_root=str(source['novelty_id'])).exists()
     native.correct(**params);results.append({'scenario':scenario,'source_history_and_head_rolled_back_then_retry':True})
    else:
     connections.close_all();barrier=Barrier(2)
     def correct(request_id):
      try:
       barrier.wait(timeout=10);r=native.correct(**{**params,'request_id':request_id});return {'accepted':True,'revision':r['revision'],'replayed':r['replayed']}
      except AccountingError:return {'accepted':False}
      finally:connections.close_all()
     second=params['request_id'] if scenario=='correction_same_request' else str(uuid.uuid4())
     with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(correct,[params['request_id'],second]))
     accepted=[a for a in answers if a['accepted']]
     if scenario=='correction_same_request':assert len(accepted)==2 and sum(a['replayed'] for a in accepted)==1,answers
     else:assert len(accepted)==1,answers
     results.append({'scenario':scenario,'accepted':len(accepted),'single_correction_revision':True})
    found=native.lookup(actor=user,provider_id=provider.pk,payroll_id=args['payroll_id'],source_reference='synthetic:pg:'+scenario)
    assert found['revision']==1 and found['source']['amount']=='30.00' and found['history'][0]['before']['amount']=='25.00'
    assert not JournalEntry.plain_objects.filter(tenant=company).exists()
    continue
   if native_intake:
    from apps.prestadores.mi_negocio.gestion_contable.nomina import native_novelty as native
    params={'actor':user,'provider_id':provider.pk,'payroll_id':args['payroll_id'],'request_id':str(uuid.uuid4()),'employee_id':args['workers'][0]['employee_id'],'concept_id':concept.pk,'event_date':timezone.localdate().isoformat(),'amount':'25.00','source_reference':'synthetic:pg:'+scenario,'evidence_digest':'a'*64,'authorization_digest':'b'*64,'confirmed':True}
    if scenario=='capture_reference_failure':
     create_event=OutboxEvent.objects.create
     def fail(**kw):
      if kw.get('event_type')==native.REFERENCE:raise RuntimeError('Synthetic reference failure')
      return create_event(**kw)
     with patch.object(OutboxEvent.objects,'create',side_effect=fail):
      try:native.record(**params)
      except RuntimeError:pass
      else:raise AssertionError('Reference failure did not abort capture')
     assert not payroll.NovedadNomina.objects.filter(empleado_id=params['employee_id']).exists()
     assert not OutboxEvent.objects.filter(event_type=native.RECORDED,payload__body__company_id=str(company.pk)).exists()
     result=native.record(**params);results.append({'scenario':scenario,'rollback_then_retry_single_capture':True})
    else:
     connections.close_all();barrier=Barrier(2)
     def capture(request_id):
      try:
       barrier.wait(timeout=10);r=native.record(**{**params,'request_id':request_id});return {'accepted':True,'id':r['novelty_id'],'replayed':r['replayed']}
      except AccountingError:return {'accepted':False}
      finally:connections.close_all()
     second=params['request_id'] if scenario=='capture_same_request' else str(uuid.uuid4())
     with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(capture,[params['request_id'],second]))
     accepted=[a for a in answers if a['accepted']]
     if scenario=='capture_same_request':assert len(accepted)==2 and len({a['id'] for a in accepted})==1 and sum(a['replayed'] for a in accepted)==1,answers
     else:assert len(accepted)==1,answers
     results.append({'scenario':scenario,'accepted':len(accepted),'single_native_capture':True})
    found=native.lookup(actor=user,provider_id=provider.pk,payroll_id=args['payroll_id'],source_reference=params['source_reference'])
    assert found['found'] and not found['processed'] and found['read_only']
    assert payroll.NovedadNomina.objects.filter(empleado_id=params['employee_id']).count()==1
    assert OutboxEvent.objects.filter(event_type=native.RECORDED,payload__body__company_id=str(company.pk)).count()==1
    assert not JournalEntry.plain_objects.filter(tenant=company).exists()
    continue
   source=payroll.NovedadNomina.objects.create(empleado_id=args['workers'][0]['employee_id'],concepto=concept,fecha_evento=timezone.localdate(),valor='25.00',cantidad='1.00')
   args['workers'][0]['novelty_deductions']=[{'novelty_id':source.pk,'evidence_digest':'c'*64,'authorization_digest':'d'*64}]
   source_rows=[source];compensation=os.environ.get('PAYROLL_SOURCE_EARNINGS_FIXTURE')=='1'
   if compensation:
    args['policy'].update(novelty_mode=novelty.COMPENSATION_MODE,source_earning_rules=[])
    for c in args['policy']['components']:c['basis']='GROSS'
    items=args['workers'][0].pop('novelty_deductions')
    for field,amount in [('bonificaciones','50.00'),('comisiones','30.00')]:
     concept=payroll.ConceptoNomina.objects.create(codigo=uuid.uuid4().hex[:10],descripcion='Synthetic PG '+field,tipo='DEVENGADO')
     row=payroll.NovedadNomina.objects.create(empleado_id=args['workers'][0]['employee_id'],concepto=concept,fecha_evento=timezone.localdate(),valor=amount,cantidad='1.00');source_rows.append(row)
     args['policy']['source_earning_rules'].append({'concept_id':concept.pk,'detail_field':field});items.append({'novelty_id':row.pk,'evidence_digest':'e'*64,'authorization_digest':'f'*64})
    args['workers'][0]['novelty_items']=items
   scope={'actor':user,'provider_id':provider.pk};first=engine.review_payroll(**scope,**args)
   if scenario=='claim_failure':
    original=OutboxEvent.objects.create;claim_count=0
    def create_event(**kw):
     nonlocal claim_count
     if kw.get('event_type')==novelty.KIND:
      claim_count+=1
      if claim_count==(2 if compensation else 1):raise RuntimeError('Synthetic source proof failure')
     return original(**kw)
    with patch.object(OutboxEvent.objects,'create',side_effect=create_event):
     try:engine.post_payroll(**scope,payroll_id=args['payroll_id'],review_id=first['review_id'],confirmed=True)
     except RuntimeError:pass
     else:raise AssertionError('Consumption proof failure did not abort payroll')
    source.refresh_from_db();assert not source.procesada and source.planilla_id is None
    assert not JournalEntry.plain_objects.filter(tenant=company).exists()
    assert not payroll.NovedadNomina.objects.filter(pk__in=[r.pk for r in source_rows],procesada=True).exists()
    applied=engine.post_payroll(**scope,payroll_id=args['payroll_id'],review_id=first['review_id'],confirmed=True)
    source.refresh_from_db();assert source.procesada and str(source.planilla_id)==args['payroll_id']
    assert payroll.NovedadNomina.objects.filter(pk__in=[r.pk for r in source_rows],procesada=True).count()==len(source_rows)
    results.append({'scenario':scenario,'source_count':len(source_rows),'source_and_journal_rolled_back_then_retry':True});continue
   second_id=args['payroll_id'];second=first
   if scenario=='competing_payrolls':
    original_sheet=payroll.Planilla.objects.get(pk=args['payroll_id']);other=payroll.Planilla.objects.create(perfil_id=provider.pk,periodo_inicio=original_sheet.periodo_inicio,periodo_fin=original_sheet.periodo_fin);second_id=str(other.pk)
    second=engine.review_payroll(**scope,**{**args,'payroll_id':second_id})
   connections.close_all();barrier=Barrier(2)
   def attempt(task):
    sheet,review=task
    try:
     barrier.wait(timeout=10);result=engine.post_payroll(**scope,payroll_id=sheet,review_id=review['review_id'],confirmed=True)
     return {'accepted':True,'journal_id':result['journal_id'],'replayed':result['replayed'],'payroll_id':sheet}
    except AccountingError:return {'accepted':False}
    finally:connections.close_all()
   with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(attempt,[(args['payroll_id'],first),(second_id,second)]))
   accepted=[a for a in answers if a['accepted']]
   if scenario=='same_review':assert len(accepted)==2 and len({a['journal_id'] for a in accepted})==1 and sum(a['replayed'] for a in accepted)==1,answers
   else:assert len(accepted)==1,answers
   source.refresh_from_db();assert source.procesada and str(source.planilla_id)==accepted[0]['payroll_id']
   assert JournalEntry.plain_objects.filter(tenant=company,is_posted=True).count()==1
   assert OutboxEvent.objects.filter(pk=novelty.key(company,source.pk),event_type=novelty.KIND).count()==1
   state=engine.payroll_state(**scope,payroll_id=accepted[0]['payroll_id']);assert state['preview']['snapshot']['totals']['net']==('531.80' if compensation else '455.00') and state['applied']['journal_id']==accepted[0]['journal_id']
   assert payroll.NovedadNomina.objects.filter(pk__in=[r.pk for r in source_rows],procesada=True).count()==len(source_rows)
   assert OutboxEvent.objects.filter(event_type=novelty.KIND,payload__company_id=str(company.pk)).count()==len(source_rows)
   assert LedgerEngine.validate_ledger_integrity(company.pk)['is_valid']
   results.append({'scenario':scenario,'accepted':len(accepted),'single_source_consumption_and_journal':True,'ledger_integrity':True})
  connections.close_all();print(json.dumps({'passed':True,'postgresql':'16','disposable':True,'restricted_fixture_role':True,'runtime_ddl_denied':True,'source_earnings':compensation,'native_intake':native_intake,'native_correction':native_correction,'scenarios':results,'production_roles_qualified':False,'professional_payroll_acceptance':False,'production_ready':False}))

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--run-local-disposable',action='store_true');parser.add_argument('--with-source-earnings',action='store_true');parser.add_argument('--native-intake',action='store_true');parser.add_argument('--native-correction',action='store_true');args=parser.parse_args()
 if not args.run_local_disposable:parser.error('Explicit --run-local-disposable required')
 env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
 def docker(*args):return subprocess.check_output(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stderr=subprocess.PIPE,text=True,timeout=25).strip()
 docker('info','--format','{{.ServerVersion}}');name='sgacd-payroll-novelties-'+uuid.uuid4().hex[:12];database='payroll_novelties_'+uuid.uuid4().hex;password=secrets.token_urlsafe(32);started=False
 with tempfile.TemporaryDirectory(prefix='payroll-novelties-pg-') as private:
  directory=Path(private);directory.chmod(0o700);config=directory/'postgres.env';config.write_text('POSTGRES_USER=fixture_owner\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB='+database+'\n');config.chmod(0o600)
  try:
   docker('run','--pull=never','--rm','-d','--name',name,'--tmpfs','/var/lib/postgresql/data:rw,size=268435456','-p','127.0.0.1::5432','--env-file',str(config),'postgres:16-alpine');started=True;deadline=time.monotonic()+45
   while True:
    try:docker('exec',name,'pg_isready','-h','127.0.0.1','-U','fixture_owner','-d',database);break
    except subprocess.CalledProcessError:
     if time.monotonic()>deadline:raise RuntimeError('Disposable PostgreSQL readiness timeout')
     time.sleep(.2)
   port=int(docker('port',name,'5432/tcp').rsplit(':',1)[1]);child={**env,'PAYROLL_NOVELTIES_TEST_URL':'postgresql://fixture_owner:'+password+'@127.0.0.1:'+str(port)+'/'+database,'PYTHONDONTWRITEBYTECODE':'1','PAYROLL_SOURCE_EARNINGS_FIXTURE':'1' if args.with_source_earnings else '0','NATIVE_PAYROLL_SOURCE_TEST':'1' if args.native_intake else '0','NATIVE_PAYROLL_CORRECTION_TEST':'1' if args.native_correction else '0'}
   completed=subprocess.run([sys.executable,__file__,'--worker'],env=child,capture_output=True,text=True,timeout=90)
   if completed.returncode:
    fd,path=tempfile.mkstemp(prefix='payroll-novelties-pg-error-');os.close(fd);Path(path).write_text(completed.stderr);raise RuntimeError('PostgreSQL payroll fixture failed; private diagnostic '+path)
   print(completed.stdout.splitlines()[-1])
  finally:
   if started:docker('stop','--time','2',name)
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:run()
