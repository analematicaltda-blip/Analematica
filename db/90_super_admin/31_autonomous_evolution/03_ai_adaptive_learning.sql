-- 90_super_admin/31_autonomous_evolution/03_ai_adaptive_learning.sql
-- FASE 31 — AUTONOMOUS EVOLUTION ENGINE: AI Adaptive Learning

CREATE TABLE IF NOT EXISTS ai_core.adaptive_learning_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name TEXT,
    historical_relevance_score DECIMAL(5, 4),
    adaptive_priority_adjustment JSONB,
    evolutionary_memory_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
