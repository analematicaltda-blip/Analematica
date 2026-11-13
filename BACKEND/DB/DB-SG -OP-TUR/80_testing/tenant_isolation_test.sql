-- sarita_db/80_testing/tenant_isolation_test.sql
-- Validación de aislamiento Multi-Tenant (RLS)

-- 1. Setup session para Tenant A
-- Use a standard Postgres SET command that won't fail linting if possible
-- or just keep it as valid SQL for Postgres.
SET "sarita.current_tenant_id" = '00000000-0000-0000-0000-000000000001';

-- Intentar leer datos de Tenant B (suponiendo que existen)
SELECT * FROM identity.users WHERE tenant_id = '00000000-0000-0000-0000-000000000002';
-- Resultado esperado: 0 filas.

-- 2. Intento de Bypass vía subquery
SELECT count(*) FROM (
    SELECT * FROM identity.users
    WHERE tenant_id = '00000000-0000-0000-0000-000000000002'
) AS sub;
