CREATE TABLE IF NOT EXISTS ai_core.agent_memory_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL, -- Logical segmentation (GOV, TOURIST, etc)
    entity_id UUID NOT NULL,
    agent_id UUID NOT NULL REFERENCES ai_core.agents_master(id),
    memory_content JSONB NOT NULL,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
