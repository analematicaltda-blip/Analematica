-- 48.1 — IMPLEMENTAR RLS REAL (ANTI-TENANT LEAKAGE)
-- This script activates total isolation with FORCE RLS.

DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema IN ('core', 'identity', 'finance', 'ai_core', 'erp', 'tourism')
        AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY',
            (SELECT table_schema FROM information_schema.tables WHERE table_name = t LIMIT 1), t);
        EXECUTE format('ALTER TABLE %I.%I FORCE ROW LEVEL SECURITY',
            (SELECT table_schema FROM information_schema.tables WHERE table_name = t LIMIT 1), t);
    END LOOP;
END $$;

-- Base Isolation Policy for all critical domains
-- Requirements: tenant_id, trace_id, actor_id
CREATE OR REPLACE FUNCTION security.fn_get_current_tenant() RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_tenant_id')::UUID;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply actual policies (using example for finance)
DROP POLICY IF EXISTS finance_tenant_isolation ON finance.sovereign_ledger_global;
CREATE POLICY finance_tenant_isolation ON finance.sovereign_ledger_global
    USING (tenant_id = security.fn_get_current_tenant())
    WITH CHECK (tenant_id = security.fn_get_current_tenant());

-- Forensic audit of RLS violations (Conceptual SQL Trigger)
-- In a real scenario, we'd log unauthorized attempts here.
