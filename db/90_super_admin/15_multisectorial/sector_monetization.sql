-- 90_super_admin/15_multisectorial/sector_monetization.sql
-- Monetization strategies for different sectors

CREATE TABLE IF NOT EXISTS erp.sector_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_name TEXT NOT NULL, -- 'HOTEL', 'RESTAURANT', 'GOVERNMENT', 'ARTISAN'
    plan_name TEXT NOT NULL,
    base_price DECIMAL(18, 2),
    commission_rate DECIMAL(5, 2),
    features JSONB,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.white_label_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL UNIQUE,
    brand_name TEXT,
    custom_domain TEXT,
    theme_settings JSONB,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
