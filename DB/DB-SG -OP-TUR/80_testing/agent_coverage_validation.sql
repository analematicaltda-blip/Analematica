-- sarita_db/80_testing/agent_coverage_validation.sql
-- Validación de cobertura de agentes (SCTA)

-- Verificar que eventos en tablas críticas tengan registros correspondientes en SCTA
SELECT
    'tourism.booking_reservations' as source_table,
    count(br.id) as total_records,
    count(ae.id) as covered_by_agent
FROM tourism.booking_reservations br
LEFT JOIN ai_core.agent_executions ae ON br.context_id = ae.context_id
HAVING count(br.id) > count(ae.id);

SELECT
    'finance.payment_intents' as source_table,
    count(p.id) as total_records,
    count(ae.id) as covered_by_agent
FROM finance.payment_intents p
LEFT JOIN ai_core.agent_executions ae ON p.context_id = ae.context_id
HAVING count(p.id) > count(ae.id);
