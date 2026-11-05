-- sarita_db/80_testing/global_columns_real_check.sql
-- Validación real de presencia de columnas globales de trazabilidad

SELECT
    table_schema,
    table_name,
    SUM(CASE WHEN column_name = 'tenant_id' THEN 1 ELSE 0 END) as has_tenant_id,
    SUM(CASE WHEN column_name = 'trace_id' THEN 1 ELSE 0 END) as has_trace_id,
    SUM(CASE WHEN column_name = 'context_id' THEN 1 ELSE 0 END) as has_context_id
FROM information_schema.columns
WHERE table_schema IN ('core', 'identity', 'governance', 'tourism', 'erp', 'finance', 'ai_core')
GROUP BY table_schema, table_name
HAVING
    SUM(CASE WHEN column_name = 'tenant_id' THEN 1 ELSE 0 END) = 0 OR
    SUM(CASE WHEN column_name = 'trace_id' THEN 1 ELSE 0 END) = 0 OR
    SUM(CASE WHEN column_name = 'context_id' THEN 1 ELSE 0 END) = 0
ORDER BY 1, 2;
