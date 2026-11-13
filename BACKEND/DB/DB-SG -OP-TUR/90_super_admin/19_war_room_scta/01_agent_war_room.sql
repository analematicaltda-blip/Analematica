-- 90_super_admin/19_war_room_scta/01_agent_war_room.sql
-- FASE 2 — WAR ROOM SCTA: Agent Live Map

CREATE TABLE IF NOT EXISTS ai_core.agent_war_room_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    current_status TEXT CHECK (current_status IN ('ACTIVE', 'DEGRADED', 'ORPHAN', 'CORRUPT', 'REBEL', 'STOPPED', 'OUT_OF_COVERAGE', 'SATURATED', 'UNTRACEABLE')),
    cognitive_risk_score DECIMAL(5, 2), -- 0.00 to 100.00
    last_trace_id UUID,
    active_conflicts JSONB DEFAULT '[]',
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS ai_core.agent_conflict_resolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conflict_type TEXT,
    agent_a_id UUID NOT NULL,
    agent_b_id UUID NOT NULL,
    resolution_priority INTEGER,
    status TEXT DEFAULT 'PENDING',
    arbitrator_agent_id UUID, -- Higher hierarchy agent
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
