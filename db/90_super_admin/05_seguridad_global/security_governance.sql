-- 90_super_admin/05_seguridad_global/security_governance.sql
-- Global security, RLS enforcement and Anti-fraud

CREATE TABLE IF NOT EXISTS infrastructure.security_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_name TEXT NOT NULL UNIQUE,
    enforcement_level TEXT CHECK (enforcement_level IN ('STRICT', 'PERMISSIVE', 'AUDIT_ONLY')),
    scope JSONB, -- Schemas or tables affected
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS infrastructure.login_audit_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN,
    failure_reason TEXT,
    mfa_verified BOOLEAN,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- A.9 Gobierno de Auditoría y Forense
CREATE TABLE IF NOT EXISTS infrastructure.forensic_audit_chain (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL,
    previous_hash TEXT,
    current_hash TEXT NOT NULL,
    payload_snapshot JSONB,
    verification_status TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
