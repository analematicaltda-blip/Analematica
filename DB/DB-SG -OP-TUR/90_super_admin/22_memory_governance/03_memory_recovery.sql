-- 90_super_admin/22_memory_governance/03_memory_recovery.sql
-- FASE 5 — GOBIERNO COGNITIVO DE MEMORIA IA: Recovery and Lifecycle

CREATE TABLE IF NOT EXISTS ai_core.cognitive_rollback_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    rollback_target_time TIMESTAMPTZ,
    reason_code TEXT,
    affected_memories JSONB,
    recovery_status TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS ai_core.memory_lifecycle_control (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_category TEXT,
    retention_policy JSONB,
    auto_purge_enabled BOOLEAN DEFAULT true,
    last_purge_at TIMESTAMPTZ,
    memory_growth_rate DECIMAL(10, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
