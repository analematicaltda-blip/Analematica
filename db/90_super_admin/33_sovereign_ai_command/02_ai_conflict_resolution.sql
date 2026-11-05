-- 90_super_admin/33_sovereign_ai_command/02_ai_conflict_resolution.sql
-- FASE 33 — SOVEREIGN AI COMMAND: AI Conflict Resolution

CREATE TABLE IF NOT EXISTS ai_core.ai_cognitive_arbitration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_a_id UUID NOT NULL,
    agent_b_id UUID NOT NULL,
    conflict_context TEXT,
    hierarchical_winner_id UUID,
    was_isolated BOOLEAN DEFAULT false, -- If one agent was corrupt
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
