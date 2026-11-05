-- 90_super_admin/32_digital_twin/03_failure_prediction.sql
-- FASE 32 — DIGITAL TWIN ECOSYSTEM: Failure Prediction

CREATE TABLE IF NOT EXISTS infrastructure.failure_prediction_engine (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_component TEXT,
    predicted_failure_type TEXT,
    confidence_interval JSONB,
    early_warning_triggered BOOLEAN DEFAULT false,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
