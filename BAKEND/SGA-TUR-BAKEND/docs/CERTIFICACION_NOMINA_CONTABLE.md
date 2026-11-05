# MATRIZ DE CERTIFICACIÓN NÓMINA-CONTABLE — SARITA 2026

## 🧪 Bloque XIV: Batería de Pruebas Obligatorias
El sistema de sincronización debe superar el 100% de estos tests para obtener el sello **READY**:

| ID | Escenario | Resultado Esperado |
| :--- | :--- | :--- |
| **TN-01** | Liquidación Exitosa | Generación de asiento con 4 líneas (Gasto, Provisión, SS, Banco). |
| **TN-02** | Reintento de Evento | Cero duplicados en el Libro Diario (Idempotencia). |
| **TN-03** | Periodo Contable Cerrado | Bloqueo de asiento y marca de 'PENDING' en el evento. |
| **TN-04** | Error de Mapeo | Aborto de transacción y notificación al Admin por falta de cuenta. |
| **TN-05** | Multi-tenant Safe | Tenant A no puede disparar la nómina del Tenant B. |
| **TN-06** | Reversión Total | Generación de asiento inverso post-anulación. |

## 📈 Bloque XIII: Métricas de Operatividad
La Torre de Control expondrá en tiempo real:
- `% Conciliación Automática:` (Asientos Generados / Nóminas Procesadas) * 100.
- `Eventos en Outbox:` Conteo de señales de nómina pendientes de envío.
- `Latencia Contable:` Tiempo promedio entre el cierre de nómina y el posteo del asiento.

---
**Criterio de Éxito:** Se considera un sistema 100% cerrado cuando no exista un solo pago de nómina en el banco que no tenga un rastro contable inmutable asociado.
