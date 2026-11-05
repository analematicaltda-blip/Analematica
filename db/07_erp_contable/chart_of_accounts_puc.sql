-- ==============================================================================
-- db/07_erp_contable/chart_of_accounts_puc.sql
-- Módulo Contable Maestro: Plan Único de Cuentas (PUC) & Integración Multimódulo
-- ==============================================================================

CREATE TABLE IF NOT EXISTS erp.chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(30) NOT NULL CHECK (account_type IN (
        'ASSET',            -- 1: Activos
        'LIABILITY',        -- 2: Pasivos
        'EQUITY',           -- 3: Patrimonio
        'REVENUE',          -- 4: Ingresos
        'EXPENSE',          -- 5: Gastos
        'COST_OF_SALES',    -- 6: Costos de Ventas
        'PRODUCTION_COST',  -- 7: Costos de Producción
        'DEBTOR_ORDER',     -- 8: Cuentas de Orden Deudoras
        'CREDITOR_ORDER'    -- 9: Cuentas de Orden Acreedoras
    )),
    nature VARCHAR(10) NOT NULL CHECK (nature IN ('DEBITO', 'CREDITO')),
    level INTEGER NOT NULL, -- 1=Clase, 2=Grupo, 4=Cuenta, 6=Subcuenta, >=8=Auxiliar
    parent_code VARCHAR(20),
    allows_movement BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT,
    CONSTRAINT uq_puc_tenant_code UNIQUE (tenant_id, code)
);

CREATE TABLE IF NOT EXISTS erp.tax_rules_and_retentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept VARCHAR(100) NOT NULL, -- 'IVA_VENTAS', 'IVA_DESCONTABLE', 'RETEFUENTE_SERVICIOS', 'RETEICA', 'IMPUESTO_RENTA'
    rate_percentage NUMERIC(5, 2) NOT NULL,
    base_minima NUMERIC(18, 2) DEFAULT 0.00,
    credit_account_code VARCHAR(20) NOT NULL,
    debit_account_code VARCHAR(20) NOT NULL,
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT
);

-- Tabla de Enlace Cruzado Multimódulo (Ventas, Archivo, Finanzas, Operativo -> Contabilidad)
CREATE TABLE IF NOT EXISTS erp.accounting_module_bridges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_module VARCHAR(50) NOT NULL CHECK (origin_module IN ('VENTAS', 'ARCHIVO', 'FINANZAS', 'OPERATIVO', 'TURISMO')),
    origin_reference_id UUID NOT NULL,
    origin_document_type VARCHAR(50) NOT NULL,
    journal_entry_id UUID NOT NULL,
    status VARCHAR(20) DEFAULT 'POSTED',
    tenant_id UUID NOT NULL,
    trace_id UUID NOT NULL,
    context_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hash_integridad TEXT,
    CONSTRAINT uq_origin_bridge UNIQUE (tenant_id, origin_module, origin_reference_id)
);
