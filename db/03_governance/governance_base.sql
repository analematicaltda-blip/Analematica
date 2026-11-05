CREATE TABLE IF NOT EXISTS governance.administrative_acts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    act_name TEXT NOT NULL, act_type TEXT,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);
