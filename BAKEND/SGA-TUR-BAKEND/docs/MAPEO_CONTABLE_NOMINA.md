# MAPEO CONTABLE DE NÓMINA — SARITA 2026

## 🎯 Objetivo (Bloque IV)
Establecer la tabla parametrizada que traduce cada concepto de nómina en su impacto contable correspondiente (Débito/Crédito). Esto garantiza que la integración sea determinística y no dependa de lógica cableada.

## 🏗️ Estructura del Modelo `PayrollAccountingMap`

| Campo | Tipo | Propósito | Ejemplo |
| :--- | :--- | :--- | :--- |
| `payroll_concept` | String | Código del concepto salarial. | `SALARIO_BASE` |
| `debit_account` | String (Code) | Cuenta para el gasto. | `510506` (Sueldos) |
| `credit_account` | String (Code) | Cuenta para la obligación. | `250505` (Sueldos x Pagar) |
| `cost_center_required`| Boolean | Si requiere asignar centro de costo. | `True` |
| `third_party_required`| Boolean | Si requiere asignar ID de tercero. | `True` |

## 📝 Configuración Estándar (Vía 2)

| Concepto | Débito | Crédito | Descripción |
| :--- | :--- | :--- | :--- |
| **Salario Base** | 510506 (Gasto) | 250505 (CxP Sueldos) | Causación de sueldos. |
| **Seguridad Social** | 510569 (Gasto) | 237005 (Obligaciones SS) | Aporte patronal. |
| **Deducción Salud** | 250505 (CxP Sueldos) | 237005 (Aportes Salud) | Retención al empleado. |
| **Pago Neto** | 250505 (CxP Sueldos) | 111005 (Bancos) | Desembolso de nómina. |

---
**Regla de Oro:** Sin un mapeo activo para el `payroll_concept`, el `GenerarAsientoNominaSoldado` disparará un error fatal y detendrá la sincronización para ese Tenant.
