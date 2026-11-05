-- 90_super_admin/21_operational_nervous_system/02_operational_pressure.sql
-- FASE 4 — SISTEMA NERVIOSO OPERACIONAL: Pressure

CREATE TABLE IF NOT EXISTS infrastructure.operational_pressure_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id TEXT, -- 'FINANCE', 'ERP', 'CORE'
    tenant_pressure_map JSONB, -- pressure score per tenant
    inter_domain_conflicts JSONB,
    saturation_level DECIMAL(5, 4),
    last_rebalance_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
