-- 90_super_admin/27_sovereign_runtime/04_ai_execution_layer.sql
-- BLOQUE 4 — AI EXECUTION LAYER

-- Active execution of AI agents
CREATE TABLE IF NOT EXISTS ai_core.live_agent_execution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    current_task_id UUID,
    execution_context JSONB,
    command_chain_level INTEGER, -- Hierarchical rank
    status TEXT DEFAULT 'IDLE' CHECK (status IN ('IDLE', 'EXECUTING', 'WAITING', 'FAILED', 'SUSPENDED')),
    resource_consumption_score DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Strategic vs Tactical agent decisions
CREATE TABLE IF NOT EXISTS ai_core.agent_tactical_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    decision_type TEXT CHECK (decision_type IN ('TACTICAL', 'STRATEGIC', 'EMERGENCY')),
    decision_payload JSONB,
    confidence_score DECIMAL(5, 4),
    justification TEXT,
    was_executed BOOLEAN DEFAULT false,
    execution_trace_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- AI Execution metrics and failure tracking
CREATE TABLE IF NOT EXISTS ai_core.ai_execution_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    success_rate DECIMAL(5, 4),
    avg_latency_ms INTEGER,
    failure_patterns JSONB, -- Detection of repetitive errors
    last_failure_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
