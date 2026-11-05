-- 90_super_admin/21_operational_nervous_system/03_sla_global.sql
-- FASE 4 — SISTEMA NERVIOSO OPERACIONAL: Global SLA

CREATE TABLE IF NOT EXISTS infrastructure.global_sla_governance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id TEXT NOT NULL,
    target_availability DECIMAL(5, 2),
    current_availability DECIMAL(5, 2),
    violation_incidents_count INTEGER DEFAULT 0,
    sla_impact_score DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
