-- 90_super_admin/14_expansion/expansion_management.sql
-- B.7 Gestión de Expansión Empresarial

CREATE TABLE IF NOT EXISTS erp.franchise_network (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    franchise_name TEXT NOT NULL,
    owner_entity_id UUID,
    territory_jurisdiction JSONB,
    royalty_percentage DECIMAL(5, 2),
    status TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.partner_white_labels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_name TEXT NOT NULL,
    custom_domain TEXT UNIQUE,
    branding_config JSONB,
    integration_endpoints JSONB,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
