# INTEGRACIÓN CONTABLE FISCAL — SARITA 2026

## 🎯 Objetivo (Bloque 6)
Garantizar que ningún impuesto sea calculado sin tener una ruta automática de registro en los libros legales. Esto elimina el riesgo de "impuestos volantes" que no impactan el balance.

## 🏗️ Modelo `TaxAccountMapping`

| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `tax_id` | FK | Referencia al impuesto configurado. |
| `debit_account` | String (Code) | Cuenta para el débito (Activo/Gasto). |
| `credit_account`| String (Code) | Cuenta para el crédito (Pasivo/Obligación).|

### 🔄 Flujo de Integración
1.  **Cálculo:** El `TaxEngine` determina el monto (ej: $19,000 IVA).
2.  **Puente:** El `TaxAccountingBridge` consulta el mapeo activo para el `tenant_id`.
3.  **Asiento:** Se generan las líneas contables automáticamente:
    - **Venta:** Débito CxC (1305), Crédito Ingresos (4135), **Crédito IVA (2408)**.
    - **Compra:** Débito Inventario (1435), **Débito IVA Descontable (2408)**, Crédito Proveedores (2205).

## 🔒 Regla de Hard Lock
El sistema rechazará cualquier factura o nómina si el `TaxEngine` detecta un impuesto aplicable que no posee un `TaxAccountMapping` activo. El error se reportará como `FiscalInconsistencyError`.

---
**Resultado:** Cero discrepancia entre el reporte fiscal y el balance contable.
