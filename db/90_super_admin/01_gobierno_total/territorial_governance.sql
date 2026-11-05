-- 90_super_admin/01_gobierno_total/territorial_governance.sql
-- A.6 Gobierno Territorial y Geoespacial

CREATE TABLE IF NOT EXISTS governance.countries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    iso_code TEXT NOT NULL UNIQUE, -- e.g., 'COL', 'USA'
    country_name TEXT NOT NULL,
    continent TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS governance.territorial_divisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES governance.countries(id),
    division_name TEXT NOT NULL, -- Departamento / Estado
    divipola_code TEXT, -- Specific for Colombia, but extensible
    geographic_bounds GEOGRAPHY(POLYGON, 4326),
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS governance.municipalities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    division_id UUID NOT NULL REFERENCES governance.territorial_divisions(id),
    municipality_name TEXT NOT NULL,
    divipola_code TEXT UNIQUE,
    geo_center GEOGRAPHY(POINT, 4326),
    jurisdiction_type TEXT, -- 'URBAN', 'RURAL', 'SPECIAL'
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
