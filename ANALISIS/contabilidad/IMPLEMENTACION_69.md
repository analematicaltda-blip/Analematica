# Implementación 69 · Datos laborales verificables y despacho condicionado

Se incorporaron registros persistentes por trabajador para autorización profesional, EPP, jornadas, cierre de jornadas abiertas, descanso y revocaciones. El despacho genérico consulta esas referencias y vuelve a comprobarlas en las dos confirmaciones del titular. La ausencia de datos no se interpreta como aptitud ni descanso.

La decisión profesional queda cifrada y segregada. Capturarla requiere revisor provisionado y permiso clínico explícito; consultarla exige adicionalmente permiso clínico de lectura. El resumen del titular incluye referencias y fechas, sin decisión ni documentos médicos. Las altas son idempotentes y versionadas, con soporte y autor; correcciones y revocaciones no borran historia.

Se añadió un camino positivo de inicio solo para órdenes genéricas con política del servidor y datos válidos. Conserva bloqueos del cambio genérico de estado. El fin requiere dos confirmaciones, deja una jornada persistida y lleva a VALIDACION contable, sin declarar operación completada ni contabilizar nómina/costos. Cambios de fuente, permisos revocados, registros vencidos, trabajo solapado y reintentos se controlan transaccionalmente.

## Verificación

- 37 pruebas específicas nuevas aprobadas: cifrado estricto, permisos, empresa ajena, datos ausentes, aptitud restringida/no aptitud, vigencias, EPP, trabajo/descanso, inmutabilidad, idempotencia, paginación, revisión doble, rollback y fin registrado.
- Migración real en una base SQLite nueva: seis tablas vacías, sin violaciones FK, guardas SQL presentes y `makemigrations --check` sin diferencias para `sg_sst`. No se crearon trabajadores ni soportes reales/ficticios en esa base.
- 613 pruebas Python aprobadas en 38 suites, sin omisiones; incluye 40 pruebas del puente corporativo. Manifiesto estable, hashes de artefactos verificados y comparados con las fuentes actuales. Dependencias compatibles.

[Contrato de datos, rutas, permisos y operación](OPERACION_DATOS_SEGURIDAD_TRABAJADOR.md). [Evidencia 69](evidencias/implementacion-69.json).

## Alcance que sigue pendiente

Datos legítimos y revisión profesional de políticas/habilitación, trabajo fuera de plataforma, evidencia física, migración histórica y pruebas PostgreSQL del flujo nuevo, interfaces de captura y procesos especializados. No hay activación por defecto, actuación física, pago ni transmisión oficial. No se modificó el diseño visual.

El avance global permanece **61,11 % (44/72)** y la aceptación completa **0/24**: amplía ACC-012 ya acreditada, sin sumar dos veces. R09 continúa en ejecución por su alcance pendiente; no se declaran cerrados los 20 hitos. Sin commits, push ni despliegue.
