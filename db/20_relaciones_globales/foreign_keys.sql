-- 20_relaciones/foreign_keys.sql
-- ESTABILIZACIÓN INTEGRAL DE RELACIONES PRE-AUDITORÍA

-- [CORE & IDENTITY]
ALTER TABLE identity.users ADD CONSTRAINT fk_user_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);
ALTER TABLE identity.roles ADD CONSTRAINT fk_role_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);

-- [GOVERNANCE]
ALTER TABLE governance.administrative_acts ADD CONSTRAINT fk_act_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);

-- [TOURISM]
ALTER TABLE tourism.tourist_profiles ADD CONSTRAINT fk_tp_user FOREIGN KEY (user_id) REFERENCES identity.users(id);
ALTER TABLE tourism.tourist_profiles ADD CONSTRAINT fk_tp_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);
ALTER TABLE tourism.booking_reservations ADD CONSTRAINT fk_br_tourist FOREIGN KEY (tourist_id) REFERENCES tourism.tourist_profiles(id);
ALTER TABLE tourism.booking_reservations ADD CONSTRAINT fk_br_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);

-- [ERP]
ALTER TABLE erp.business_operations ADD CONSTRAINT fk_bo_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);

-- [FINANCE & LEDGER]
ALTER TABLE finance.payment_intents ADD CONSTRAINT fk_pay_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);
ALTER TABLE finance.wallets ADD CONSTRAINT fk_wallet_user FOREIGN KEY (user_id) REFERENCES identity.users(id);
ALTER TABLE finance.wallets ADD CONSTRAINT fk_wallet_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);
ALTER TABLE ledger.transactions ADD CONSTRAINT fk_trans_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);
ALTER TABLE ledger.ledger_entries ADD CONSTRAINT fk_le_trans FOREIGN KEY (transaction_id) REFERENCES ledger.transactions(id);
ALTER TABLE ledger.ledger_entries ADD CONSTRAINT fk_le_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);

-- [EVENTS]
ALTER TABLE events.event_store ADD CONSTRAINT fk_ev_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);

-- [AI CORE]
ALTER TABLE ai_core.agent_executions ADD CONSTRAINT fk_ae_agent FOREIGN KEY (agent_id) REFERENCES ai_core.agents_master(id);
ALTER TABLE ai_core.agent_executions ADD CONSTRAINT fk_ae_context FOREIGN KEY (context_id) REFERENCES ai_core.agent_context_universal(id);
ALTER TABLE ai_core.agent_executions ADD CONSTRAINT fk_ae_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);
ALTER TABLE ai_core.agent_memory_global ADD CONSTRAINT fk_am_agent FOREIGN KEY (agent_id) REFERENCES ai_core.agents_master(id);
ALTER TABLE ai_core.agent_memory_global ADD CONSTRAINT fk_am_tenant FOREIGN KEY (tenant_id) REFERENCES core.tenants(id);
