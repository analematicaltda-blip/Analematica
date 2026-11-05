-- 90_super_admin/25_sovereign_orchestrator/02_priority_engine.sql
-- FASE 8 — ORQUESTADOR CENTRAL SOBERANO: Priority Engine

CREATE TABLE IF NOT EXISTS infrastructure.systemic_priority_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT,
    base_priority INTEGER,
    dynamic_priority_rules JSONB,
    critical_threshold INTEGER,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
