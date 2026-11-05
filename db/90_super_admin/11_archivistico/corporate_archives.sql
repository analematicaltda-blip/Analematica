-- 90_super_admin/11_archivistico/corporate_archives.sql
-- B.3 Gestión Archivística SARITA

CREATE TABLE IF NOT EXISTS erp.corporate_legal_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_type TEXT NOT NULL, -- 'CONTRACT', 'NDA', 'POLICY', 'ISO_CERT'
    version_label TEXT,
    signing_status TEXT,
    digital_signature_id UUID,
    expiry_date DATE,
    metadata JSONB,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
