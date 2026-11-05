-- 90_super_admin/32_digital_twin/01_ecosystem_twin.sql
-- FASE 32 — DIGITAL TWIN ECOSYSTEM: Ecosystem Twin

CREATE TABLE IF NOT EXISTS infrastructure.ecosystem_digital_twin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_timestamp TIMESTAMPTZ DEFAULT now(),
    virtual_state_snapshot JSONB, -- Full operational replica state
    is_synchronized BOOLEAN DEFAULT true,
    last_sync_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
