-- 90_super_admin/22_memory_governance/01_memory_audit.sql
-- FASE 5 — GOBIERNO COGNITIVO DE MEMORIA IA

CREATE TABLE IF NOT EXISTS ai_core.memory_governance_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL,
    agent_id UUID NOT NULL,
    access_time TIMESTAMPTZ DEFAULT now(),
    is_authorized BOOLEAN DEFAULT true,
    action_performed TEXT, -- 'READ', 'WRITE', 'EVOLVE'
    context_consistency_score DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS ai_core.memory_corruption_detection (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_segment_id UUID NOT NULL,
    corruption_type TEXT CHECK (corruption_type IN ('TOXIC', 'CROSS_CONTAMINATION', 'ORPHAN', 'INCONSISTENT', 'MANIPULATED', 'DUPLICATED')),
    detection_method TEXT, -- 'SCTA_VALIDATION', 'AGENT_AUDIT'
    impact_level TEXT,
    quarantine_status BOOLEAN DEFAULT false,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
