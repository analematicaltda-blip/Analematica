"""Isolated real PostgreSQL ledger races; run only via the marked MFA fixture."""
import json,os,subprocess,sys,tempfile,uuid
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
ROOT=Path(__file__).resolve().parents[3]

def worker():
    from datetime import date,timedelta
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from decimal import Decimal
    from unittest.mock import patch
    sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
    from init_local import initialize
    with tempfile.TemporaryDirectory(prefix='ledger-pg-keys-') as private:
        initialize(private)
        config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
        config['DATABASE_URL']=os.environ['LEDGER_TEST_DATABASE_URL']
        os.environ.update(config,BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',PGOPTIONS='-c statement_timeout=15000 -c lock_timeout=10000')
        import django;django.setup()
        from django.db import connection,connections
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from apps.core_erp.tenancy.models import Tenant
        from apps.core_erp.accounting.models import ChartOfAccounts,Account,FiscalPeriod,JournalEntry,LedgerEntry,AccountingAuditLog,AccountingEventReceipt
        from apps.core_erp.accounting.ledger_engine import LedgerEngine
        from apps.core_erp.accounting.journal_service import JournalService
        from apps.core_erp.accounting.exceptions import AccountingError
        from apps.core_erp.outbox_models import OutboxEvent
        from apps.core_erp.accounting import delivery
        from apps.core_erp.accounting.delivery_models import AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance
        from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
        from apps.core_erp.accounting import ratios
        from apps.core_erp.fx.models import Currency,FXRateTable
        assert connection.vendor=='postgresql'
        created=set();visiting=set()
        with connection.schema_editor() as editor:
            def create(model):
                model=model._meta.concrete_model
                if model in created or model in visiting:return
                visiting.add(model)
                for field in model._meta.local_fields:
                    if field.is_relation and field.remote_field and field.remote_field.model is not model:create(field.remote_field.model)
                for field in model._meta.local_many_to_many:create(field.remote_field.model)
                editor.create_model(model);created.add(model);visiting.remove(model)
            for model in (AccountingEventReceipt,AccountingAuditLog,LedgerEntry,OutboxEvent,AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance,AccountingRatioPolicy,Currency,FXRateTable):create(model)
        user=get_user_model()(username='ledger-pg-fixture',role='BUSINESS_OWNER');get_user_model().objects.bulk_create([user])
        results=[]
        for scenario in ['same_event','changed_payload','disjoint_accounts','duplicate_reversal','post_vs_edit','close_vs_post']:
            tenant=Tenant.objects.create(name='Synthetic ledger company',tax_id=uuid.uuid4().hex,state='ACTIVE')
            chart=ChartOfAccounts.plain_objects.create(tenant=tenant,name='Synthetic chart')
            accounts=[Account.plain_objects.create(tenant=tenant,chart_of_accounts=chart,code=str(1100+i),name='Fixture account',type='ASSET') for i in range(4)]
            period=FiscalPeriod.plain_objects.create(tenant=tenant,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open')
            def lines(offset=0):return [{'account':accounts[offset],'debit':'10.00'},{'account':accounts[offset+1],'credit':'10.00'}]
            def draft(offset=0):return JournalService.create_entry(str(tenant.pk),timezone.localdate(),'Fixture journal',lines(offset),created_by=user)
            entries=[]
            if scenario=='disjoint_accounts':entries=[draft(),draft(2)]
            elif scenario in {'duplicate_reversal','post_vs_edit','close_vs_post'}:entries=[draft()]
            if scenario=='duplicate_reversal':LedgerEngine.post_entry(entries[0].pk,tenant_id=tenant.pk,actor=user)
            line_id=LedgerEntry.plain_objects.filter(journal_entry=entries[0]).first().pk if entries else None
            connections.close_all();barrier=Barrier(2)
            def attempt(index):
                try:
                    barrier.wait(timeout=10)
                    if scenario in {'same_event','changed_payload'}:
                        result=LedgerEngine.post_lines(tenant_id=tenant.pk,entry_date=timezone.localdate(),description='Changed' if scenario=='changed_payload' and index else 'Fixture',lines_data=lines(),actor=user,idempotency_key='event-fixture')
                    elif scenario=='disjoint_accounts':result=LedgerEngine.post_entry(entries[index].pk,tenant_id=tenant.pk,actor=user)
                    elif scenario=='duplicate_reversal':result=LedgerEngine.reverse_entry(entries[0].pk,tenant_id=tenant.pk,actor=user)
                    elif scenario=='post_vs_edit' and index:
                        row=LedgerEntry.plain_objects.get(pk=line_id);row.description='Concurrent edit';row.save();return {'accepted':True,'kind':'edit'}
                    elif scenario=='close_vs_post' and index:
                        row=FiscalPeriod.plain_objects.get(pk=period.pk);row.status='closed';row.save();return {'accepted':True,'kind':'close'}
                    else:result=LedgerEngine.post_entry(entries[0].pk,tenant_id=tenant.pk,actor=user)
                    return {'accepted':True,'id':str(result.pk)}
                except (AccountingError,PermissionError):return {'accepted':False}
                finally:connections.close_all()
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(attempt,index) for index in (0,1)];outcomes=[f.result(timeout=25) for f in futures]
            accepted=sum(row['accepted'] for row in outcomes)
            posted=JournalEntry.plain_objects.filter(tenant=tenant,is_posted=True).count()
            receipt_count=AccountingEventReceipt.objects.filter(tenant=tenant).count()
            if scenario=='same_event':assert accepted==2 and posted==1 and receipt_count==1 and len({r['id'] for r in outcomes})==1
            elif scenario=='changed_payload':assert accepted==1 and posted==1 and receipt_count==1
            elif scenario=='disjoint_accounts':assert accepted==2 and posted==2
            elif scenario=='duplicate_reversal':assert accepted==1 and posted==2
            elif scenario=='post_vs_edit':assert posted==1
            elif scenario=='close_vs_post':assert posted in {0,1} and FiscalPeriod.plain_objects.get(pk=period.pk).status=='closed'
            assert LedgerEngine.validate_ledger_integrity(tenant.pk)['is_valid']
            assert OutboxEvent.objects.filter(payload__tenant_id=str(tenant.pk)).count()==posted
            results.append({'scenario':scenario,'accepted':accepted,'posted_journals':posted,'outbox_count':posted,'chain_valid':True})
        os.environ['ACCOUNTING_LOCAL_PROJECTION_ENABLED']='1'
        for scenario in ['delivery_claim','delivery_duplicate','delivery_parallel_events','delivery_stale_lease','delivery_receipt_replay','delivery_rollback']:
            tenant=Tenant.objects.create(name='Synthetic projector company',tax_id=uuid.uuid4().hex,state='ACTIVE')
            chart=ChartOfAccounts.plain_objects.create(tenant=tenant,name='Projection chart')
            a=Account.plain_objects.create(tenant=tenant,chart_of_accounts=chart,code='1105',name='Cash',type='ASSET')
            b=Account.plain_objects.create(tenant=tenant,chart_of_accounts=chart,code='4105',name='Income',type='REVENUE')
            FiscalPeriod.plain_objects.create(tenant=tenant,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open')
            for index in range(2 if scenario=='delivery_parallel_events' else 1):
                LedgerEngine.post_lines(tenant_id=tenant.pk,entry_date=timezone.localdate(),description='Projection contract',lines_data=[{'account':a,'debit':'10.00'},{'account':b,'credit':'10.00'}],actor=user,idempotency_key='projection-'+str(index))
            delivery.enqueue(tenant.pk)
            leases=[]
            if scenario!='delivery_claim':leases=[delivery.claim(tenant.pk)]
            if scenario=='delivery_parallel_events':leases.append(delivery.claim(tenant.pk))
            if scenario=='delivery_stale_lease':
                AccountingDelivery.objects.filter(pk=leases[0]['id']).update(lease_until=timezone.now()-timedelta(seconds=1))
                leases.append(delivery.claim(tenant.pk))
            if scenario=='delivery_receipt_replay':
                delivery.consume(tenant.pk,leases[0]['id'],leases[0]['token'])
                AccountingDelivery.objects.filter(pk=leases[0]['id']).update(status='RETRY',next_attempt_at=timezone.now())
                lease=delivery.claim(tenant.pk);result=delivery.consume(tenant.pk,lease['id'],lease['token']);assert result['applied'] is False
            elif scenario=='delivery_rollback':
                with patch.object(AccountingProjectionReceipt.objects,'create',side_effect=OSError('Synthetic failure')):
                    try:delivery.consume(tenant.pk,leases[0]['id'],leases[0]['token'])
                    except OSError:pass
                    else:raise AssertionError('Expected transaction failure')
                assert not AccountingDailyBalance.objects.filter(tenant=tenant).exists()
                assert not AccountingProjectionReceipt.objects.filter(tenant=tenant).exists()
                delivery.consume(tenant.pk,leases[0]['id'],leases[0]['token'])
            else:
                connections.close_all();barrier=Barrier(2)
                def consume_attempt(index):
                    try:
                        barrier.wait(timeout=10)
                        if scenario=='delivery_claim':return delivery.claim(tenant.pk) is not None
                        lease=leases[index] if scenario in {'delivery_parallel_events','delivery_stale_lease'} else leases[0]
                        delivery.consume(tenant.pk,lease['id'],lease['token']);return True
                    except delivery.LeaseLost:return False
                    finally:connections.close_all()
                with ThreadPoolExecutor(max_workers=2) as pool:
                    fs=[pool.submit(consume_attempt,index) for index in (0,1)];accepted=sum(f.result(timeout=25) for f in fs)
                assert accepted==(2 if scenario=='delivery_parallel_events' else 1)
            expected=0 if scenario=='delivery_claim' else 2 if scenario=='delivery_parallel_events' else 1
            receipts=AccountingProjectionReceipt.objects.filter(tenant=tenant).count();assert receipts==expected
            if expected:assert AccountingDailyBalance.objects.get(tenant=tenant,account=a).debit==Decimal('10')*expected
            assert not OutboxEvent.objects.filter(payload__tenant_id=str(tenant.pk)).exclude(status='PENDING',published_at=None).exists()
            results.append({'scenario':scenario,'projection_receipts':receipts,'duplicate_effect':False,'external_publication_verified':False})
        tenant=Tenant.objects.create(name='Classification race',tax_id=uuid.uuid4().hex,state='ACTIVE')
        chart=ChartOfAccounts.plain_objects.create(tenant=tenant,name='Classification')
        asset=Account.plain_objects.create(tenant=tenant,chart_of_accounts=chart,code='1105',name='Cash',type='ASSET')
        liability=Account.plain_objects.create(tenant=tenant,chart_of_accounts=chart,code='2105',name='Current',type='LIABILITY')
        mapping={'cash_equivalents':[str(asset.pk)],'temporary_investments':[],
                 'immediate_receivables':[],'current_liabilities':[str(liability.pk)]}
        connections.close_all();barrier=Barrier(2)
        def configure_attempt(index):
            try:
                barrier.wait(timeout=10)
                ratios.configure(tenant.pk,actor=user,mapping=mapping,evidence_digest='b'*64,expected_revision=0,confirmed=True)
                return True
            except AccountingError:return False
            finally:connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            fs=[pool.submit(configure_attempt,index) for index in (0,1)]
            accepted=sum(f.result(timeout=25) for f in fs)
        assert accepted==1
        assert AccountingRatioPolicy.objects.filter(tenant=tenant).count()==1
        assert ratios.describe(ratios.latest(tenant.pk))['revision']==1
        results.append({'scenario':'ratio_review_revision_race','accepted':accepted,'stored_revisions':1})
        from apps.core_erp.accounting import sql_guards
        from django.db import transaction,DatabaseError
        import copy
        sql_guards.install(connection)
        from apps.core_erp.accounting.sql_guard_hardening import install as harden_guards
        from apps.core_erp.accounting.sql_guard_health import inspect_guards
        harden_guards(connection)
        assert inspect_guards(connection)['ready']
        FiscalPeriod.plain_objects.create(tenant=tenant,period_start=date(2026,1,1),period_end=date(2026,12,31),status='open')
        protected=LedgerEngine.post_lines(tenant_id=tenant.pk,entry_date=timezone.localdate(),description='Protected fixture',
            lines_data=[{'account':asset,'debit':'10.00'},{'account':liability,'credit':'10.00'}],actor=user,idempotency_key='sql-protected')
        line=LedgerEntry.plain_objects.filter(journal_entry=protected).first()
        def blocked(action):
            try:
                with transaction.atomic():action()
            except DatabaseError as exc:
                assert 'ACCOUNTING_' in str(exc);return
            raise AssertionError('Expected SQL guard rejection')
        blocked(lambda:JournalEntry.plain_objects.filter(pk=protected.pk).update(description='Modified'))
        blocked(lambda:JournalEntry.plain_objects.filter(pk=protected.pk).update(is_posted=False))
        blocked(lambda:JournalEntry.plain_objects.filter(pk=protected.pk)._raw_delete('default'))
        blocked(lambda:LedgerEntry.plain_objects.filter(pk=line.pk).update(debit_amount='99'))
        blocked(lambda:LedgerEntry.plain_objects.filter(pk=line.pk)._raw_delete('default'))
        clone=copy.copy(line);clone.pk=uuid.uuid4();clone._state=copy.copy(line._state);clone._state.adding=True
        blocked(lambda:LedgerEntry.plain_objects.bulk_create([clone]))
        blocked(lambda:AccountingRatioPolicy.objects.filter(tenant=tenant).update(evidence_digest='f'*64))
        blocked(lambda:AccountingRatioPolicy.objects.filter(tenant=tenant)._raw_delete('default'))
        def truncate(table):
            with connection.cursor() as cursor:cursor.execute('TRUNCATE '+connection.ops.quote_name(table)+' CASCADE')
        for table in sql_guards.TABLES.values():blocked(lambda table=table:truncate(table))
        with connection.cursor() as cursor:
            cursor.execute('ALTER TABLE core_erp_ledgerentry DISABLE TRIGGER accounting_row_guard_v1')
        assert 'accounting_sql_guards_disabled' in inspect_guards(connection)['checks']
        with connection.cursor() as cursor:
            cursor.execute('ALTER TABLE core_erp_ledgerentry ENABLE TRIGGER accounting_row_guard_v1')
            cursor.execute('CREATE TEMP TABLE core_erp_journalentry (id uuid PRIMARY KEY,is_posted boolean)')
            cursor.execute('INSERT INTO pg_temp.core_erp_journalentry VALUES (%s,false)',[protected.pk])
        blocked(lambda:LedgerEntry.plain_objects.filter(pk=line.pk).update(debit_amount='99'))
        with connection.cursor() as cursor:cursor.execute('DROP TABLE pg_temp.core_erp_journalentry')
        assert inspect_guards(connection)['ready']
        results.append({'scenario':'guard_health_and_temp_shadowing','disabled_detected':True,'temp_shadow_bypass_blocked':True})
        reversal=LedgerEngine.reverse_entry(protected.pk,'Reviewed correction',tenant_id=tenant.pk,actor=user)
        assert reversal.is_posted and LedgerEngine.validate_ledger_integrity(tenant.pk)['is_valid']
        results.append({'scenario':'posted_sql_guards','blocked_operations':11,'posting_and_reversal_valid':True,'privileged_bypass_protection':False})
        from apps.core_erp.accounting.db_privileges import inspect_privileges
        assert not inspect_privileges(connection)['ready']
        assert 'accounting_db_superuser' in inspect_privileges(connection)['checks']
        usd,_=Currency.objects.get_or_create(code='USD',defaults={'name':'USD fixture','symbol':'$'})
        cop,_=Currency.objects.get_or_create(code='COP',defaults={'name':'COP fixture','symbol':'$'})
        FXRateTable.objects.create(base_currency=usd,target_currency=cop,rate=Decimal('4000'),effective_from=timezone.now()-timedelta(days=3),version=1)
        FXRateTable.objects.create(base_currency=usd,target_currency=cop,rate=Decimal('4500'),effective_from=timezone.now(),version=2)
        foreign_draft=JournalService.create_entry(str(tenant.pk),timezone.localdate()-timedelta(days=2),'Foreign race fixture',
            [{'account':asset,'debit':'10.00'},{'account':liability,'credit':'10.00'}],created_by=user,currency='USD',base_currency='COP')
        foreign_posted=LedgerEngine.post_entry(foreign_draft.pk,tenant_id=tenant.pk,actor=user)
        assert foreign_posted.exchange_rate==Decimal('4000')
        connections.close_all();barrier=Barrier(2)
        def reverse_foreign(index):
            try:
                barrier.wait(timeout=10)
                reversed_entry=LedgerEngine.reverse_entry(foreign_posted.pk,'Reviewed foreign correction',tenant_id=tenant.pk,actor=user)
                assert reversed_entry.exchange_rate==Decimal('4000');return True
            except AccountingError:return False
            finally:connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            fs=[pool.submit(reverse_foreign,index) for index in (0,1)]
            assert sum(f.result(timeout=25) for f in fs)==1
        assert JournalEntry.plain_objects.filter(tenant=tenant,reversed_entry_id=foreign_posted.pk,is_posted=True).count()==1
        assert LedgerEngine.validate_ledger_integrity(tenant.pk)['is_valid']
        results.append({'scenario':'foreign_neutral_reversal_race','single_reversal':True,'historical_rate_preserved':True})
        runtime_role='ledger_runtime_'+uuid.uuid4().hex;runtime_password=uuid.uuid4().hex
        role_q=connection.ops.quote_name(runtime_role);database_q=connection.ops.quote_name(connection.settings_dict['NAME'])
        runtime_connection=None
        try:
            with connection.cursor() as cursor:
                cursor.execute('CREATE ROLE '+role_q+' LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD %s',[runtime_password])
                cursor.execute('REVOKE TEMPORARY ON DATABASE '+database_q+' FROM PUBLIC')
                cursor.execute('GRANT CONNECT ON DATABASE '+database_q+' TO '+role_q)
                cursor.execute('GRANT USAGE ON SCHEMA public TO '+role_q)
                cursor.execute('GRANT SELECT,INSERT,UPDATE ON core_erp_journalentry,core_erp_ledgerentry TO '+role_q)
                cursor.execute('GRANT SELECT,INSERT ON core_erp_accountingratiopolicy TO '+role_q)
            runtime_connection=connection.copy(alias='accounting_runtime_probe')
            runtime_connection.settings_dict.update(USER=runtime_role,PASSWORD=runtime_password)
            assert inspect_privileges(runtime_connection)['ready']
            from apps.core_erp.accounting.runtime_profile import describe_profile
            profile=describe_profile()
            with connection.cursor() as cursor:
                for item in profile['tables']:
                    table=connection.ops.quote_name(item['table'])
                    cursor.execute('GRANT '+','.join(item['privileges'])+' ON '+table+' TO '+role_q)
                    if item['update_columns']:
                        columns=','.join(connection.ops.quote_name(col) for col in item['update_columns'])
                        cursor.execute('GRANT UPDATE ('+columns+') ON '+table+' TO '+role_q)
            parsed_runtime=urlsplit(os.environ['LEDGER_TEST_DATABASE_URL'])
            from urllib.parse import quote
            netloc=quote(runtime_role,safe='')+':'+quote(runtime_password,safe='')+'@'+parsed_runtime.netloc.rsplit('@',1)[1]
            runtime_url=urlunsplit((parsed_runtime.scheme,netloc,parsed_runtime.path,parsed_runtime.query,parsed_runtime.fragment))
            payload={'tenant_id':str(tenant.pk),'user_id':user.pk,'asset_id':str(asset.pk),'liability_id':str(liability.pk)}
            child=subprocess.run([sys.executable,__file__,'--runtime-worker'],env={**os.environ,'LEDGER_TEST_DATABASE_URL':runtime_url,'LEDGER_RUNTIME_CASE':json.dumps(payload)},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
            if child.returncode:
                fd,filename=tempfile.mkstemp(prefix='ledger-runtime-error-');os.close(fd);Path(filename).write_text(child.stderr)
                raise RuntimeError('Restricted accounting runtime failed; private diagnostic '+filename)
            runtime_result=json.loads(child.stdout.splitlines()[-1])
            assert runtime_result['posting_replay_reversal_reports_projection_valid']
            from customer_byos_contract import run_customer_contract
            customer_result=run_customer_contract(connection,runtime_role,runtime_password,tenant.pk,os.environ['LEDGER_TEST_CUSTOMER_DATABASE'])
            results.append({'scenario':'customer_postgres_byos',**customer_result})
            results.extend(customer_result['package_versions']['scenarios'])
            results.append({'scenario':'restricted_accounting_runtime',**runtime_result})
            try:
                with runtime_connection.cursor() as cursor:cursor.execute('ALTER TABLE core_erp_ledgerentry DISABLE TRIGGER accounting_row_guard_v1')
            except DatabaseError as exc:assert getattr(exc.__cause__,'pgcode',None)=='42501'
            else:raise AssertionError('Runtime role must not disable accounting guards.')
            with connection.cursor() as cursor:cursor.execute('SET ROLE '+role_q)
            try:assert 'accounting_db_superuser' in inspect_privileges(connection)['checks']
            finally:
                with connection.cursor() as cursor:cursor.execute('RESET ROLE')
            results.append({'scenario':'accounting_privilege_boundary','admin_rejected':True,'separate_runtime_qualified_for_guarded_tables':True,'disable_trigger_denied':True,'session_admin_cannot_hide_behind_set_role':True})
        finally:
            if runtime_connection is not None:runtime_connection.close()
            with connection.cursor() as cursor:
                cursor.execute('GRANT TEMPORARY ON DATABASE '+database_q+' TO PUBLIC')
                cursor.execute('DROP OWNED BY '+role_q)
                cursor.execute('DROP ROLE '+role_q)
        from invoice_queue_postgres import run_invoice_queue_races
        results.extend(run_invoice_queue_races(user))
        from reservation_source_postgres import run_reservation_source_races
        results.extend(run_reservation_source_races(user))
        from accounting_restore_contract import inspect_restored
        restore_expectation=inspect_restored(connection)
        connections.close_all()
        print(json.dumps({'postgresql':True,'scope':'Separate temporary database; real Django transactions and row locks','results':results,'restore_expectation':restore_expectation}))

def restored_worker():
    sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
    from init_local import initialize
    with tempfile.TemporaryDirectory(prefix='ledger-restore-keys-') as private:
        initialize(private)
        config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
        config['DATABASE_URL']=os.environ['LEDGER_TEST_DATABASE_URL']
        os.environ.update(config,BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1')
        import django;django.setup()
        from django.db import connection
        from accounting_restore_contract import inspect_restored
        print(json.dumps(inspect_restored(connection)))


def runtime_worker():
    sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
    from init_local import initialize
    with tempfile.TemporaryDirectory(prefix='ledger-runtime-keys-') as private:
        initialize(private)
        config=dict(line.split('=',1) for line in (Path(private)/'erp-tur.env').read_text().splitlines() if '=' in line)
        config['DATABASE_URL']=os.environ['LEDGER_TEST_DATABASE_URL']
        os.environ.update(config,BACKEND_SERVICE='erp-tur',DJANGO_SETTINGS_MODULE='tourism_settings',PYTHON_DOTENV_DISABLED='1',ACCOUNTING_LOCAL_PROJECTION_ENABLED='1')
        import django;django.setup()
        from django.contrib.auth import get_user_model
        from django.db import connection,transaction,DatabaseError
        from django.utils import timezone
        from apps.core_erp.accounting.db_privileges import inspect_privileges
        from apps.core_erp.accounting.ledger_engine import LedgerEngine
        from apps.core_erp.accounting.reports_engine import ReportsEngine
        from apps.core_erp.accounting import delivery
        from apps.core_erp.accounting.models import Account
        case=json.loads(os.environ['LEDGER_RUNTIME_CASE']);assert inspect_privileges(connection)['ready']
        actor=get_user_model().objects.get(pk=case['user_id'])
        asset=Account.plain_objects.get(pk=case['asset_id']);liability=Account.plain_objects.get(pk=case['liability_id'])
        args={'tenant_id':case['tenant_id'],'entry_date':timezone.localdate(),'description':'Restricted runtime fixture',
              'lines_data':[{'account':asset,'debit':'50.00'},{'account':liability,'credit':'50.00'}],
              'actor':actor,'idempotency_key':'restricted-runtime-fixture'}
        entry=LedgerEngine.post_lines(**args);assert LedgerEngine.post_lines(**args).pk==entry.pk
        assert LedgerEngine.reverse_entry(entry.pk,'Reviewed restricted correction',tenant_id=case['tenant_id'],actor=actor).is_posted
        from apps.core_erp.accounting.journal_service import JournalService
        from decimal import Decimal
        from datetime import timedelta
        foreign_draft=JournalService.create_entry(case['tenant_id'],timezone.localdate()-timedelta(days=2),'Restricted USD fixture',
            [{'account':asset,'debit':'10.00'},{'account':liability,'credit':'10.00'}],created_by=actor,currency='USD',base_currency='COP')
        foreign=LedgerEngine.post_entry(foreign_draft.pk,tenant_id=case['tenant_id'],actor=actor)
        assert foreign.exchange_rate==Decimal('4000')
        neutral=LedgerEngine.reverse_entry(foreign.pk,'Restricted neutral correction',tenant_id=case['tenant_id'],actor=actor)
        assert neutral.exchange_rate==Decimal('4000')
        report=ReportsEngine.get_trial_balance(case['tenant_id'],timezone.localdate())
        assert report['total_debit']==report['total_credit']
        delivery.run_batch(case['tenant_id'],100);assert delivery.status(case['tenant_id'])['complete']
        assert LedgerEngine.validate_ledger_integrity(case['tenant_id'])['is_valid']
        from apps.core_erp.accounting.reconciliation import inspect_company
        diagnostic=inspect_company(case['tenant_id'],limit=50)
        assert diagnostic['read_only'] and not diagnostic['repairs_executed']
        assert diagnostic['entries'] and all(not row['findings'] for row in diagnostic['entries'])
        denied=0
        for table,column,value in [('core_erp_tenant','name','Forbidden rename'),('core_erp_account','type','REVENUE')]:
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:cursor.execute('UPDATE '+connection.ops.quote_name(table)+' SET '+connection.ops.quote_name(column)+'=%s',[value])
            except DatabaseError as exc:assert getattr(exc.__cause__,'pgcode',None)=='42501';denied+=1
            else:raise AssertionError('Lock-only grants must not permit metadata rewrites.')
        print(json.dumps({'posting_replay_reversal_reports_projection_valid':True,'metadata_rewrites_denied':denied,'foreign_neutral_reversal_valid':True,'reconciliation_diagnostic_valid':True,'database_admin':False,'scope':'Core flow fixture; not all ERP paths or production roles'}))


def run():
    if os.environ.get('MFA_PG_FIXTURE')!='1':raise RuntimeError('Isolated PG fixture required')
    parsed=urlsplit(os.environ['MFA_TEST_DATABASE_URL']);container=os.environ['MFA_TEST_CONTAINER']
    if parsed.hostname!='127.0.0.1' or parsed.path!='/mfa_fixture':raise RuntimeError('Private source required')
    name='ledger_'+uuid.uuid4().hex;restored_name='ledger_restore_'+uuid.uuid4().hex;customer_name='customer_vault_'+uuid.uuid4().hex;created=False;restored_created=False;customer_created=False
    env={key:value for key,value in os.environ.items() if key not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
    def docker(*args):subprocess.run(['docker','--host=unix:///var/run/docker.sock',*args],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=15)
    diagnostic_dir=tempfile.mkdtemp(prefix='ledger-recovery-meta-');env['LEDGER_RESTORE_DEBUG_DIR']=diagnostic_dir
    try:
        docker('exec',container,'createdb','-U','mfa_fixture',name);created=True
        docker('exec',container,'createdb','-U','mfa_fixture',customer_name);customer_created=True
        env['LEDGER_TEST_CUSTOMER_DATABASE']=customer_name
        env['LEDGER_TEST_DATABASE_URL']=urlunsplit(('postgresql',parsed.netloc,'/'+name,parsed.query,parsed.fragment))
        result=subprocess.run([sys.executable,__file__,'--worker'],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
        if result.returncode:
            fd,filename=tempfile.mkstemp(prefix='ledger-pg-error-');os.close(fd);Path(filename).write_text(result.stderr)
            raise RuntimeError('Ledger PostgreSQL contract failed; private diagnostic '+filename)
        report=json.loads(result.stdout.splitlines()[-1])
        with tempfile.TemporaryDirectory(prefix='ledger-backup-') as private:
            archive=Path(private)/'ledger.dump'
            with open(archive,'xb',opener=lambda file,flags:os.open(file,flags,0o600)) as stream:
                subprocess.run(['docker','--host=unix:///var/run/docker.sock','exec',container,'pg_dump','-U','mfa_fixture','-Fc',name],env=env,stdout=stream,stderr=subprocess.PIPE,check=True,timeout=30)
            if archive.stat().st_size>32*1024*1024:raise RuntimeError('Fixture archive exceeds its supported bound.')
            docker('exec',container,'createdb','-U','mfa_fixture',restored_name);restored_created=True
            with archive.open('rb') as stream:
                subprocess.run(['docker','--host=unix:///var/run/docker.sock','exec','-i',container,'pg_restore','--exit-on-error','--no-owner','--no-acl','-U','mfa_fixture','-d',restored_name],env=env,stdin=stream,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True,timeout=30)
            def verify(database):
                selected={**env,'LEDGER_TEST_DATABASE_URL':urlunsplit(('postgresql',parsed.netloc,'/'+database,parsed.query,parsed.fragment))}
                check=subprocess.run([sys.executable,__file__,'--verify-restored'],env=selected,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
                if check.returncode:
                    fd,filename=tempfile.mkstemp(prefix='ledger-restore-error-');os.close(fd);Path(filename).write_text(check.stderr)
                    raise RuntimeError('Private ledger restore verification failed: '+filename)
                return json.loads(check.stdout.splitlines()[-1])
            restored=verify(restored_name);source_after=verify(name)
            if restored!=report['restore_expectation'] or source_after!=report['restore_expectation']:
                raise AssertionError('Ledger recovery metadata mismatch; private diagnostic '+diagnostic_dir)
            report['restore']={**restored,'source_unchanged':True,'archive_mode_private':archive.stat().st_mode&0o077==0,
                               'external_keys_restored':False,'production_qualified':False}
            report['results'].append({'scenario':'ledger_backup_restore','digest_equal':True,'source_unchanged':True,'guards_and_integrity_valid':True})
        import shutil;shutil.rmtree(diagnostic_dir)
        return report
    finally:
        if customer_created:docker('exec',container,'dropdb','--force','-U','mfa_fixture',customer_name)
        if restored_created:docker('exec',container,'dropdb','--force','-U','mfa_fixture',restored_name)
        if created:docker('exec',container,'dropdb','--force','-U','mfa_fixture',name)

if __name__=='__main__':
    if '--runtime-worker' in sys.argv and os.environ.get('MFA_PG_FIXTURE')=='1':runtime_worker()
    elif '--verify-restored' in sys.argv and os.environ.get('MFA_PG_FIXTURE')=='1':restored_worker()
    elif '--worker' in sys.argv and os.environ.get('MFA_PG_FIXTURE')=='1':worker()
    else:raise SystemExit('Run via mfa_postgres_check.py isolated fixture.')
