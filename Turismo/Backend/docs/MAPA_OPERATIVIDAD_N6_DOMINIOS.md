# MAPA DE OPERATIVIDAD POR DOMINIO — SARITA 2026

## 🎯 Objetivo (Bloque 2)
Dotar a cada dominio de "Soldados Reales" capaces de modificar el estado persistente y asegurar la integridad financiera y operativa.

## 🧾 1. Dominio Contable
- **SoldadoRegistroIngreso:** Escribe directamente en el `LedgerEngine`. Valida que el débito a CxC iguale al crédito en Ingresos + IVA.
- **SoldadoCierreParcial:** Bloquea el periodo contable para que ningún otro soldado pueda escribir en esa fecha.
- **Evento:** `ACCOUNTING_ENTRY_CREATED`.

## 💰 2. Dominio Financiero
- **SoldadoRegistroCredito:** Crea un cronograma de pagos persistente (`PaymentSchedule`). Genera los asientos de causación inicial de la deuda.
- **SoldadoAlertaSobrecosto:** No solo informa; bloquea la creación de nuevas órdenes de compra si el presupuesto del rubro se ha agotado.
- **Evento:** `CREDIT_SCHEDULE_ESTABLISHED`.

## 👥 3. Dominio Nómina
- **SoldadoLiquidacion:** Crea el registro `PayrollRecord` por empleado. Dispara el asiento de gasto salarial (Cuenta 5) y el pasivo prestacional (Cuenta 2).
- **Evento:** `PAYROLL_LINE_COMMITTED`.

## 🏥 4. Dominio SST (Seguridad y Salud)
- **SoldadoIncidentes:** Crea un registro en `IncidentRecord`. Adjunta evidencia digital (hash) y notifica al dominio de Gobierno para supervisión inmediata.
- **Evento:** `SAFETY_INCIDENT_FILED`.

## 🌍 5. Dominio Turista
- **SoldadoGestorReservas:** Crea el modelo `Reservation`. Valida disponibilidad real en el módulo operativo. Genera el anticipo contable si aplica pago parcial.
- **Evento:** `RESERVATION_CONFIRMED`.

## 🛍️ 6. Dominio Artesanos
- **SoldadoRegistroInventario:** Modifica el `InventoryLevel`. Valida contra stock negativo. Sincroniza con el catálogo de ventas.
- **Evento:** `STOCK_MUTATION_EXECUTED`.

---
**Regla de Cierre:** No se permite el despliegue de ningún dominio que posea un soldado en estado "Mock" o "Informativo".
