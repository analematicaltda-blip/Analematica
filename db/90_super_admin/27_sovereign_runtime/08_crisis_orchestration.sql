-- 90_super_admin/27_sovereign_runtime/08_crisis_orchestration.sql
-- BLOQUE 8 — CRISIS ORCHESTRATION

-- Crisis protocols and lockdown sequences
CREATE TABLE IF NOT EXISTS infrastructure.crisis_protocols_active (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protocol_name TEXT NOT NULL,
    activation_trigger TEXT,
    affected_nodes UUID[],
    lockdown_level INTEGER DEFAULT 0, -- 0 (none) to 5 (nuclear)
    recovery_estimated_time INTERVAL,
    status TEXT DEFAULT 'ARMED' CHECK (status IN ('ARMED', 'ACTIVATED', 'DEACTIVATING', 'COMPLETED')),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- AI and Tenant Isolation (Quarantine)
CREATE TABLE IF NOT EXISTS infrastructure.sovereign_quarantine (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_id UUID NOT NULL, -- agent_id or tenant_id
    quarantine_type TEXT CHECK (quarantine_type IN ('AI_ISOLATION', 'TENANT_FREEZE', 'NETWORK_SEGREGATION')),
    isolation_layer TEXT,
    is_forensic_locked BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Recovery sequences and automatic healing
CREATE TABLE IF NOT EXISTS infrastructure.recovery_orchestration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crisis_id UUID NOT NULL REFERENCES infrastructure.crisis_protocols_active(id),
    step_sequence INTEGER,
    action_type TEXT,
    status TEXT DEFAULT 'PENDING',
    retry_count INTEGER DEFAULT 0,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
