-- 90_super_admin/27_sovereign_runtime/05_policy_execution_engine.sql
-- BLOQUE 5 — POLICY EXECUTION ENGINE

-- Real-time policy execution monitoring
CREATE TABLE IF NOT EXISTS infrastructure.active_policy_execution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID NOT NULL,
    target_entity_id UUID,
    status TEXT CHECK (status IN ('ENFORCED', 'VIOLATED', 'BYPASSED', 'CRIPPLED')),
    reaction_taken TEXT, -- e.g., 'FREEZE_TENANT', 'LOG_AUDIT', 'BLOCK_FINANCE'
    execution_latency INTEGER, -- ms
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Adaptive and dynamic sovereign rules
CREATE TABLE IF NOT EXISTS infrastructure.adaptive_sovereign_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL,
    base_logic TEXT,
    dynamic_conditions JSONB,
    current_priority INTEGER,
    is_active BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Policy penalties and automatic sanctions
CREATE TABLE IF NOT EXISTS infrastructure.policy_penalties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    violation_trace_id UUID NOT NULL,
    penalty_type TEXT NOT NULL, -- 'FINANCIAL_TAX', 'QUARANTINE', 'IA_DEGRADATION'
    impact_magnitude DECIMAL(10, 4),
    is_resolved BOOLEAN DEFAULT false,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
