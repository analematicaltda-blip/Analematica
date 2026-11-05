-- 90_super_admin/19_war_room_scta/02_cognitive_surveillance.sql
-- FASE 2 — WAR ROOM SCTA: Cognitive Surveillance

CREATE TABLE IF NOT EXISTS ai_core.cognitive_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_time TIMESTAMPTZ DEFAULT now(),
    cognitive_latency_ms INTEGER,
    memory_contamination_index DECIMAL(5, 4),
    scta_coverage_percentage DECIMAL(5, 2),
    operational_pressure_ia DECIMAL(5, 2),
    active_rebellions_count INTEGER DEFAULT 0,
    domain_id TEXT, -- e.g., 'FINANCE', 'TOURISM'
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS ai_core.agent_memory_surveillance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL,
    memory_segment_id UUID,
    integrity_status TEXT,
    is_corrupt BOOLEAN DEFAULT false,
    last_audit_time TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
