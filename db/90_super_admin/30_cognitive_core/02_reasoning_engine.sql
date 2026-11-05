-- 90_super_admin/30_cognitive_core/02_reasoning_engine.sql
-- FASE 30 — COGNITIVE CORE: Reasoning Engine

CREATE TABLE IF NOT EXISTS ai_core.reasoning_active_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_type TEXT CHECK (reasoning_type IN ('TACTICAL', 'STRATEGIC', 'FINANCIAL', 'TERRITORIAL', 'OPERATIONAL')),
    context_data JSONB,
    inference_path JSONB,
    conclusion_reached TEXT,
    confidence_score DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
