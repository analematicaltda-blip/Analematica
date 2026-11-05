-- 90_super_admin/09_comercial/internal_crm.sql
-- B.1 Gestión Comercial SARITA (Internal)

CREATE TABLE IF NOT EXISTS erp.crm_leads_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    entity_sector TEXT, -- 'GOVERNMENT', 'HOSPITALITY', 'COMMERCE'
    funnel_stage TEXT CHECK (funnel_stage IN ('LEAD', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST')),
    estimated_revenue DECIMAL(18, 2),
    assigned_user_id UUID, -- Internal salesperson
    contact_payload JSONB,
    source TEXT, -- 'INBOUND', 'OUTBOUND', 'WPC_FUNNEL'
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.marketing_campaigns_internal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_name TEXT NOT NULL,
    channel TEXT, -- 'WHATSAPP', 'EMAIL', 'ADS'
    budget DECIMAL(18, 2),
    roi_metrics JSONB,
    ai_optimized BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
