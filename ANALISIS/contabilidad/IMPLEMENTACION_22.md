# Implementación 22 · Contrapartida multimoneda neutra a valoración histórica

**Avance: 27,78 % (20/72 hitos).** Refuerza ACC-004/006, ya puntuados por incremento y pruebas; no cierra su aceptación completa.

## Comportamiento

El núcleo compartido permite revertir exactamente un asiento multimoneda v2 contabilizado. La contrapartida conserva moneda de transacción, moneda base, tasa registrada e importes base originales, invirtiendo cada débito/crédito en la misma cuenta. No solicita ni aplica una cotización nueva y no reconoce diferencias en cambio automáticamente.

Antes de contabilizar se comprueban hash del original, empresa, monedas, valoración original y correspondencia completa de líneas. No permite omitir/agregar líneas, cambiar cuentas/importes o registrar una segunda contrapartida contabilizada. Continúan las comprobaciones de actor activo, cuentas activas, periodo actual abierto, fecha y moneda base vigente. El original no se modifica.

La contrapartida recibe su propio asiento, hash, auditoría y outbox en la transacción existente. La serialización empresarial conserva el rechazo de duplicados concurrentes. El consumidor local proyecta sus importes base históricos y el informe se neutraliza respecto del asiento original.

No es una liquidación bancaria, devolución parcial, revaluación o ajuste fiscal. No se invierte el valor económico usando la tasa de hoy: se cancela contablemente el registro original. Una diferencia en cambio o un ajuste requiere otro flujo explícito revisado.

## Verificación

115 métodos Python y 19 escenarios contables PostgreSQL aprobados. Casos nuevos:

- Tasa original 4000 y cotización posterior 4500: contrapartida a 4000, importes base originales, hash original intacto e informe neto cero.
- Se impide solicitar nueva cotización durante la reversión y se rechaza la segunda contrapartida.
- Líneas alteradas no contabilizan; periodo actual cerrado revierte toda la creación de la contrapartida.
- Carrera PostgreSQL entre dos solicitudes: una sola contrapartida contabilizada, con valoración histórica.
- Proceso autenticado con rol DML restringido: posteo USD fechado antes de la nueva cotización, contrapartida histórica, informe y proyección local válidos.
- El ensayo posterior de dump/restore conserva estos registros, sus controles y la integridad.

Evidencia: `evidencias/implementacion-22.json`. No se requieren cambios de esquema.

## Límites

Reversión extranjera limitada a originales v2 verificados. Legados, cuentas inactivas, moneda base empresarial cambiada, valoración inconsistente o periodo no disponible requieren conciliación/proceso autorizado; no se sortean esos controles. No se implementan diferencias de cambio, pagos/refund externos, parciales ni aprobación fiscal de un caso real. Continúan la trazabilidad/cualificación de fuentes FX y validación profesional, interfaces y demás pools. Sin cambios de datos del usuario, commit o push.
