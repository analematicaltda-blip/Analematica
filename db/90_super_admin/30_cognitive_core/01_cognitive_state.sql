-- 90_super_admin/30_cognitive_core/01_cognitive_state.sql
-- FASE 30 — COGNITIVE CORE: Cognitive State

CREATE TABLE IF NOT EXISTS ai_core.cognitive_state_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operational_consciousness_level DECIMAL(5, 4), -- 0.0 to 1.0
    ecosystem_saturation DECIMAL(5, 4),
    systemic_stability_index DECIMAL(5, 4),
    active_intelligence_index DECIMAL(5, 4),
    cognitive_corruption_risk DECIMAL(5, 4),
    resilience_index DECIMAL(5, 4),
    current_thought_process_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
