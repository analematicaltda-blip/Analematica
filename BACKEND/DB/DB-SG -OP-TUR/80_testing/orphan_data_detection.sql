-- sarita_db/80_testing/orphan_data_detection.sql
-- Detección de datos huérfanos y violaciones de integridad referencial lógica

-- 1. Registros sin tenant válido (que no existen en core.tenants)
-- Nota: Esto asume que core.tenants es la tabla maestra.
-- Este script debe adaptarse a cada tabla, aquí se muestra un ejemplo genérico.

-- Ejemplo para finance.payment_intents
SELECT 'finance.payment_intents' as table_name, count(*) as orphans
FROM finance.payment_intents p
LEFT JOIN core.tenants t ON p.tenant_id = t.id
WHERE t.id IS NULL;

-- 2. Relaciones rotas en Ledger
SELECT 'ledger.ledger_entries' as table_name, count(*) as broken_links
FROM finance.ledger_entries le
LEFT JOIN finance.ledger_transactions lt ON le.transaction_id = lt.id
WHERE lt.id IS NULL;

-- 3. Bookings sin Turista válido
SELECT 'tourism.booking_reservations' as table_name, count(*) as broken_links
FROM tourism.booking_reservations br
LEFT JOIN tourism.tourist_profiles tp ON br.tourist_id = tp.id
WHERE tp.id IS NULL;
