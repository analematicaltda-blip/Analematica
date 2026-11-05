-- 90_super_admin/30_cognitive_core/03_cognitive_decisions.sql
-- FASE 30 — COGNITIVE CORE: Cognitive Decisions

CREATE TABLE IF NOT EXISTS ai_core.autonomous_decisions_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_tree_path JSONB,
    authorization_level_required INTEGER,
    dynamic_priority INTEGER,
    decision_risk_score DECIMAL(5, 4),
    was_rolled_back BOOLEAN DEFAULT false,
    rollback_reason TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
