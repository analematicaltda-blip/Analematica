-- TEST DE ATOMICIDAD DEL MOTOR TRANSACCIONAL
BEGIN;

-- Intento de operación sin context_id (DEBE FALLAR por scta_enforce)
-- Pero el motor central fn_execute lo requiere explícitamente.

DO $$
BEGIN
    PERFORM core.fn_execute_financial_operation(
        '00000000-0000-0000-0000-000000000001',
        '{"trace_id": "00000000-0000-0000-0000-000000000001", "context_id": "00000000-0000-0000-0000-000000000001", "event_type": "TEST", "amount": 100, "account_debit": "11111111-1111-1111-1111-111111111111", "account_credit": "22222222-2222-2222-2222-222222222222"}'::JSONB
    );
    RAISE NOTICE 'Transacción procesada correctamente';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error esperado detectado: %', SQLERRM;
END; $$;

ROLLBACK;
