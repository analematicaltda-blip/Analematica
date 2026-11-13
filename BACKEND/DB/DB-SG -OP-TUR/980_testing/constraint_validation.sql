-- VALIDACIÓN DE REGLAS DE NEGOCIO (CONSTRAINTS)
SELECT
    table_name,
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema IN ('finance', 'ledger', 'tourism')
AND constraint_type IN ('UNIQUE', 'CHECK');
