-- 90_super_admin/24_ecosystem_control_center/01_ecosystem_visibility.sql
-- FASE 7 — CENTRO DE CONTROL TOTAL DEL ECOSISTEMA: Visibility

CREATE TABLE IF NOT EXISTS infrastructure.ecosystem_live_view (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    view_timestamp TIMESTAMPTZ DEFAULT now(),
    active_tenants_count INTEGER,
    active_agents_count INTEGER,
    global_financial_health_score DECIMAL(5, 4),
    global_operational_status TEXT,
    systemic_risk_level TEXT,
    active_threats_count INTEGER DEFAULT 0,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS infrastructure.ecosystem_health_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id TEXT, -- 'FINANCE', 'IA', 'CORE', 'OPERATIONS'
    health_score DECIMAL(5, 4),
    degradation_detected BOOLEAN DEFAULT false,
    recovery_action_pending BOOLEAN DEFAULT false,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
