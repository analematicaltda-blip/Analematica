# REGLAS DE SINCRONIZACIÓN INVENTARIO ↔ CONTABILIDAD — SARITA 2026

## 📜 Propósito (Bloque V)
Definir el comportamiento del `LedgerEngine` ante cada tipo de movimiento de stock. La contabilidad es el reflejo inmutable de la realidad física de las bodegas.

## 🔄 1. Recepción de Compra (Entrada)
- **Físico:** Aumenta stock.
- **Contable:**
    - **Débito:** Cuenta Inventario (14xx) - Valorización del activo.
    - **Crédito:** Cuenta x Pagar Proveedores (22xx) - Reconocimiento de deuda.

## 🔄 2. Consumo / Venta (Salida)
- **Físico:** Disminuye stock.
- **Contable:**
    - **Débito:** Costo de Ventas (6xxx) - Realización del gasto.
    - **Crédito:** Cuenta Inventario (14xx) - Descargue del activo.
- **Valoración:** Se aplicará **Promedio Ponderado** de forma predeterminada para el cálculo del costo.

## 🔄 3. Ajuste de Inventario (Mermas/Sobrantes)
- **Sobrante (+):**
    - **Débito:** Inventario (14xx).
    - **Crédito:** Ajustes / Otros Ingresos (42xx).
- **Faltante (-):**
    - **Débito:** Ajustes / Gasto Mermas (51xx).
    - **Crédito:** Inventario (14xx).

## 🔄 4. Transferencia entre Bodegas
- **Físico:** Mueve de Bodega A a Bodega B.
- **Contable:**
    - **Crédito:** Inventario Bodega Origen.
    - **Débito:** Inventario Bodega Destino.
- **Nota:** El impacto neto en el estado de resultados es **Cero**.

---
**Regla de Trazabilidad:** Todo asiento contable generado por estas reglas debe guardar el `inventory_movement_id` en el campo `reference` del Ledger.
