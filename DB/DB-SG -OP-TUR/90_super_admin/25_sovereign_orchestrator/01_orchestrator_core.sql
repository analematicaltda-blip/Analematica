-- 90_super_admin/25_sovereign_orchestrator/01_orchestrator_core.sql
-- FASE 8 — ORQUESTADOR CENTRAL SOBERANO: Core Orchestration

CREATE TABLE IF NOT EXISTS infrastructure.global_orchestration_plan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_name TEXT,
    execution_priority INTEGER,
    target_domains TEXT[],
    autonomous_scaling_enabled BOOLEAN DEFAULT true,
    last_execution_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS infrastructure.conflict_arbitration_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conflict_source_id UUID NOT NULL,
    domain_a TEXT,
    domain_b TEXT,
    arbitration_logic TEXT,
    winner_domain TEXT,
    applied_at TIMESTAMPTZ DEFAULT now(),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
