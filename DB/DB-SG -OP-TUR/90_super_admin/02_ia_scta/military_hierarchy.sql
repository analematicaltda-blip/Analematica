-- 90_super_admin/02_ia_scta/military_hierarchy.sql
-- AI Military Hierarchy and activation rules

CREATE TABLE IF NOT EXISTS ai_core.agent_military_hierarchy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL, -- References ai_core.agents
    rank TEXT NOT NULL CHECK (rank IN ('GENERAL', 'COLONEL', 'MAJOR', 'CAPTAIN', 'LIEUTENANT', 'SERGEANT')),
    command_chain_id UUID, -- Parent in hierarchy
    authority_level INTEGER NOT NULL,
    activation_rules JSONB,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS ai_core.agent_global_orchestration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    orchestrator_agent_id UUID NOT NULL,
    target_domain TEXT NOT NULL, -- e.g., 'FINANCE', 'TOURISM'
    coordination_policy TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
