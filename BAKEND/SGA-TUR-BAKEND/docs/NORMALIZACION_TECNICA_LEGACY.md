# NORMALIZACIÓN TÉCNICA Y DICCIONARIO LEGACY — SARITA 2026

## 🎯 Objetivo (Bloque 17)
Eliminar la deuda técnica semántica. El lenguaje técnico oficial de Sarita es el **Inglés Técnico**. Se prohíbe la mezcla de idiomas en nombres de clases, modelos y campos.

## 📖 Diccionario de Normalización (Vía 2)

| Término Legacy (ES) | Término Estándar (EN) | Dominio |
| :--- | :--- | :--- |
| `PlanDeCuentas` | `ChartOfAccounts` | Contabilidad |
| `AsientoContable` | `JournalEntry` | Contabilidad |
| `FacturaVenta` | `SalesInvoice` | Comercial |
| `ReciboCaja` | `Receipt` | Financiero |
| `PlanillaNomina` | `Payroll` | Laboral |
| `Almacen` | `Warehouse` | Inventario |

## 🛠️ Regla 1:1 de Hooks Frontend (Bloque 16)
Cada método en el frontend (Next.js) debe estar respaldado por un contrato OpenAPI real:

- **Hook:** `getFinancialReport()`
- **Backend:** `GET /api/v1/accounting/reports/`
- **Estado:** ❌ Mock Prohibido en Producción.

## 🔄 Proceso de Migración Semántica
1.  **Aliasing:** Se mantendrán las clases en español como aliases (herencia o variable) marcadas como `@deprecated`.
2.  **Referenciación:** Todas las nuevas integraciones deben usar exclusivamente el término en inglés.
3.  **Cierre:** Tras 6 meses, se eliminarán los archivos legacy.

---
**Resultado:** Un código limpio, profesional y preparado para la auditoría de ingenieros globales.
