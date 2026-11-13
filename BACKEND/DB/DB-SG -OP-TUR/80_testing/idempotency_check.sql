-- sarita_db/80_testing/idempotency_check.sql
-- Validación de idempotencia y detección de duplicados por trace_id

-- 1. Duplicados en Pagos por trace_id
SELECT
    trace_id,
    COUNT(*) as occurrences
FROM finance.payment_intents
GROUP BY trace_id
HAVING COUNT(*) > 1;

-- 2. Duplicados en Event Store por trace_id (si aplica unicidad lógica)
SELECT
    trace_id,
    event_type,
    COUNT(*) as occurrences
FROM events.event_store
GROUP BY trace_id, event_type
HAVING COUNT(*) > 1;
