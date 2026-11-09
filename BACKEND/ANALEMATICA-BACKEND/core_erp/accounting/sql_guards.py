"""Database immutability guard v1. Does not replace posting authorization or DB roles.

Protects already posted headers/lines and historical ratio policies. A database
owner/superuser able to disable triggers remains outside this protection boundary.
"""
TABLES={'journal':'core_erp_journalentry','line':'core_erp_ledgerentry','policy':'core_erp_accountingratiopolicy'}

def install(connection):
    if connection.vendor not in {'postgresql','sqlite'}:raise RuntimeError('Accounting SQL guards require PostgreSQL or SQLite.')
    q=connection.ops.quote_name
    j,l,p=(q(TABLES[k]) for k in ('journal','line','policy'))
    statements=[]
    if connection.vendor=='postgresql':
        statements=[f'''CREATE OR REPLACE FUNCTION core_accounting_header_guard_v1() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
          IF TG_OP='INSERT' THEN
            IF NEW.is_posted THEN RAISE EXCEPTION 'ACCOUNTING_DRAFT_REQUIRED'; END IF;
          ELSIF OLD.is_posted THEN RAISE EXCEPTION 'ACCOUNTING_POSTED_IMMUTABLE';
          END IF;
          IF TG_OP='DELETE' THEN RETURN OLD; END IF; RETURN NEW;
        END $$''',
        f'''CREATE OR REPLACE FUNCTION core_accounting_line_guard_v1() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE parent_posted boolean;
        BEGIN
          IF TG_OP='UPDATE' AND OLD.journal_entry_id IS DISTINCT FROM NEW.journal_entry_id THEN
            RAISE EXCEPTION 'ACCOUNTING_LINE_REASSIGNMENT_DENIED';
          END IF;
          IF TG_OP='DELETE' THEN
            SELECT is_posted INTO parent_posted FROM {j} WHERE id=OLD.journal_entry_id FOR UPDATE;
          ELSE
            SELECT is_posted INTO parent_posted FROM {j} WHERE id=NEW.journal_entry_id FOR UPDATE;
          END IF;
          IF parent_posted THEN RAISE EXCEPTION 'ACCOUNTING_POSTED_LINE_IMMUTABLE'; END IF;
          IF TG_OP='DELETE' THEN RETURN OLD; END IF; RETURN NEW;
        END $$''',
        '''CREATE OR REPLACE FUNCTION core_accounting_deny_v1() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN RAISE EXCEPTION 'ACCOUNTING_HISTORY_IMMUTABLE'; END $$''']
        for table,function,events in [(j,'core_accounting_header_guard_v1','INSERT OR UPDATE OR DELETE'),(l,'core_accounting_line_guard_v1','INSERT OR UPDATE OR DELETE'),(p,'core_accounting_deny_v1','UPDATE OR DELETE')]:
            statements.extend([f'DROP TRIGGER IF EXISTS accounting_row_guard_v1 ON {table}',f'CREATE TRIGGER accounting_row_guard_v1 BEFORE {events} ON {table} FOR EACH ROW EXECUTE FUNCTION {function}()'])
        for table in (j,l,p):
            statements.extend([f'DROP TRIGGER IF EXISTS accounting_truncate_guard_v1 ON {table}',f'CREATE TRIGGER accounting_truncate_guard_v1 BEFORE TRUNCATE ON {table} FOR EACH STATEMENT EXECUTE FUNCTION core_accounting_deny_v1()'])
    else:
        rules=[('header_insert',j,'INSERT','NEW.is_posted=1'),('header_update',j,'UPDATE','OLD.is_posted=1'),('header_delete',j,'DELETE','OLD.is_posted=1'),
               ('line_insert',l,'INSERT',f'EXISTS(SELECT 1 FROM {j} WHERE id=NEW.journal_entry_id AND is_posted=1)'),
               ('line_update',l,'UPDATE',f'OLD.journal_entry_id IS NOT NEW.journal_entry_id OR EXISTS(SELECT 1 FROM {j} WHERE id=OLD.journal_entry_id AND is_posted=1)'),
               ('line_delete',l,'DELETE',f'EXISTS(SELECT 1 FROM {j} WHERE id=OLD.journal_entry_id AND is_posted=1)'),
               ('policy_update',p,'UPDATE','1=1'),('policy_delete',p,'DELETE','1=1')]
        for name,table,operation,condition in rules:
            statements.append(f"CREATE TRIGGER IF NOT EXISTS accounting_{name}_v1 BEFORE {operation} ON {table} WHEN {condition} BEGIN SELECT RAISE(ABORT,'ACCOUNTING_HISTORY_IMMUTABLE'); END")
    with connection.cursor() as cursor:
        for statement in statements:cursor.execute(statement)


def uninstall(connection):
    q=connection.ops.quote_name
    with connection.cursor() as cursor:
        if connection.vendor=='postgresql':
            for table in TABLES.values():
                for trigger in ('accounting_row_guard_v1','accounting_truncate_guard_v1'):cursor.execute(f'DROP TRIGGER IF EXISTS {trigger} ON {q(table)}')
            for function in ('core_accounting_header_guard_v1','core_accounting_line_guard_v1','core_accounting_deny_v1'):cursor.execute(f'DROP FUNCTION IF EXISTS {function}()')
        elif connection.vendor=='sqlite':
            for name in ('header_insert','header_update','header_delete','line_insert','line_update','line_delete','policy_update','policy_delete'):cursor.execute(f'DROP TRIGGER IF EXISTS accounting_{name}_v1')
        else:raise RuntimeError('Unsupported accounting SQL guard backend.')
