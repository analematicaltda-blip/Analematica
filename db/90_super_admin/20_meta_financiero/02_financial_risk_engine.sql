-- 90_super_admin/20_meta_financiero/02_financial_risk_engine.sql
-- FASE 3 — META CONTROL FINANCIERO: Risk Engine

CREATE TABLE IF NOT EXISTS finance.systemic_risk_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exposure_per_tenant JSONB, -- Map of tenant_id -> exposure_score
    insolvency_risk_index DECIMAL(5, 4),
    loss_propagation_factor DECIMAL(5, 4),
    fraud_anomaly_detected BOOLEAN DEFAULT false,
    systemic_stress_level TEXT CHECK (systemic_stress_level IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS finance.fraud_prevention_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type TEXT,
    affected_entities UUID[],
    block_action_taken BOOLEAN DEFAULT false,
    ai_risk_assessment JSONB,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
