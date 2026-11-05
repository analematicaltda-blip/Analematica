-- 90_super_admin/31_autonomous_evolution/01_schema_evolution.sql
-- FASE 31 — AUTONOMOUS EVOLUTION ENGINE: Schema Evolution

CREATE TABLE IF NOT EXISTS infrastructure.schema_evolution_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_schema TEXT NOT NULL,
    version_tag TEXT NOT NULL,
    evolution_type TEXT CHECK (evolution_type IN ('EXPANSION', 'OPTIMIZATION', 'PATCH', 'MUTATION')),
    change_log JSONB,
    is_backward_compatible BOOLEAN DEFAULT true,
    rollback_plan_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
