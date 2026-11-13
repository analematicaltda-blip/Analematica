-- =============================================================================
-- SARITA SOVEREIGN OS - GLOBAL RLS ENFORCEMENT
-- Logic: Mandates tenant-level isolation for all operational domains
-- =============================================================================

-- Ensure RLS is active on Governance
ALTER TABLE IF EXISTS governance.global_tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS governance.global_tenants FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_governance ON governance.global_tenants;
CREATE POLICY tenant_isolation_governance ON governance.global_tenants
    USING (id = security.fn_get_tenant_id());

-- Ensure RLS is active on AI Core
ALTER TABLE IF EXISTS ai_core.agent_hierarchy ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ai_core.agent_hierarchy FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_ai_core ON ai_core.agent_hierarchy;
CREATE POLICY tenant_isolation_ai_core ON ai_core.agent_hierarchy
    USING (tenant_id = security.fn_get_tenant_id());

-- Ensure RLS is active on Global Finance
ALTER TABLE IF EXISTS finance.global_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS finance.global_wallets FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_finance ON finance.global_wallets;
CREATE POLICY tenant_isolation_finance ON finance.global_wallets
    USING (tenant_id = security.fn_get_tenant_id());

-- Note: In production, a dynamic script applies this to ALL tables with a tenant_id column.
-- This file certifies the core RLS bridge using the security nucleus.
