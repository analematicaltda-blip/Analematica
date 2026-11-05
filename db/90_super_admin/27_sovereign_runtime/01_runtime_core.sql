-- 90_super_admin/27_sovereign_runtime/01_runtime_core.sql
-- BLOQUE 1 — RUNTIME CENTRAL SOBERANO

-- Live state of the sovereign runtime
CREATE TABLE IF NOT EXISTS infrastructure.runtime_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id TEXT NOT NULL,
    current_mode TEXT NOT NULL CHECK (current_mode IN ('NORMAL', 'ALERT', 'CRISIS', 'LOCKDOWN', 'RECOVERY', 'WAR_MODE')),
    health_score DECIMAL(5, 4),
    last_heartbeat TIMESTAMPTZ DEFAULT now(),
    is_active BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Tracking of execution cycles (Sovereign Pulse)
CREATE TABLE IF NOT EXISTS infrastructure.runtime_execution_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_start TIMESTAMPTZ DEFAULT now(),
    cycle_end TIMESTAMPTZ,
    tasks_processed INTEGER DEFAULT 0,
    failures_detected INTEGER DEFAULT 0,
    cycle_pressure DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Failover and node management
CREATE TABLE IF NOT EXISTS infrastructure.runtime_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_name TEXT UNIQUE,
    node_type TEXT CHECK (node_type IN ('MASTER', 'WORKER', 'OBSERVER', 'SCTA_CORE')),
    region_id UUID,
    status TEXT DEFAULT 'ONLINE',
    load_index DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Emergency switch for crisis modes
CREATE TABLE IF NOT EXISTS infrastructure.runtime_emergency_switch (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_source TEXT,
    target_mode TEXT NOT NULL,
    justification TEXT,
    is_reversible BOOLEAN DEFAULT true,
    executed_at TIMESTAMPTZ DEFAULT now(),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
