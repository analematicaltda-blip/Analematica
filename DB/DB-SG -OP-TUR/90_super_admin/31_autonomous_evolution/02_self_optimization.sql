-- 90_super_admin/31_autonomous_evolution/02_self_optimization.sql
-- FASE 31 — AUTONOMOUS EVOLUTION ENGINE: Self Optimization

CREATE TABLE IF NOT EXISTS infrastructure.self_optimization_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bottleneck_component TEXT,
    detected_issue TEXT,
    recommendation_logic JSONB, -- e.g., 'CREATE INDEX', 'REPARTITION'
    was_applied BOOLEAN DEFAULT false,
    performance_gain_est DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
