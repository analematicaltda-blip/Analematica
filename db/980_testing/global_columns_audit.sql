-- AUDITORÍA DE COLUMNAS DE TRAZABILIDAD (Misión 2)
SELECT
    table_schema,
    table_name,
    SUM(CASE WHEN column_name = 'tenant_id' THEN 1 ELSE 0 END) as has_tenant,
    SUM(CASE WHEN column_name = 'trace_id' THEN 1 ELSE 0 END) as has_trace,
    SUM(CASE WHEN column_name = 'context_id' THEN 1 ELSE 0 END) as has_context
FROM information_schema.columns
WHERE table_schema IN ('identity', 'tourism', 'erp', 'finance', 'ai_core')
GROUP BY table_schema, table_name
HAVING SUM(CASE WHEN column_name = 'tenant_id' THEN 1 ELSE 0 END) = 0
    OR SUM(CASE WHEN column_name = 'trace_id' THEN 1 ELSE 0 END) = 0
    OR SUM(CASE WHEN column_name = 'context_id' THEN 1 ELSE 0 END) = 0;
