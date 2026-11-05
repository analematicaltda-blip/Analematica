-- 90_super_admin/23_federacion_soberana/03_sovereign_ai.sql
-- FASE 6 — SOBERANÍA MULTIEMPRESA: Sovereign AI and Memory

CREATE TABLE IF NOT EXISTS ai_core.federated_agent_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    federation_id UUID NOT NULL,
    agent_category TEXT,
    operational_limit_rules JSONB,
    memory_isolation_policy TEXT,
    autonomous_decision_allowed BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
