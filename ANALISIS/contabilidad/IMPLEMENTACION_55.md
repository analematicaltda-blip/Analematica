# Implementación 55 · Capacidad hotelera revisada y ratios contables

**Avance global: 50,00 % (36/72), sin crédito duplicado de ACC-016.** H15 pasa a ejecución: 4 hitos verificados localmente, 8 en ejecución y 8 pendientes. Los 20 hitos no están completados y la aceptación completa continúa en 0/24 tareas.

## Cambio operativo

ERP y Analemática permiten consultar las habitaciones físicas existentes de la empresa, seleccionar explícitamente la disponibilidad del día y clasificar cuentas de ingresos de habitaciones, otros ingresos operativos, gastos/costos operativos y partidas no operativas. Una primera confirmación guarda la revisión y una segunda del mismo titular confirma la versión diaria. Reintentos recuperan el mismo resultado; versiones competidoras se serializan bajo bloqueo de empresa. No se generan asientos al registrar capacidad.

RevPAR y GOPPAR utilizan importes COP de líneas realmente contabilizadas, con fecha económica y fecha de conocimiento. Cada resultado expone procedencia contable y versiones de capacidad. Una corrección posterior no entra en una consulta con corte anterior. El servicio valida hashes, cuentas, pertenencia y pruebas de revisión. No utiliza precios del catálogo como ingresos ni inventario actual para inventar capacidad pasada.

Capacidad cero, días sin observación, clasificación cambiante o cuentas financieras sin clasificar producen un indicador no disponible, con motivo visible. El margen de paquete permanece sin calcular mientras falte asignación de costos por paquete. El catálogo de habitaciones y los resultados se retiran de la interfaz al perder identidad. Se mantienen los colores azul, azul claro y texto blanco y la adaptación móvil.

## Evidencia ejecutada

- **403 pruebas Python aprobadas**, incluidas 24 del nuevo servicio y una integración HTTP corporativa.
- **45 escenarios PostgreSQL aprobados**, incluidos reintento concurrente y competencia entre revisiones hoteleras; restauración local verificada.
- **227 comprobaciones Chromium aprobadas**: 53 ERP, 30 corporativas, 52 apertura/políticas, 28 nómina, 32 conciliación y 32 hoteleras. Ambos paneles recorren las dos confirmaciones, ratios 5/4 sobre ingresos 10 y gastos 2, revisión a capacidad cero y recuperación del corte previo.
- TypeScript estricto de cuatro componentes sin errores. No se acredita compilación Next completa.
- Suite final con fuentes estables: `/tmp/sgacd-hotel-55-final`. Reporte, resultados y huellas de capturas en [evidencia 55](evidencias/implementacion-55.json). Son datos sintéticos aislados, no aceptación productiva.

## Límites y trabajo pendiente

La disponibilidad es una declaración revisada del titular sobre habitaciones existentes; no demuestra ocupación, disponibilidad de una noche completa ni autenticidad independiente. Solo se captura el día actual de Bogotá. Se necesitan series legítimas, revisión profesional, ocupación/ADR, dimensiones por establecimiento y asignación de costos por paquete. El modelo legado alternativo de habitaciones no se fusionó ni migró.

El alcance actual es COP, inventarios de 1–50 habitaciones, ventanas de 31 días, hasta 500 versiones de capacidad y 2000 líneas financieras por consulta; cada grupo admite 10 cuentas y el catálogo muestra hasta 200 con aviso. No hay conversión de divisas. Las cuentas no clasificadas bloquean ratios, evitando omitir costos silenciosamente.

Los cortes se basan en timestamps registrados por la aplicación, no en reloj certificado ni prueba de publicación original. Los hashes del outbox no sustituyen WORM, firma independiente ni controles contra escrituras SQL privilegiadas. Falta cualificar retención, restauración, permisos de base de datos y rendimiento sobre infraestructura objetivo. La API admite corte explícito; el formulario consulta el corte actual.

Continúan abiertos otros desarrollos locales y validaciones externas del plan de 20 hitos. No se realizaron commits, push, actualización de main, pagos, despliegues ni solicitudes DIAN/bancarias reales.
