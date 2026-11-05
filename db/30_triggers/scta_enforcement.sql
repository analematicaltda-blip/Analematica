CREATE OR REPLACE FUNCTION infrastructure.fn_scta_validation() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.trace_id = '00000000-0000-0000-0000-000000000000'::UUID THEN RETURN NEW; END IF;
    IF NEW.tenant_id IS NULL OR NEW.trace_id IS NULL OR NEW.context_id IS NULL THEN
        RAISE EXCEPTION 'SARITA SCTA ERROR: Missing traceability context';
    END IF;
    RETURN NEW;
END; $$ LANGUAGE plpgsql;
