-- =============================================================================
-- SARITA SOVEREIGN OS - SECURITY NUCLEUS
-- Domain: Security Infrastructure & Context Management
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS security;

-- Extension for forensic hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Function to retrieve the current tenant_id from session context
CREATE OR REPLACE FUNCTION security.fn_get_tenant_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.tenant_id', true), '')::UUID;
EXCEPTION
    WHEN OTHERS THEN RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to retrieve the current trace_id from session context
CREATE OR REPLACE FUNCTION security.fn_get_trace_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.trace_id', true), '')::UUID;
EXCEPTION
    WHEN OTHERS THEN RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to retrieve the current context_id from session context
CREATE OR REPLACE FUNCTION security.fn_get_context_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.context_id', true), '')::UUID;
EXCEPTION
    WHEN OTHERS THEN RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to retrieve the current agent_id from session context
CREATE OR REPLACE FUNCTION security.fn_get_agent_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.agent_id', true), '')::UUID;
EXCEPTION
    WHEN OTHERS THEN RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON SCHEMA security IS 'Sovereign security nucleus for RLS and context enforcement';
