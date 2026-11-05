-- 90_super_admin/12_contable/internal_accounting.sql
-- SARITA Internal ERP: Accounting and Taxes

CREATE TABLE IF NOT EXISTS erp.corporate_puc (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_code TEXT NOT NULL UNIQUE,
    account_name TEXT NOT NULL,
    account_type TEXT CHECK (account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')),
    parent_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.corporate_financial_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type TEXT NOT NULL, -- 'BALANCE_SHEET', 'PROFIT_LOSS'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    data JSONB,
    generated_by_agent_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
