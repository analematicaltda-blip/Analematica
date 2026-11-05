-- 90_super_admin/18_kernel_gobierno/01_global_kernel.sql
-- FASE 1 — KERNEL DE GOBIERNO GLOBAL

-- Sovereign system state
CREATE TABLE IF NOT EXISTS infrastructure.global_system_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    current_mode TEXT NOT NULL CHECK (current_mode IN ('NORMAL', 'MAINTENANCE', 'CONTINGENCY', 'AUDIT', 'EMERGENCY_SHUTDOWN')),
    is_sovereign_active BOOLEAN DEFAULT true,
    global_version TEXT,
    system_hash TEXT, -- Integrity of the entire schema state
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Activation matrix for modules across the ecosystem
CREATE TABLE IF NOT EXISTS infrastructure.module_activation_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID NOT NULL,
    is_globally_active BOOLEAN DEFAULT true,
    priority_level INTEGER DEFAULT 1, -- Higher = more critical
    can_be_frozen BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Freeze control for tenants (Sovereign suspension)
CREATE TABLE IF NOT EXISTS core.tenant_freeze_control (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    freeze_type TEXT CHECK (freeze_type IN ('FULL', 'READ_ONLY', 'FINANCIAL_ONLY', 'IA_ONLY')),
    reason_code TEXT,
    is_active BOOLEAN DEFAULT true,
    frozen_at TIMESTAMPTZ DEFAULT now(),
    unfrozen_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL, -- Master Tenant ID
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Regional isolation protocols
CREATE TABLE IF NOT EXISTS governance.regional_isolation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL, -- DIVIPOLA / Municipality
    isolation_mode TEXT CHECK (isolation_mode IN ('TOTAL', 'RESTRICTED', 'DATA_ONLY')),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- AI Shutdown and emergency control
CREATE TABLE IF NOT EXISTS ai_core.ai_shutdown_control (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID, -- If null, affects ALL agents
    shutdown_level TEXT CHECK (shutdown_level IN ('SOFT', 'HARD', 'NUCLEAR')), -- Nuclear = kill process + wipe temp memory
    trigger_source TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Sovereign policies and catastrophic events
CREATE TABLE IF NOT EXISTS infrastructure.sovereign_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_name TEXT NOT NULL,
    enforcement_logic TEXT, -- SQL or JSON rules
    priority INTEGER,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS infrastructure.catastrophic_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT,
    impact_level TEXT,
    recovery_protocol_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
