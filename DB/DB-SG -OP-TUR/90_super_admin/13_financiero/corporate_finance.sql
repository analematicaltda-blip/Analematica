-- 90_super_admin/13_financiero/corporate_finance.sql
-- B.5 Gestión Financiera SARITA

CREATE TABLE IF NOT EXISTS erp.saas_metrics_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_period DATE,
    mrr DECIMAL(18, 2), -- Monthly Recurring Revenue
    arr DECIMAL(18, 2), -- Annual Recurring Revenue
    churn_rate DECIMAL(5, 2),
    cac DECIMAL(18, 2), -- Customer Acquisition Cost
    ltv DECIMAL(18, 2), -- Lifetime Value
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.expansion_investment_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name TEXT,
    allocated_budget DECIMAL(18, 2),
    spent_amount DECIMAL(18, 2),
    expected_roi DECIMAL(5, 2),
    status TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
