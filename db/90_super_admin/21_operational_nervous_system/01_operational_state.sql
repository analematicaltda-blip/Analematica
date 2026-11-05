-- 90_super_admin/21_operational_nervous_system/01_operational_state.sql
-- FASE 4 — SISTEMA NERVIOSO OPERACIONAL: Observability

CREATE TABLE IF NOT EXISTS infrastructure.operational_nervous_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id TEXT NOT NULL,
    health_index DECIMAL(5, 4),
    is_degraded BOOLEAN DEFAULT false,
    active_bottlenecks JSONB,
    blocked_ops_count INTEGER DEFAULT 0,
    latency_p99 INTEGER, -- in ms
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS infrastructure.global_telemetry_stream (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT,
    source_domain TEXT,
    payload JSONB,
    severity TEXT CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL', 'FATAL')),
    operational_pressure_score DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
