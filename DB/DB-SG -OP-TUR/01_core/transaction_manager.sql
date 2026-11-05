-- SARITA UNIFIED TRANSACTION MANAGER
-- Version: 1.2 (Production Hardened)

CREATE OR REPLACE FUNCTION core.fn_execute_financial_operation(
    p_operation_type TEXT,
    p_amount DECIMAL,
    p_source_account_id UUID,
    p_dest_account_id UUID,
    p_tenant_id UUID,
    p_trace_id UUID,
    p_context_id UUID
) RETURNS UUID AS $$
DECLARE
    v_transaction_id UUID;
BEGIN
    -- 1. Insert into Transaction Header (atomic check)
    INSERT INTO finance.transactions (
        amount, operation_type, tenant_id, trace_id, context_id, status
    ) VALUES (
        p_amount, p_operation_type, p_tenant_id, p_trace_id, p_context_id, 'COMPLETED'
    ) RETURNING id INTO v_transaction_id;

    -- 2. Insert into Ledger Entries (Double Entry Enforcement)
    -- Debit Entry
    INSERT INTO finance.ledger_entries (
        transaction_id, account_id, entry_type, amount, tenant_id, trace_id, context_id
    ) VALUES (
        v_transaction_id, p_source_account_id, 'DEBIT', p_amount, p_tenant_id, p_trace_id, p_context_id
    );

    -- Credit Entry
    INSERT INTO finance.ledger_entries (
        transaction_id, account_id, entry_type, amount, tenant_id, trace_id, context_id
    ) VALUES (
        v_transaction_id, p_dest_account_id, 'CREDIT', p_amount, p_tenant_id, p_trace_id, p_context_id
    );

    -- 3. Sync with Immutable Event Store for AI Governance
    INSERT INTO core.event_store (
        entity_type, entity_id, operation, new_data, tenant_id, trace_id, context_id
    ) VALUES (
        'FINANCIAL_TRANSACTION', v_transaction_id, 'EXECUTE',
        json_build_object('amount', p_amount, 'type', p_operation_type),
        p_tenant_id, p_trace_id, p_context_id
    );

    RETURN v_transaction_id;
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'SARITA TRANSACTION FAILURE: %', SQLERRM;
END; $$ LANGUAGE plpgsql;
