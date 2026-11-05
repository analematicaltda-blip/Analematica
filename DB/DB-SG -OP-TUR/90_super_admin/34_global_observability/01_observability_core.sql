-- 90_super_admin/34_global_observability/01_observability_core.sql
-- FASE 34 — GLOBAL OBSERVABILITY MATRIX: Observability Core

CREATE TABLE IF NOT EXISTS infrastructure.global_observability_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matrix_version TEXT,
    system_health_score DECIMAL(5, 4),
    universal_state_summary JSONB,
    active_monitors_count INTEGER,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
