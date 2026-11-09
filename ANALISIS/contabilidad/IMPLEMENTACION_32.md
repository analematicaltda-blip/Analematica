# Implementación 32 · Exactitud monetaria independiente del contexto

**Avance: 36,11 % (26/72 hitos).** Se corrige y verifica ACC-008, ya puntuado. No se acredita otro hito.

## Corrección funcional

El contrato de solicitud fiscal sumaba Decimal bajo el contexto global de Python. Una dependencia que redujera su precisión podía redondear los totales o activar excepciones aun con entradas válidas. Ahora transforma las cadenas monetarias validadas en centavos enteros, acumula enteros y formatea por división/resto. Ninguna operación depende de floats, redondeos o del contexto decimal global.

Conserva el contrato de dos decimales y sus límites: no amplía monedas ni cambia las reglas tributarias. Para entradas previamente exactas, los payloads y claves conservan su representación; no se migran requests históricos. Si existieran requests generados bajo un contexto decimal alterado, deberán diagnosticarse y reconciliarse expresamente; no se sobrescriben automáticamente.

## Evidencia

145 métodos Python aprobados en nueve suites. Tres pruebas nuevas verifican precisión decimal global de 2 dígitos con traps Inexact/Rounded activos, 100 componentes monetarios máximos y digest estable al invertir el orden de los componentes. El bruto máximo del caso probado es `100000000000000.00`, exacto. Las pruebas del outbox siguen aprobadas.

Evidencia: `evidencias/implementacion-32.json`. Fuente estable. PostgreSQL no se repitió: no cambiaron transacciones, esquema, consultas o bloqueo.

## Hallazgo de integración comercial

La revisión de `apps/domain_business/operativa/models.py` y `apps/turismo/models/provider_models.py` encontró reservas con estado y total, pero sin revisión fiscal ni desglose tributario normativo suficiente para construir el contrato. No se ha convertido ese total en neto ni supuesto IVA/exención. El servicio `ReservationApplicationService` también contiene un fallback `SIM-123` y llama a una creación ausente en el adaptador `SargentoReservas` inspeccionado; no es una fuente confiable de emisión hasta corregir y probar su recorrido real.

Antes de conectarlo: identificar el flujo de reservas canónico utilizado, conservar sus dependencias, incorporar revisión/desglose tributario persistentes y autorizados, bloquear estado y empresa bajo la misma transacción, y verificar titularidad mediante vínculo vigente. Después integrar el productor al outbox y validar consumidor fiscal. Esta entrega no modifica ese flujo ni expone solicitudes basadas en snapshots arbitrarios.

Los criterios restantes de la matriz, incluyendo integración corporativa Analemática, siguen pendientes. Sin cambios de datos del usuario, commit, push o despliegue.
