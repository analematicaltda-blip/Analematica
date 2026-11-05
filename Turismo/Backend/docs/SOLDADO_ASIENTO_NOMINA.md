# SOLDADO: GENERAR ASIENTO NÓMINA (N6 ORO V2) — SARITA 2026

## 🎯 Responsabilidad (Bloque V)
Transformar el evento `NominaProcesada` en un asiento contable compuesto de doble partida. Es el ejecutor final de la verdad financiera laboral.

## 🏗️ Especificación Técnica

| Atributo | Valor |
| :--- | :--- |
| **Clase** | `GenerarAsientoNominaSoldado` |
| **Dominio** | `contabilidad` |
| **Agregado Raíz** | `AsientoContable` |
| **Permisos** | `['contabilidad.generar.nomina']` |
| **Idempotencia** | `True` (Key: `nominaId + version + tenant`) |
| **Outbox** | `True` (Event: `AsientoNominaGenerado`) |

## 🔄 Lógica de Ejecución Atómica

1.  **Validación de Periodo:** Verificar que el periodo contable asociado a la `fechaPago` esté `OPEN`.
2.  **Consulta de Mapeo:** Cargar los mapeos de `PayrollAccountingMap` para todos los conceptos recibidos.
3.  **Construcción de Líneas:**
    - Generar líneas de Débito (Gasto) agrupadas por centro de costo.
    - Generar líneas de Crédito (Obligaciones/Bancos) por cada tipo de descuento y pago neto.
4.  **Validación de Partida Doble:** `if abs(TotalDébito - TotalCrédito) > 0.001 raise UnbalancedPayrollError`.
5.  **Persistencia:** Guardar `JournalEntry` con el `hashOrigen` de la nómina para trazabilidad forense.

---
**Garantía:** Si el mapeo falla para un solo concepto, el soldado aborta la operación completa, manteniendo la contabilidad limpia.
