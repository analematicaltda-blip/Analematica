# MAPEO CONTABLE DE INVENTARIO — SARITA 2026

## 🎯 Objetivo (Bloque IV)
Garantizar que cada producto o categoría de inventario tenga una ruta contable definida. Sin esta parametrización, el sistema bloqueará cualquier movimiento de stock para evitar descuadres financieros.

## 🏗️ Estructura del Modelo `InventoryAccountingMap`

| Campo | Tipo | Propósito | Ejemplo |
| :--- | :--- | :--- | :--- |
| `product_id` | UUID | Vínculo con el Producto Unificado. | `UUID-P-01` |
| `inventory_account`| String | Cuenta del Activo (Inventario). | `143501` (Mercancías) |
| `cost_account` | String | Cuenta del Gasto (Costo de Venta).| `613501` (Costo Hotelería) |
| `adjustment_account`| String | Cuenta para ajustes +/-. | `519505` (Ajustes Invent.) |
| `loss_account` | String | Cuenta para mermas/pérdidas. | `519510` (Mermas) |
| `cost_center` | String | Centro de costo responsable. | `BODEGA-GAITAN` |

## 📝 Reglas de Validación Preventiva

1.  **Bloqueo por Parametrización:** Al intentar crear un `MovimientoInventario`, el sistema verificará la existencia de este mapa. Si el producto no tiene cuentas asignadas → `raise AccountingParameterError`.
2.  **Validación de Costo:** Se prohíben entradas con `costo = 0.00` salvo autorización del Super Admin (Donaciones/Muestras).
3.  **Aislamiento:** El mapeo es específico por `tenant_id`, permitiendo que el Hotel A y la Agencia B usen planes de cuentas distintos.

---
**Resultado:** Cada unidad de stock en la bodega tiene un reflejo monetario exacto en el balance general.
