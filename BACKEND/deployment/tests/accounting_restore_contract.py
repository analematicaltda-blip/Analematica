"""Read-only fixture fingerprints and functional checks, never a production restore tool."""
import hashlib,json,os,uuid,re
from pathlib import Path

def normalize_constraints(rows):
    result=[];statuses={'PENDING','LEASED','RETRY','DELIVERED','QUARANTINED'}
    for row in rows:
        values=list(row)
        if values[0:2]==['core_erp_accountingdelivery','accounting_delivery_valid_status']:
            expression=values[-1]
            match=re.fullmatch(r"CHECK \(status::text = ANY \(ARRAY\[(.*?)\](::text\[\])?\)\)",expression)
            if not match:raise AssertionError('Unexpected status constraint expression; do not discard DDL differences.')
            labels=[]
            for term in match[1].split(', '):
                item=re.fullmatch(r"'([A-Z]+)'::character varying(::text)?",term)
                if not item or bool(item[2])==bool(match[2]):raise AssertionError('Unsupported array cast transformation.')
                labels.append(item[1])
            assert len(labels)==len(statuses) and set(labels)==statuses
            values[-1]='CHECK_STATUS_SET:'+','.join(sorted(labels))
        result.append(values)
    return result


def inspect_restored(connection):
    from django.db import DatabaseError,transaction
    from apps.core_erp.accounting.models import JournalEntry
    from apps.core_erp.accounting.ledger_engine import LedgerEngine
    from apps.core_erp.accounting.sql_guard_health import inspect_guards
    q=connection.ops.quote_name;tables={};sequences={}
    with connection.cursor() as cursor:
        for table in sorted(connection.introspection.table_names(cursor)):
            cursor.execute('SELECT pg_catalog.row_to_json(t)::text FROM '+q(table)+' t')
            rows=sorted(row[0] for row in cursor.fetchall())
            tables[table]={'rows':len(rows),'digest':hashlib.sha256('\n'.join(rows).encode()).hexdigest()}
        cursor.execute("SELECT n.nspname,c.relname FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='S' AND n.nspname=current_schema() ORDER BY c.relname")
        for schema,name in cursor.fetchall():
            cursor.execute('SELECT last_value,is_called FROM '+q(schema)+'.'+q(name))
            sequences[name]=list(cursor.fetchone())
        cursor.execute('''SELECT pg_catalog.pg_get_functiondef(p.oid) FROM pg_catalog.pg_proc p
            JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace
            WHERE n.nspname=current_schema() AND p.proname LIKE 'core_accounting_%' ORDER BY p.proname''')
        functions=[row[0] for row in cursor.fetchall()]
        cursor.execute('''SELECT c.relname,t.tgname,t.tgenabled,pg_catalog.pg_get_triggerdef(t.oid)
            FROM pg_catalog.pg_trigger t JOIN pg_catalog.pg_class c ON c.oid=t.tgrelid
            JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname=current_schema() AND NOT t.tgisinternal ORDER BY c.relname,t.tgname''')
        triggers=cursor.fetchall()
        cursor.execute("""SELECT c.relname,a.attname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity,a.attgenerated,pg_catalog.pg_get_expr(d.adbin,d.adrelid)
            FROM pg_catalog.pg_attribute a JOIN pg_catalog.pg_class c ON c.oid=a.attrelid
            JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
            LEFT JOIN pg_catalog.pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum
            WHERE n.nspname=current_schema() AND c.relkind='r' AND a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum""")
        columns=cursor.fetchall()
        cursor.execute("""SELECT rel.relname,c.conname,c.contype,c.convalidated,c.condeferrable,c.condeferred,pg_catalog.pg_get_constraintdef(c.oid,true)
            FROM pg_catalog.pg_constraint c JOIN pg_catalog.pg_class rel ON rel.oid=c.conrelid
            JOIN pg_catalog.pg_namespace n ON n.oid=rel.relnamespace
            WHERE n.nspname=current_schema() ORDER BY rel.relname,c.conname""")
        constraints=normalize_constraints(cursor.fetchall())
        cursor.execute("""SELECT t.relname,i.relname,pg_catalog.pg_get_indexdef(i.oid)
            FROM pg_catalog.pg_index x JOIN pg_catalog.pg_class t ON t.oid=x.indrelid
            JOIN pg_catalog.pg_class i ON i.oid=x.indexrelid JOIN pg_catalog.pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname=current_schema() ORDER BY t.relname,i.relname""")
        indexes=cursor.fetchall()
    manifest={'tables':tables,'sequences':sequences,'functions':functions,'triggers':triggers,
              'columns':columns,'constraints':constraints,'indexes':indexes}
    diagnostic=os.environ.get('LEDGER_RESTORE_DEBUG_DIR')
    if diagnostic:
        destination=Path(diagnostic)/(uuid.uuid4().hex+'.json')
        with open(destination,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:
            json.dump({'database':connection.settings_dict['NAME'],'manifest':manifest},stream,sort_keys=True,indent=2)
    components={key:hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest() for key,value in manifest.items()}
    digest=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    companies=list(JournalEntry.plain_objects.filter(is_posted=True).values_list('tenant_id',flat=True).distinct())
    if not companies:raise AssertionError('A nonempty posted ledger is required for the recovery contract.')
    for company_id in companies:
        assert LedgerEngine.validate_ledger_integrity(company_id)['is_valid']
    assert inspect_guards(connection)['ready']
    from apps.core_erp.accounting.delivery_models import AccountingDelivery
    job=AccountingDelivery.objects.first()
    assert job is not None
    for status in ['PENDING','LEASED','RETRY','DELIVERED','QUARANTINED']:
        with transaction.atomic():
            assert AccountingDelivery.objects.filter(pk=job.pk).update(status=status)==1
            transaction.set_rollback(True)
    try:
        with transaction.atomic():AccountingDelivery.objects.filter(pk=job.pk).update(status='INVALID_PROBE')
    except DatabaseError as exc:
        cause=exc.__cause__
        assert getattr(cause,'pgcode',None)=='23514'
        assert getattr(getattr(cause,'diag',None),'constraint_name',None)=='accounting_delivery_valid_status'
    else:raise AssertionError('Restored status check constraint failed.')
    entry=JournalEntry.plain_objects.filter(is_posted=True).first()
    try:
        with transaction.atomic():JournalEntry.plain_objects.filter(pk=entry.pk).update(description='Restore guard probe')
    except DatabaseError as exc:assert 'ACCOUNTING_' in str(exc)
    else:raise AssertionError('Restored posted-header guard did not reject mutation.')
    return {'digest':digest,'component_digests':components,'table_count':len(tables),'total_rows':sum(row['rows'] for row in tables.values()),
            'posted_companies_verified':len(companies),'sequence_count':len(sequences),
            'accounting_functions':len(functions),'guard_triggers':len(triggers),
            'columns':len(columns),'constraints':len(constraints),'indexes':len(indexes),
            'ledger_integrity_valid':True,'guards_ready':True,'mutation_blocked':True,'status_constraint_behavior_verified':True,'constraint_normalization':'status_text_array_cast_v1'}
