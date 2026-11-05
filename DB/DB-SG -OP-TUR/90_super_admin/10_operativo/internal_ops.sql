-- 90_super_admin/10_operativo/internal_ops.sql
-- B.2 Gestión Operativa SARITA

CREATE TABLE IF NOT EXISTS erp.internal_service_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_type TEXT NOT NULL, -- 'MAINTENANCE', 'IMPLEMENTATION', 'SUPPORT'
    priority TEXT CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    status TEXT DEFAULT 'PENDING',
    sla_hours INTEGER,
    assigned_team_id UUID,
    resolution_details TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.operational_monitoring_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_name TEXT,
    metric_key TEXT,
    metric_value DECIMAL(18, 4),
    is_anomaly BOOLEAN DEFAULT false,
    ai_intervention_id UUID,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
