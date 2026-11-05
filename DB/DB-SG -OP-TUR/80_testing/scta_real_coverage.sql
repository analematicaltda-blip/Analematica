-- sarita_db/80_testing/scta_real_coverage.sql
-- Auditoría dinámica de cobertura de triggers SCTA

WITH target_tables AS (
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema IN ('core', 'identity', 'governance', 'tourism', 'erp', 'finance')
    AND table_type = 'BASE TABLE'
),
table_triggers AS (
    SELECT
        event_object_schema as schema,
        event_object_table as table,
        trigger_name
    FROM information_schema.triggers
)
SELECT
    tt.table_schema,
    tt.table_name,
    EXISTS (SELECT 1 FROM table_triggers tr WHERE tr.schema = tt.table_schema AND tr.table = tt.table_name AND tr.trigger_name LIKE '%context_guard%') as has_context_guard,
    EXISTS (SELECT 1 FROM table_triggers tr WHERE tr.schema = tt.table_schema AND tr.table = tt.table_name AND tr.trigger_name LIKE '%trace_guard%') as has_trace_guard,
    EXISTS (SELECT 1 FROM table_triggers tr WHERE tr.schema = tt.table_schema AND tr.table = tt.table_name AND tr.trigger_name LIKE '%ai_feed%') as has_ai_feed
FROM target_tables tt
ORDER BY 1, 2;
