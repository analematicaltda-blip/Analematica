# Implementación 71 · Conciliación visible y medición del motor

Se amplió R03 con un registro por cuenta que atribuye movimientos reales del ledger a reservas, compras, ventas y contrapartidas. Distingue IVA descontable/generado y retenciones, conserva movimientos sin soporte atribuido y no los declara fiscales. Valida pruebas, recibos, revisión, documento e integridad del asiento. Se mantienen los endpoints anteriores.

El reporte está conectado al panel ERP y a una nueva opción de Analemática. Se conserva la identidad visual y se invalidan resultados al cambiar consulta/contexto. El puente ahora verifica campos, fuentes y sumas exactas antes de reenviar el reporte.

Se inició además el incremento independiente de R19: un banco de medición local ejecuta revisión, posteo, recuperación y conciliación, con p50/p95/p99, máximo y errores. La evaluación de clasificaciones conserva abstenciones; sin modelo/dataset autorizado la precisión queda no evaluada.

## Verificación

- 21 casos nuevos del registro y8 del contrato entre backends.
- 9 pruebas nuevas de medición: colas, errores, máximo sin redondear, denominadores y abstenciones.
- Recorridos Chromium reales del ERP y Analemática, tipos estrictos y capturas móviles: evidencia asociada.
- **681 pruebas Python aprobadas en 41 suites**, sin omisiones, incluidas50 del puente corporativo. **81 comprobaciones Chromium** en ambos paneles, tipos estrictos aprobados y capturas inspeccionadas. Manifiesto estable y hashes verificados; la medición optimizada corresponde a las mismas fuentes actuales.

[Conciliación y paneles](OPERACION_CONCILIACION_INTEGRAL.md) · [Medición reproducible](OPERACION_BENCHMARK.md) · [Evidencia71](evidencias/implementacion-71.json).

Los20 hitos no están cerrados. R03 conserva pendientes de fuentes nativas, deduplicación entre rutas, fiscalidad completa y validación profesional. R18 no se completa por conectar este reporte; R19 aún requiere carga objetivo, endurecimiento y revisión independientes, optimización según mediciones y evaluar IA con un dataset autorizado.

Avance calculado: **63,89 % (46/72)**; aceptación completa **0/24**. La base original se conserva. El porcentaje se regenera desde el registro de hitos; solo se acredita el incremento local de herramienta de medición y su verificación, sin aceptación completa ni garantía250ms/99,8%. Sin commits, push, despliegues, datos reales, pagos ni envíos DIAN.

## Hallazgo medido y corrección

Con100 documentos, la conciliación llegó inicialmente a máximo547.209ms y p95519.922ms. Se eliminaron las lecturas repetidas por documento mediante instantánea por lotes y validación compartida de posteo. La repetición midió máximo134.922ms y p95110.854ms, sin errores. Se conservan ambos resultados y manifiestos; son ensayos secuenciales locales, no una garantía productiva.

Capturas móviles: [ERP](evidencias/implementacion-71-erp.png) · [Analemática](evidencias/implementacion-71-corporate.png).
