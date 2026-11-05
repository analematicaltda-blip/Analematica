-- 90_super_admin/08_erp_corporativo/internal_crm.sql
-- SARITA Internal ERP: CRM and Commercial Management

CREATE TABLE IF NOT EXISTS erp.corporate_crm_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL, -- e.g., 'Gobernación de Antioquia', 'Hotel X'
    entity_type TEXT NOT NULL, -- 'GOVERNMENT', 'PROVIDER', 'PARTNER'
    contact_info JSONB,
    funnel_stage TEXT NOT NULL,
    assigned_agent_id UUID,
    estimated_value DECIMAL(18, 2),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.corporate_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    plan_name TEXT NOT NULL,
    billing_cycle TEXT CHECK (billing_cycle IN ('MONTHLY', 'ANNUAL')),
    amount DECIMAL(18, 2),
    status TEXT DEFAULT 'ACTIVE',
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.corporate_expansion_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_name TEXT NOT NULL, -- e.g., 'Franchise Bogota'
    unit_type TEXT NOT NULL, -- 'FRANCHISE', 'BRANCH', 'WHITE_LABEL'
    parent_id UUID,
    geographic_coverage JSONB, -- DIVIPOLA codes
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
