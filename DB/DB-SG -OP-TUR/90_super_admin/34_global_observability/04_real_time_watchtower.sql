-- 90_super_admin/34_global_observability/04_real_time_watchtower.sql
-- FASE 34 — GLOBAL OBSERVABILITY MATRIX: Real Time Watchtower

CREATE TABLE IF NOT EXISTS infrastructure.sovereign_watchtower_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_severity TEXT CHECK (alert_severity IN ('INFO', 'WARNING', 'CRITICAL', 'SOVEREIGN_EMERGENCY')),
    component_source TEXT,
    event_description TEXT,
    is_mitigated BOOLEAN DEFAULT false,
    ai_resolution_trace_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
