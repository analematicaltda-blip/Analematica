-- 90_super_admin/31_autonomous_evolution/04_operational_mutation_control.sql
-- FASE 31 — AUTONOMOUS EVOLUTION ENGINE: Operational Mutation Control

CREATE TABLE IF NOT EXISTS infrastructure.operational_mutation_quarantine (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mutation_id UUID NOT NULL,
    anti_corruption_validation BOOLEAN DEFAULT false,
    quarantine_status TEXT DEFAULT 'PENDING',
    auto_rollback_triggered BOOLEAN DEFAULT false,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
