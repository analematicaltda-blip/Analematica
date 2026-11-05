-- REPORTE DE COBERTURA SCTA
SELECT
    event_object_schema as schema,
    event_object_table as tabla,
    trigger_name,
    'infrastructure.fn_scta_validation' as function
FROM information_schema.triggers
WHERE trigger_name = 'trg_scta_enforce'
ORDER BY 1, 2;
