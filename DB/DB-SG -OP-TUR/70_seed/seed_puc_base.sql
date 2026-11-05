-- ==============================================================================
-- db/70_seed/seed_puc_base.sql
-- Inserción de Cuentas PUC Esenciales (Ingresos, Gastos, Activos, Pasivos, Retenciones, Renta, IVA)
-- ==============================================================================

-- 1. Activos
INSERT INTO erp.chart_of_accounts (code, name, account_type, nature, level, parent_code, allows_movement, tenant_id, trace_id, context_id)
VALUES
('1', 'ACTIVO', 'ASSET', 'DEBITO', 1, NULL, false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('11', 'DISPONIBLE', 'ASSET', 'DEBITO', 2, '1', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('1105', 'CAJA', 'ASSET', 'DEBITO', 4, '11', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('110505', 'Caja General', 'ASSET', 'DEBITO', 6, '1105', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('1110', 'BANCOS', 'ASSET', 'DEBITO', 4, '11', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('111005', 'Moneda Nacional - Bancos', 'ASSET', 'DEBITO', 6, '1110', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('13', 'DEUDORES', 'ASSET', 'DEBITO', 2, '1', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('1305', 'CLIENTES NACIONALES', 'ASSET', 'DEBITO', 4, '13', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('130505', 'Clientes Nacionales - Ventas y Servicios', 'ASSET', 'DEBITO', 6, '1305', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('1355', 'ANTICIPO DE IMPUESTOS Y SALDOS A FAVOR', 'ASSET', 'DEBITO', 4, '13', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('135515', 'Retención en la Fuente a Favor', 'ASSET', 'DEBITO', 6, '1355', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('135518', 'Impuesto de Industria y Comercio Retenido', 'ASSET', 'DEBITO', 6, '1355', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('14', 'INVENTARIOS', 'ASSET', 'DEBITO', 2, '1', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('1435', 'MERCANCIAS NO FABRICADAS POR LA EMPRESA', 'ASSET', 'DEBITO', 4, '14', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('15', 'PROPIEDADES, PLANTA Y EQUIPO', 'ASSET', 'DEBITO', 2, '1', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('1592', 'DEPRECIACION ACUMULADA', 'ASSET', 'CREDITO', 4, '15', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid())
ON CONFLICT (tenant_id, code) DO NOTHING;

-- 2. Pasivos
INSERT INTO erp.chart_of_accounts (code, name, account_type, nature, level, parent_code, allows_movement, tenant_id, trace_id, context_id)
VALUES
('2', 'PASIVO', 'LIABILITY', 'CREDITO', 1, NULL, false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('22', 'PROVEEDORES', 'LIABILITY', 'CREDITO', 2, '2', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('2205', 'PROVEEDORES NACIONALES', 'LIABILITY', 'CREDITO', 4, '22', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('220505', 'Proveedores Compras y Operaciones', 'LIABILITY', 'CREDITO', 6, '2205', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('23', 'CUENTAS POR PAGAR', 'LIABILITY', 'CREDITO', 2, '2', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('2365', 'RETENCION EN LA FUENTE', 'LIABILITY', 'CREDITO', 4, '23', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('236540', 'Retención Compras Generales (2.5%)', 'LIABILITY', 'CREDITO', 6, '2365', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('236525', 'Retención Servicios (4%)', 'LIABILITY', 'CREDITO', 6, '2365', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('24', 'IMPUESTOS, GRAVAMENES Y TASAS', 'LIABILITY', 'CREDITO', 2, '2', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('2404', 'DE RENTA Y COMPLEMENTARIOS', 'LIABILITY', 'CREDITO', 4, '24', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('240405', 'Impuesto sobre la Renta Corriente (35%)', 'LIABILITY', 'CREDITO', 6, '2404', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('2408', 'IMPUESTO SOBRE LAS VENTAS POR PAGAR (IVA)', 'LIABILITY', 'CREDITO', 4, '24', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('240801', 'IVA Generado en Ventas (19%)', 'LIABILITY', 'CREDITO', 6, '2408', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('240802', 'IVA Descontable en Compras (19%)', 'LIABILITY', 'DEBITO', 6, '2408', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('25', 'OBLIGACIONES LABORALES (NOMINA)', 'LIABILITY', 'CREDITO', 2, '2', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('2505', 'SALARIOS POR PAGAR', 'LIABILITY', 'CREDITO', 4, '25', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid())
ON CONFLICT (tenant_id, code) DO NOTHING;

-- 3. Patrimonio
INSERT INTO erp.chart_of_accounts (code, name, account_type, nature, level, parent_code, allows_movement, tenant_id, trace_id, context_id)
VALUES
('3', 'PATRIMONIO', 'EQUITY', 'CREDITO', 1, NULL, false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('31', 'CAPITAL SOCIAL', 'EQUITY', 'CREDITO', 2, '3', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('3115', 'APORTES SOCIALES', 'EQUITY', 'CREDITO', 4, '31', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('36', 'RESULTADOS DEL EJERCICIO', 'EQUITY', 'CREDITO', 2, '3', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('3605', 'UTILIDAD DEL EJERCICIO', 'EQUITY', 'CREDITO', 4, '36', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid())
ON CONFLICT (tenant_id, code) DO NOTHING;

-- 4. Ingresos
INSERT INTO erp.chart_of_accounts (code, name, account_type, nature, level, parent_code, allows_movement, tenant_id, trace_id, context_id)
VALUES
('4', 'INGRESOS', 'REVENUE', 'CREDITO', 1, NULL, false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('41', 'OPERACIONALES', 'REVENUE', 'CREDITO', 2, '4', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('4135', 'COMERCIO AL POR MAYOR Y AL POR MENOR', 'REVENUE', 'CREDITO', 4, '41', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('413505', 'Ingresos por Venta de Bienes', 'REVENUE', 'CREDITO', 6, '4135', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('4140', 'HOTELES Y RESTAURANTES (SERVICIOS TURISTICOS)', 'REVENUE', 'CREDITO', 4, '41', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('414005', 'Ingresos Alojamiento y Hospedaje', 'REVENUE', 'CREDITO', 6, '4140', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('414010', 'Ingresos Alimentos y Bebidas (Restaurantes)', 'REVENUE', 'CREDITO', 6, '4140', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('414015', 'Ingresos Tours y Ecoturismo', 'REVENUE', 'CREDITO', 6, '4140', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid())
ON CONFLICT (tenant_id, code) DO NOTHING;

-- 5. Gastos
INSERT INTO erp.chart_of_accounts (code, name, account_type, nature, level, parent_code, allows_movement, tenant_id, trace_id, context_id)
VALUES
('5', 'GASTOS', 'EXPENSE', 'DEBITO', 1, NULL, false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('51', 'OPERACIONALES DE ADMINISTRACION', 'EXPENSE', 'DEBITO', 2, '5', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('5105', 'GASTOS DE PERSONAL (NOMINA)', 'EXPENSE', 'DEBITO', 4, '51', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('510506', 'Sueldos y Salarios', 'EXPENSE', 'DEBITO', 6, '5105', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('5115', 'IMPUESTOS', 'EXPENSE', 'DEBITO', 4, '51', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('511505', 'Industria y Comercio', 'EXPENSE', 'DEBITO', 6, '5115', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('5160', 'DEPRECIACIONES', 'EXPENSE', 'DEBITO', 4, '51', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('52', 'OPERACIONALES DE VENTAS', 'EXPENSE', 'DEBITO', 2, '5', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('54', 'IMPUESTO DE RENTA Y COMPLEMENTARIOS', 'EXPENSE', 'DEBITO', 2, '5', false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('5405', 'IMPUESTO DE RENTA Y COMPLEMENTARIOS', 'EXPENSE', 'DEBITO', 4, '54', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('6', 'COSTOS DE VENTAS', 'COST_OF_SALES', 'DEBITO', 1, NULL, false, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid()),
('6135', 'COSTO DE VENTAS - MERCANCIAS', 'COST_OF_SALES', 'DEBITO', 4, '6', true, '00000000-0000-0000-0000-000000000001', gen_random_uuid(), gen_random_uuid())
ON CONFLICT (tenant_id, code) DO NOTHING;
