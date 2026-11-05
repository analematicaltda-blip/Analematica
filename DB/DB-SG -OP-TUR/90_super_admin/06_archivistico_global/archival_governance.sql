-- 90_super_admin/06_archivistico_global/archival_governance.sql
-- Global Archival and Document Custody

CREATE TABLE IF NOT EXISTS erp.archival_trd (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    document_series TEXT NOT NULL,
    retention_years_office INTEGER,
    retention_years_central INTEGER,
    disposition_procedure TEXT, -- ELIMINATION, CONSERVATION, DIGITALIZATION
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

CREATE TABLE IF NOT EXISTS erp.global_document_custody (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    storage_provider TEXT, -- S3, IPFS, LOCAL
    storage_path TEXT,
    checksum_sha256 TEXT,
    is_forensic_immutable BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
