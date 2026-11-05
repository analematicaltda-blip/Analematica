-- 90_super_admin/20_meta_financiero/01_financial_brain.sql
-- FASE 3 — META CONTROL FINANCIERO: Financial Brain

CREATE TABLE IF NOT EXISTS finance.ecosystem_liquidity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_liquidity DECIMAL(24, 8),
    locked_assets DECIMAL(24, 8),
    circulating_supply DECIMAL(24, 8),
    currency TEXT DEFAULT 'USD',
    global_reserve_ratio DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS finance.sovereign_ledger_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_time TIMESTAMPTZ DEFAULT now(),
    source_entity_id UUID NOT NULL, -- Tenant or System
    target_entity_id UUID NOT NULL,
    amount DECIMAL(24, 8),
    entry_type TEXT CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    event_sourcing_id UUID NOT NULL,
    mathematical_trace_hash TEXT NOT NULL, -- Forensically verifiable chain
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
