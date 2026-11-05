-- 90_super_admin/34_global_observability/03_global_heatmaps.sql
-- FASE 34 — GLOBAL OBSERVABILITY MATRIX: Global Heatmaps

CREATE TABLE IF NOT EXISTS infrastructure.global_system_heatmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    heatmap_type TEXT CHECK (heatmap_type IN ('FINANCIAL_PRESSURE', 'COGNITIVE_LOAD', 'OPERATIONAL_LATENCY', 'TERRITORIAL_ACTIVITY')),
    intensity_map JSONB, -- Map of domain/region -> intensity
    last_extreme_event_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
