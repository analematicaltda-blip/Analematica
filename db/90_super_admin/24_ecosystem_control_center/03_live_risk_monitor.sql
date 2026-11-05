-- 90_super_admin/24_ecosystem_control_center/03_live_risk_monitor.sql
-- FASE 7 — CENTRO DE CONTROL TOTAL DEL ECOSISTEMA: Risk and Threat Monitoring

CREATE TABLE IF NOT EXISTS infrastructure.active_threat_monitor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    threat_type TEXT, -- 'SECURITY', 'FINANCIAL', 'COGNITIVE', 'OPERATIONAL'
    target_entities UUID[],
    severity_level TEXT,
    ai_mitigation_status TEXT,
    is_live BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
