-- 90_super_admin/30_cognitive_core/04_self_awareness.sql
-- FASE 30 — COGNITIVE CORE: Self Awareness

CREATE TABLE IF NOT EXISTS ai_core.system_self_awareness (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    internal_perception_snapshot JSONB,
    structural_inconsistency_detected BOOLEAN DEFAULT false,
    systemic_degradation_detected BOOLEAN DEFAULT false,
    anomaly_details TEXT,
    self_healing_action_taken TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
