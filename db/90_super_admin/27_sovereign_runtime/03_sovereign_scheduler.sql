-- 90_super_admin/27_sovereign_runtime/03_sovereign_scheduler.sql
-- BLOQUE 3 — SCHEDULER SOBERANO

-- Tactical scheduler for autonomous and critical jobs
CREATE TABLE IF NOT EXISTS infrastructure.tactical_scheduler (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name TEXT NOT NULL,
    job_type TEXT CHECK (job_type IN ('CRITICAL', 'AUTONOMOUS', 'MAINTENANCE', 'ESCALATION')),
    schedule_cron TEXT,
    payload JSONB,
    priority INTEGER DEFAULT 1,
    is_paused BOOLEAN DEFAULT false,
    last_run TIMESTAMPTZ,
    next_run TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Active execution of jobs
CREATE TABLE IF NOT EXISTS infrastructure.job_execution_runtime (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES infrastructure.tactical_scheduler(id),
    status TEXT DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILURE', 'TIMEOUT', 'KILLED')),
    execution_node_id UUID,
    started_at TIMESTAMPTZ DEFAULT now(),
    finished_at TIMESTAMPTZ,
    error_log TEXT,
    retry_count INTEGER DEFAULT 0,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Deadlock and collision resolution
CREATE TABLE IF NOT EXISTS infrastructure.deadlock_resolver (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detected_at TIMESTAMPTZ DEFAULT now(),
    affected_jobs UUID[],
    resolution_action TEXT,
    is_resolved BOOLEAN DEFAULT false,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
