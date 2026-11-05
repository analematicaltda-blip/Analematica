-- 90_super_admin/07_marketplace_global/marketplace_logic.sql
-- Global Marketplace governance

CREATE TABLE IF NOT EXISTS tourism.marketplace_offerings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL,
    offering_type TEXT CHECK (offering_type IN ('PRODUCT', 'SERVICE', 'EXPERIENCE', 'ACCOMMODATION')),
    title TEXT NOT NULL,
    description TEXT,
    base_price DECIMAL(18, 2),
    stock_status TEXT,
    geo_location GEOGRAPHY(POINT, 4326),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS tourism.global_inventory_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    offering_id UUID NOT NULL REFERENCES tourism.marketplace_offerings(id),
    available_units INTEGER,
    reserved_units INTEGER DEFAULT 0,
    last_update TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
