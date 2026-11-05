# EVENTO CANÓNICO DE NÓMINA — SARITA 2026

## 📜 Propósito (Bloque III)
Garantizar que la información de nómina viaje de forma íntegra e inmutable hacia el dominio contable. El evento actúa como el "contrato de verdad" entre RRHH y Finanzas.

## 🏗️ Esquema JSON Obligatorio `NominaProcesada`

```json
{
  "event_id": "UUID-V4",
  "event_name": "NominaProcesada",
  "tenantId": "UUID",
  "nominaId": "UUID",
  "periodo": "2026-03",
  "fechaPago": "2026-03-31",
  "totalBruto": 5000000.00,
  "totalDeducciones": 400000.00,
  "totalNeto": 4600000.00,
  "centroCosto": "ADMIN-01",
  "empleados": [
    {
      "terceroId": "UUID",
      "neto": 2300000.00,
      "conceptos": [
        {"codigo": "SALARIO_BASE", "monto": 2500000.00},
        {"codigo": "DED_SALUD", "monto": 100000.00}
      ]
    }
  ],
  "version": 1,
  "hashIntegridad": "SHA256-SIGNATURE",
  "correlation_id": "UUID",
  "timestamp": "ISO-8601"
}
```

## 🔒 Reglas de Emisión (Integridad Total)
1.  **Transaccionalidad:** El evento DEBE insertarse en la tabla `OutboxEvent` en la misma transacción que marca la nómina como `PROCESADA`.
2.  **Cierre de Edición:** Una vez emitido el evento, el registro de nómina en RRHH queda **bloqueado para edición**.
3.  **Hash Origen:** El `hashIntegridad` debe calcularse sobre el payload completo de empleados para evitar alteraciones en el tránsito.

---
**Resultado:** Cero pérdida de datos entre la liquidación laboral y el reflejo en el balance.
