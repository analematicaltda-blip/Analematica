-- 90_super_admin/23_federacion_soberana/01_federated_governance.sql
-- FASE 6 — SOBERANÍA MULTIEMPRESA: Federated Governance

CREATE TABLE IF NOT EXISTS governance.ecosystem_federation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    federation_name TEXT NOT NULL,
    parent_ecosystem_id UUID, -- If null, this is a Root Sovereign
    jurisdiction_scope JSONB, -- Countries, Depts
    sovereignty_level TEXT CHECK (sovereignty_level IN ('TOTAL', 'DELEGATED', 'PARTIAL')),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS governance.federated_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    federation_id UUID NOT NULL REFERENCES governance.ecosystem_federation(id),
    policy_type TEXT, -- 'FINANCIAL', 'IA', 'DATA', 'OPERATIONAL'
    policy_definition JSONB,
    override_priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
