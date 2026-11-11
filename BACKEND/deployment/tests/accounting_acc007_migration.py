"""Reproducible nonempty migration up/down probe; strictly disposable only."""
from pathlib import Path
import sys,uuid,json,os
import argparse
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'BACKEND/deployment'))
parser=argparse.ArgumentParser(description='ACC007 migration roundtrip on an explicitly disposable fresh SQLite database.')
parser.add_argument('--directory',required=True);args=parser.parse_args()
directory=Path(args.directory).resolve()
if Path('/tmp') not in directory.parents or not directory.name.startswith('acc007-'):raise RuntimeError('Use an explicit acc007- disposable directory under /tmp, never customer data.')
from fresh_local import configure
configure(str(directory),'erp-tur')
import django;django.setup()
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import connection
from apps.core_erp.tenancy.models import Tenant
from apps.core_erp.accounting.models import Account,ChartOfAccounts,FiscalPeriod,JournalEntry,LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.sql_guard_health import inspect_guards
assert inspect_guards(connection)['ready']
u=get_user_model()(username='migration-guard-'+uuid.uuid4().hex,role='BUSINESS_OWNER');get_user_model().objects.bulk_create([u]);t=Tenant.objects.create(name='Disposable migration probe',tax_id=uuid.uuid4().hex,state='ACTIVE');ch=ChartOfAccounts.plain_objects.create(tenant=t,name='Probe');a=Account.plain_objects.create(tenant=t,chart_of_accounts=ch,code='1105',name='Cash',type='ASSET');b=Account.plain_objects.create(tenant=t,chart_of_accounts=ch,code='4105',name='Income',type='REVENUE');d=timezone.localdate();FiscalPeriod.plain_objects.create(tenant=t,period_start=d,period_end=d,status='open')
entry=LedgerEngine.post_lines(tenant_id=t.pk,entry_date=d,description='Preserve existing posted data',lines_data=[{'account':a,'debit':'10.00'},{'account':b,'credit':'10.00'}],actor=u,idempotency_key=uuid.uuid4().hex)
headers=list(JournalEntry.plain_objects.values());lines=list(LedgerEntry.plain_objects.values())
call_command('migrate','core_erp','0007',interactive=False,verbosity=0);assert not inspect_guards(connection)['ready']
call_command('migrate','core_erp','0008',interactive=False,verbosity=0);assert inspect_guards(connection)['ready']
assert headers==list(JournalEntry.plain_objects.values()) and lines==list(LedgerEntry.plain_objects.values())
assert LedgerEngine.validate_ledger_integrity(t.pk)['is_valid']
print(json.dumps({'migration_roundtrip':True,'posted_rows_unchanged':True,'missing_guard_detected_during_explicit_rollback':True,'guards_ready_after_reapply':True,'synthetic_private_sqlite_only':True,'production_ready':False}))
