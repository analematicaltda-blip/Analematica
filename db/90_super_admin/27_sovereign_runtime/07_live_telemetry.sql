-- 90_super_admin/27_sovereign_runtime/07_live_telemetry.sql
-- BLOQUE 7 — LIVE TELEMETRY ENGINE

-- Live operational telemetry streams
CREATE TABLE IF NOT EXISTS infrastructure.telemetry_live_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_name TEXT NOT NULL,
    current_value DECIMAL(18, 4),
    units TEXT,
    update_frequency_ms INTEGER,
    status TEXT DEFAULT 'OK' CHECK (status IN ('OK', 'WARNING', 'CRITICAL')),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Operational heatmaps for saturation detection
CREATE TABLE IF NOT EXISTS infrastructure.operational_heatmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id TEXT,
    saturation_score DECIMAL(5, 4),
    active_bottlenecks JSONB,
    prediction_failure_score DECIMAL(5, 4),
    last_update TIMESTAMPTZ DEFAULT now(),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Anomaly detection log
CREATE TABLE IF NOT EXISTS infrastructure.telemetry_anomaly_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anomaly_type TEXT,
    affected_component TEXT,
    severity TEXT,
    ai_validation_status TEXT, -- If AI verified the anomaly
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
