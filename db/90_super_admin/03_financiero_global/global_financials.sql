-- 90_super_admin/03_financiero_global/global_financials.sql
-- Global financial governance, wallets, and marketplace commissions

CREATE TABLE IF NOT EXISTS finance.global_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL, -- Can be a tenant or SARITA itself
    wallet_type TEXT CHECK (wallet_type IN ('MASTER', 'COLLECTION', 'DISBURSEMENT', 'ESCROW')),
    balance DECIMAL(24, 8) DEFAULT 0,
    currency TEXT DEFAULT 'USD',
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS finance.marketplace_commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL, -- e.g., 'ARTISAN', 'HOTEL', 'TOUR'
    percentage DECIMAL(5, 2) NOT NULL,
    fixed_fee DECIMAL(18, 2) DEFAULT 0,
    active BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS finance.global_payment_distribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL,
    recipient_id UUID NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    role TEXT NOT NULL, -- e.g., 'PROVIDER', 'SARITA_COMMISSION', 'TAX_AUTHORITY'
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
