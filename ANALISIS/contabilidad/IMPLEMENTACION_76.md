# Implementación76 · Conciliación parcial y selección de coincidencias

Se amplió la conciliación bancaria existente en ERP y Analemática. Un extracto con filas sin coincidencia ya no bloquea todo el trabajo: el propietario puede seleccionar un candidato real para las filas ambiguas y dejar las diferencias pendientes con un motivo explícito. Se conserva el control de dos autorizaciones y no se crean gastos, ajustes ni pagos automáticamente.

## Resultado verificable

El caso de prueba importa una entrada10,00 y una salida2,00 sin asiento correspondiente. Tras confirmar, el resultado conserva **10,00 asociados y2,00 pendientes**, con motivo `BANK_FEE_UNPOSTED`. La interfaz muestra **conciliación parcial**; `fully_reconciled` y `reconciliation_confirmed` son falsos. El libro sigue balanceado e intacto.

`fully_reconciled` se refiere exclusivamente a las filas importadas, no a saldos inicial/final ni a un período bancario completo. Ningún resultado acredita autenticidad bancaria.

## Bloqueos subsanados

1. Filas ambiguas solo se rechazaban: ahora el usuario puede seleccionar expresamente un candidato de la misma empresa, cuenta, fecha, dirección e importe.
2. Una diferencia impedía conservar el trabajo válido: cada fila debe tener coincidencia seleccionada o motivo pendiente; no se puede ignorar una fila.
3. Falta de detalle residual: cantidades e importes se conservan por entradas/salidas, sin compensar diferencias opuestas ni presentarlas como cero.
4. Riesgo de reutilización: quedan reservadas las referencias de coincidencias y diferencias. Cambiar archivo o nombre no permite asociar dos veces una referencia activa ni una línea contable.
5. Falta de reapertura auditable: liberación en dos pasos conserva el historial y permite nueva revisión; no modifica ni borra asientos.
6. Lectores antiguos podían interpretar datos nuevos erróneamente: las resoluciones explícitas usan eventos de revisión/confirmaciónv2. Las reservas compatibles hacen que un lectorv1 no pueda reutilizar los movimientos confirmados que no entiende.
7. Falta de interfaz: el formulario compartido permite elegir candidato/motivo por fila, confirmar, recuperar y liberar en ambos paneles, conservando colores y navegación.

## Verificación

**801 pruebas Python aprobadas en45 suites, sin omisiones**, incluidas79 del puente corporativo. Manifiesto actual estable y hashes de registros comprobados.17 pruebas ORM/API nuevas, dos recorridos HTTP corporativos nuevos y seis pruebas del contrato de cobertura. El caso positivo y los rechazos cubren diferencias, ambigüedad, duplicados, candidato ajeno, importes distintos, reservas, reversión, recuperación, rollback de pruebas y versión de lectura. La regresión histórica de conciliación también pasó sus23 pruebas. **70 comprobaciones Chromium** entre los dos paneles:38 del recorrido parcial y32 de regresión del flujo completo anterior. Tipos estrictos de los componentes seleccionados aprobados; no sustituye build completa ni pruebas físicas.

Capturas móviles: [ERP](evidencias/implementacion-76-erp.png) · [Analemática](evidencias/implementacion-76-corporate.png).

[Evidencia76](evidencias/implementacion-76.json) · [Contrato operativo](OPERACION_CONCILIACION_PARCIAL.md).

## Pendientes reales

R12 continúa en ejecución. Faltan conciliación de saldos completos por período, pagos parciales contra un mismo movimiento, agrupaciones de varios movimientos, diferencias cambiarias, candidatos fuera de los límites de consulta, archivos grandes, identidad bancaria independiente y revisión profesional. Se adelantó el subconjunto COP independiente; la valoración FX de R11 sigue pendiente.

**63,89% (46/72), aceptación completa0/24.** No se duplica el crédito de ACC-015 ni se cierran los20 hitos. Sin commits, push, despliegues, datos reales ni movimientos de dinero.
