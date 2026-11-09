"""PostgreSQL guard patch: resolve parent in the triggering table's schema."""

def install(connection):
    if connection.vendor=='sqlite':return
    if connection.vendor!='postgresql':raise RuntimeError('Unsupported accounting guard backend.')
    with connection.cursor() as cursor:
        cursor.execute('''CREATE OR REPLACE FUNCTION core_accounting_line_guard_v1() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE parent_posted boolean; parent_id uuid;
        BEGIN
          IF TG_OP='UPDATE' AND OLD.journal_entry_id IS DISTINCT FROM NEW.journal_entry_id THEN
            RAISE EXCEPTION 'ACCOUNTING_LINE_REASSIGNMENT_DENIED';
          END IF;
          IF TG_OP='DELETE' THEN parent_id=OLD.journal_entry_id; ELSE parent_id=NEW.journal_entry_id; END IF;
          EXECUTE pg_catalog.format('SELECT is_posted FROM %I.%I WHERE id=$1 FOR UPDATE',TG_TABLE_SCHEMA,'core_erp_journalentry')
            INTO parent_posted USING parent_id;
          IF parent_posted THEN RAISE EXCEPTION 'ACCOUNTING_POSTED_LINE_IMMUTABLE'; END IF;
          IF TG_OP='DELETE' THEN RETURN OLD; END IF; RETURN NEW;
        END $$''')
