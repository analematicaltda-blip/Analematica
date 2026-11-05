-- 90_super_admin/27_sovereign_runtime/06_arbitration_engine.sql
-- BLOQUE 6 — ARBITRATION ENGINE

-- Conflict matrix for cross-domain arbitration
CREATE TABLE IF NOT EXISTS infrastructure.conflict_matrix_runtime (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_a TEXT NOT NULL,
    domain_b TEXT NOT NULL,
    default_winner TEXT, -- Priority winner
    override_rules JSONB,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Real-time resource arbitration (AI, Finance, CPU)
CREATE TABLE IF NOT EXISTS infrastructure.resource_arbitration_active (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type TEXT CHECK (resource_type IN ('AI_AGENT_CAPACITY', 'FINANCIAL_LIQUIDITY', 'OPERATIONAL_SLOTS', 'DB_CONNECTIONS')),
    competing_entities UUID[],
    winner_entity_id UUID,
    arbitration_reason TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Override mechanism for emergencies
CREATE TABLE IF NOT EXISTS infrastructure.sovereign_priority_override (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    override_type TEXT NOT NULL, -- 'FINANCIAL_OVERRIDE', 'AI_OVERRIDE'
    target_id UUID,
    new_priority INTEGER,
    authorized_by_rank TEXT,
    expires_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
