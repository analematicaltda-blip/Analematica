-- 90_super_admin/27_sovereign_runtime/02_event_bus.sql
-- BLOQUE 2 — EVENT BUS OPERACIONAL

-- Global circulatory system for ecosystem events
CREATE TABLE IF NOT EXISTS events.global_event_bus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    source_component TEXT NOT NULL,
    payload JSONB NOT NULL,
    priority INTEGER DEFAULT 1, -- 1 to 10
    correlation_id UUID,
    emitted_at TIMESTAMPTZ DEFAULT now(),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Event dispatcher and subscriptions
CREATE TABLE IF NOT EXISTS events.event_dispatcher (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events.global_event_bus(id),
    subscriber_id TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'RETRYING')),
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    processed_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Dead letter queue for failed events
CREATE TABLE IF NOT EXISTS events.dead_letter_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_event_id UUID NOT NULL,
    failure_reason TEXT,
    is_recovered BOOLEAN DEFAULT false,
    recovery_trace_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
