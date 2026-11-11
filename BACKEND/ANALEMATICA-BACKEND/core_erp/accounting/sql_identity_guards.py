"""Protect account identities committed by existing journals, without rehashing.

DDL is migration-only. An owner able to replace triggers remains outside the
runtime DML boundary; readiness checks compare installed bodies with this code.
"""
from django.db import transaction

FUNCTION='core_accounting_account_identity_guard_v1'
TABLE='core_erp_account'
TRIGGER='accounting_account_identity_v1'

def statements(connection):
    q=connection.ops.quote_name;a=q(TABLE);l=q('core_erp_ledgerentry');j=q('core_erp_journalentry')
    fields=('id','tenant_id','code','type','chart_of_accounts_id')
    if connection.vendor=='sqlite':
        changed=' OR '.join('OLD.'+field+' IS NOT NEW.'+field for field in fields)
        used=f'EXISTS(SELECT 1 FROM {l} l JOIN {j} j ON j.id=l.journal_entry_id WHERE l.account_id=OLD.id AND j.is_posted=1)'
        return [f"CREATE TRIGGER {TRIGGER} BEFORE UPDATE ON {a} WHEN ({changed}) AND {used} BEGIN SELECT RAISE(ABORT,'ACCOUNTING_ACCOUNT_IDENTITY_IMMUTABLE'); END",f"CREATE TRIGGER accounting_account_delete_v1 BEFORE DELETE ON {a} WHEN {used} BEGIN SELECT RAISE(ABORT,'ACCOUNTING_ACCOUNT_IDENTITY_IMMUTABLE'); END"]
    if connection.vendor!='postgresql':raise RuntimeError('Accounting identity guards require PostgreSQL or SQLite.')
    changed=' OR '.join('OLD.'+field+' IS DISTINCT FROM NEW.'+field for field in fields)
    return [f'''CREATE OR REPLACE FUNCTION {FUNCTION}() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE used boolean;
    BEGIN
      IF TG_OP='UPDATE' AND NOT ({changed}) THEN RETURN NEW; END IF;
      EXECUTE pg_catalog.format('SELECT EXISTS(SELECT 1 FROM %I.%I l JOIN %I.%I j ON j.id=l.journal_entry_id WHERE l.account_id=$1 AND j.is_posted)',TG_TABLE_SCHEMA,'core_erp_ledgerentry',TG_TABLE_SCHEMA,'core_erp_journalentry') INTO used USING OLD.id;
      IF used THEN RAISE EXCEPTION 'ACCOUNTING_ACCOUNT_IDENTITY_IMMUTABLE'; END IF;
      IF TG_OP='DELETE' THEN RETURN OLD; END IF; RETURN NEW;
    END $$''',f'CREATE TRIGGER {TRIGGER} BEFORE UPDATE OR DELETE ON {a} FOR EACH ROW EXECUTE FUNCTION {FUNCTION}()']

def uninstall(connection):
    with transaction.atomic(using=connection.alias),connection.cursor() as cursor:
        if connection.vendor=='sqlite':
            for name in (TRIGGER,'accounting_account_delete_v1'):cursor.execute('DROP TRIGGER IF EXISTS '+name)
        elif connection.vendor=='postgresql':
            cursor.execute(f'DROP TRIGGER IF EXISTS {TRIGGER} ON {connection.ops.quote_name(TABLE)}')
            cursor.execute(f'DROP FUNCTION IF EXISTS {FUNCTION}()')
        else:raise RuntimeError('Unsupported accounting guard backend.')

def install(connection):
    # Explicit migration/maintenance action; never called by readiness.
    with transaction.atomic(using=connection.alias):
        uninstall(connection)
        with connection.cursor() as cursor:
            for sql in statements(connection):cursor.execute(sql)
