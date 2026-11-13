-- sarita_db/80_testing/financial_consistency_check.sql
-- Validación de consistencia financiera y partida doble

-- 1. Balance contable total por trace_id (debe ser 0)
SELECT
    trace_id,
    SUM(debit) as total_debit,
    SUM(credit) as total_credit,
    SUM(debit) - SUM(credit) as imbalance
FROM finance.ledger_entries
GROUP BY trace_id
HAVING SUM(debit) - SUM(credit) != 0;

-- 2. Correspondencia payments <-> ledger_entries
-- Todo pago exitoso debe tener su asiento en el ledger
SELECT
    p.id as payment_id,
    p.amount,
    COALESCE(SUM(le.debit), 0) as ledger_amount
FROM finance.payment_intents p
LEFT JOIN finance.ledger_entries le ON p.trace_id = le.trace_id AND le.debit > 0
WHERE p.status = 'SUCCEEDED'
GROUP BY p.id, p.amount
HAVING p.amount != COALESCE(SUM(le.debit), 0);

-- 3. Saldos negativos ilegales en wallets
SELECT
    user_id,
    balance
FROM finance.wallets
WHERE balance < 0;
