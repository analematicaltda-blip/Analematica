-- 90_super_admin/26_elite_validation/01_elite_simulations.sql
-- VALIDACIÓN OBLIGATORIA DE NIVEL ÉLITE

CREATE TABLE IF NOT EXISTS testing.elite_simulation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_type TEXT CHECK (simulation_type IN (
        'ECOSYSTEM_COLLAPSE',
        'OPERATIONAL_WAR',
        'AI_CORRUPTION',
        'MASSIVE_BANKRUPTCY',
        'REGIONAL_ISOLATION',
        'INTERNAL_SABOTAGE',
        'FINANCIAL_BLOCKADE',
        'COGNITIVE_CONTAMINATION'
    )),
    start_time TIMESTAMPTZ DEFAULT now(),
    end_time TIMESTAMPTZ,
    resilience_metrics JSONB,
    passed BOOLEAN,
    critical_failures TEXT[],
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS testing.elite_attack_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vector_name TEXT,
    description TEXT,
    remediation_plan_id UUID,
    last_tested_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
