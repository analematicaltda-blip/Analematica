-- VALIDACIÓN MATEMÁTICA DE RELACIONES
SELECT
    'Tablas sin FK' as check_type,
    count(*) as result
FROM information_schema.tables t
LEFT JOIN information_schema.table_constraints tc
    ON t.table_name = tc.table_name
    AND t.table_schema = tc.table_schema
    AND tc.constraint_type = 'FOREIGN KEY'
WHERE t.table_schema IN ('identity', 'tourism', 'erp', 'finance', 'ai_core')
AND tc.constraint_name IS NULL;
