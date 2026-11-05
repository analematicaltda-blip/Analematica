-- Simulación de ataques (Entregables 990)
-- 1. Identity
SELECT * FROM tourism.tourist_profiles WHERE tenant_id != current_setting('app.current_tenant')::UUID;
-- 2. Financial
INSERT INTO finance.payment_intents (id, tenant_id, trace_id, context_id, amount) VALUES (gen_random_uuid(), '0', '0', '0', 100);
