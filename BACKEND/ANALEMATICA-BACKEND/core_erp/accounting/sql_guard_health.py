"""Read-only structural guard checks, not forensic attestation of function bodies."""
from .sql_guards import TABLES


def inspect_guards(connection):
    issues=set()
    with connection.cursor() as cursor:
        if connection.vendor=='sqlite':
            expected={f'accounting_{name}_v1':TABLES[kind] for kind,names in [
                ('journal',('header_insert','header_update','header_delete')),
                ('line',('line_insert','line_update','line_delete')),
                ('policy',('policy_update','policy_delete'))] for name in names}
            cursor.execute("SELECT name,tbl_name,sql FROM sqlite_master WHERE type='trigger'")
            actual={name:(table,sql) for name,table,sql in cursor.fetchall()}
            for name,table in expected.items():
                if name not in actual:issues.add('accounting_sql_guards_missing')
                elif actual[name][0]!=table or not actual[name][1]:issues.add('accounting_sql_guards_invalid')
        elif connection.vendor=='postgresql':
            expected={}
            for kind,function,events in [('journal','core_accounting_header_guard_v1',31),('line','core_accounting_line_guard_v1',31),('policy','core_accounting_deny_v1',27)]:
                expected[(TABLES[kind],'accounting_row_guard_v1')]=(function,events)
                expected[(TABLES[kind],'accounting_truncate_guard_v1')]=('core_accounting_deny_v1',34)
            cursor.execute('''SELECT c.relname,t.tgname,t.tgenabled,t.tgtype,p.proname,t.tgnargs,t.tgqual IS NULL,t.tgattr::text='',p.pronamespace=c.relnamespace
                FROM pg_catalog.pg_trigger t JOIN pg_catalog.pg_class c ON c.oid=t.tgrelid
                JOIN pg_catalog.pg_proc p ON p.oid=t.tgfoid
                WHERE NOT t.tgisinternal AND t.tgrelid IN (pg_catalog.to_regclass(%s),pg_catalog.to_regclass(%s),pg_catalog.to_regclass(%s))''',list(TABLES.values()))
            actual={(table,name):(enabled,events,function,args,no_when,all_columns,same_schema) for table,name,enabled,events,function,args,no_when,all_columns,same_schema in cursor.fetchall()}
            for key,(function,events) in expected.items():
                if key not in actual:issues.add('accounting_sql_guards_missing');continue
                enabled,found_events,found_function,args,no_when,all_columns,same_schema=actual[key]
                if enabled not in {'O','A'}:issues.add('accounting_sql_guards_disabled')
                if (found_events,found_function,args,no_when,all_columns,same_schema)!=(events,function,0,True,True,True):issues.add('accounting_sql_guards_invalid')
        else:issues.add('accounting_sql_guards_unsupported')
    return {'ready':not issues,'checks':sorted(issues),'scope':'structural_presence_and_enabled_state_not_body_attestation'}
