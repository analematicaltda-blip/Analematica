-- 90_super_admin/04_operacional_global/monitoring.sql
-- Global operational monitoring and service status

CREATE TABLE IF NOT EXISTS infrastructure.service_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT NOT NULL,
    status TEXT CHECK (status IN ('HEALTHY', 'DEGRADED', 'DOWN')),
    uptime_percentage DECIMAL(5, 2),
    last_ping TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS infrastructure.global_job_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL,
    payload JSONB,
    status TEXT DEFAULT 'PENDING',
    priority INTEGER DEFAULT 0,
    scheduled_for TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    error_log TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
