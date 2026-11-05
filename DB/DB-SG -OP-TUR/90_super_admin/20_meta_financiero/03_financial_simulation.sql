-- 90_super_admin/20_meta_financiero/03_financial_simulation.sql
-- FASE 3 — META CONTROL FINANCIERO: Simulations

CREATE TABLE IF NOT EXISTS finance.financial_collapse_simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_name TEXT,
    trigger_conditions JSONB,
    simulated_impact JSONB, -- Loss of liquidity, churn, etc.
    resilience_score DECIMAL(5, 2),
    generated_by_agent_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS finance.multi_client_pressure_test (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_parameters JSONB,
    bottleneck_detected TEXT,
    simulation_log_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
