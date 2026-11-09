# Implementación 09 · Historial revisable de clasificación

**Avance: 22,22 % (16/72 hitos).** Continúa ACC-016; no se cierra su aceptación completa ni se cambia el denominador.

Se añadió al núcleo compartido `ratios.history`: historial empresarial paginado mediante revisión anterior, con límite de 1 a 50 registros. Cada página verifica los digests antes de devolverla. Las revisiones antiguas conservan sus cuentas originales, incluso si hoy están inactivas; no se reclasifica ni reescribe la historia. Una nueva revisión entre páginas no duplica registros de las páginas anteriores.

El ERP expone `GET cuentas/historial-liquidez/?provider_id=<UUID>&limite=20&antes_revision=<n>` bajo el prefijo contable existente. Reutiliza titularidad, vínculo empresarial y autenticación. La consulta no ofrece operaciones de edición o borrado. Rechaza límites y cursores inválidos y oculta páginas cuya integridad no puede comprobarse.

La pantalla muestra versiones, fecha, identificador del revisor, evidencia declarada, digest y cuentas. Permite consultar páginas anteriores o volver a las recientes; se actualiza después del guardado. Cambiar identidad o empresa oculta resultados anteriores y cancela solicitudes. Conserva la identidad azul con texto blanco y controles de foco. Un digest local no acredita firma independiente ni impide la manipulación por un operador SQL privilegiado.

## Verificación

- 71 métodos contables aprobados, incluidos paginación estable, empresa ajena, límites/cursores, cuentas históricas inactivas y alteración de una revisión antigua.
- 14 comprobaciones integradas de navegador, sesión/CSRF Django y ORM en datos sintéticos aislados: confirma que el historial conserva revisiones 1 y 3 después de revisión concurrente y guardado.
- Tipado TypeScript estricto sin errores.
- Evidencia local y hashes comprobados; no migraciones ni cambios de datos del usuario.

Evidencia: `evidencias/implementacion-09.json`. No se repitió PostgreSQL en este corte: no cambia el algoritmo de bloqueo ni el esquema; las nuevas consultas se probaron mediante ORM y la API real de Django aislados.

Pendientes: conexión contable autenticada de la consola Analemática, cobertura real revisada por contabilidad, políticas con vigencias, consulta de un ratio usando explícitamente una revisión histórica, validación móvil/accesibilidad integral, fallos de red, indicadores operativos y restantes pools. No se habilita producción ni se realiza commit o push.
