-- 30_triggers/z_scta_coverage_auto.sql
-- COBERTURA AUTOMÁTICA SCTA PARA TODA LA DB

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN ('identity', 'tourism', 'erp', 'finance')
        AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trg_scta_enforce ON %I.%I', r.table_schema, r.table_name);
        EXECUTE format('CREATE TRIGGER trg_scta_enforce BEFORE INSERT OR UPDATE ON %I.%I FOR EACH ROW EXECUTE FUNCTION infrastructure.fn_scta_validation()', r.table_schema, r.table_name);
    END LOOP;
END $$;
