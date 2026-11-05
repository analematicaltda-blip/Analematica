-- 90_super_admin/32_digital_twin/04_strategic_scenarios.sql
-- FASE 32 — DIGITAL TWIN ECOSYSTEM: Strategic Scenarios

CREATE TABLE IF NOT EXISTS infrastructure.strategic_war_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    war_scenario_name TEXT NOT NULL, -- e.g., 'ECONOMIC_WAR', 'INTERNAL_SABOTAGE', 'AI_REBELLION'
    threat_parameters JSONB,
    survival_strategy_id UUID,
    simulated_impact_score DECIMAL(5, 4),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
