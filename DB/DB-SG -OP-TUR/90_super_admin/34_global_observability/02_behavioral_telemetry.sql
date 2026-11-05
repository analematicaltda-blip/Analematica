-- 90_super_admin/34_global_observability/02_behavioral_telemetry.sql
-- FASE 34 — GLOBAL OBSERVABILITY MATRIX: Behavioral Telemetry

CREATE TABLE IF NOT EXISTS infrastructure.behavioral_telemetry_ia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    pattern_anomaly_detected BOOLEAN DEFAULT false,
    financial_behavior_score DECIMAL(5, 4),
    operational_interaction_score DECIMAL(5, 4),
    behavior_category TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
