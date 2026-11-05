-- 90_super_admin/27_sovereign_runtime/09_memory_runtime.sql
-- BLOQUE 9 — MEMORY EXECUTION GOVERNANCE

-- Dynamic AI memory contexts in runtime
CREATE TABLE IF NOT EXISTS ai_core.runtime_memory_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    active_context_id UUID,
    memory_priority INTEGER DEFAULT 1,
    context_size_kb INTEGER,
    last_access_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Cognitive overload detection and mitigation
CREATE TABLE IF NOT EXISTS ai_core.cognitive_overload_runtime (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    overload_score DECIMAL(5, 4),
    mitigation_action TEXT, -- 'CONTEXT_FLUSH', 'AGENT_THROTTLING', 'MEMORY_OFFLOAD'
    is_active BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Tactical memory switching and expiration
CREATE TABLE IF NOT EXISTS ai_core.memory_runtime_switching (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    previous_context_id UUID,
    new_context_id UUID,
    switch_reason TEXT,
    switch_latency_ms INTEGER,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
