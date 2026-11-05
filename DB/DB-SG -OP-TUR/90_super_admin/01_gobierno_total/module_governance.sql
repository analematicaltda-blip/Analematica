-- 90_super_admin/01_gobierno_total/module_governance.sql
-- Governance of SARITA modules and licensing

CREATE TABLE IF NOT EXISTS core.system_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_experimental BOOLEAN DEFAULT false,
    dependencies JSONB DEFAULT '[]',
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS core.tenant_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    module_id UUID NOT NULL REFERENCES core.system_modules(id),
    license_type TEXT CHECK (license_type IN ('FREE', 'PREMIUM', 'ENTERPRISE')),
    active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT,
    UNIQUE(tenant_id, module_id)
);

CREATE TABLE IF NOT EXISTS identity.global_hierarchies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hierarchy_name TEXT NOT NULL, -- e.g., 'SUPER_ROOT', 'ROOT', 'DIRECTOR_GENERAL'
    level INTEGER NOT NULL,
    permissions JSONB,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
