# Implementación 40 · Respuestas tardías y retorno al mismo contexto

**Avance: 38,89 % (28/72 hitos).** Corrige y verifica ACC-008/ACC-020 ya puntuados. No acredita otro hito.

## Corrección

Los paneles AccountingQuery y CommercialQueue ocultaban respuestas por contexto y abortaban solicitudes antiguas, pero conservaban el resultado/error/estado ocupado anterior. Al salir y regresar al mismo contexto podían reaparecer datos previos o quedar el botón bloqueado si la petición abortada no ejecutaba su limpieza final.

Ahora cada cambio de contexto aborta la petición y elimina resultados, errores y estado ocupado. Se mantienen las comprobaciones de identidad del contexto y AbortSignal al resolver respuestas. Se aplica tanto a empresa/sesión como a pregunta y fechas en la consulta asistida. No se cambia la autorización del backend ni se reenvía ninguna petición automáticamente.

## Prueba de respuestas tardías

La nueva suite Chromium usa un transporte que deliberadamente ignora AbortSignal. Retiene respuestas mediante promesas y libera después de cambiar/restaurar contexto; no depende de sleeps.

Ocho comprobaciones verifican vuelta empresa A → B → A sin bloqueo, éxito tardío ignorado, resultado anterior sin resucitar, error de permiso tardío ignorado, cambio/restauración de fechas, cierre con consulta pendiente, reentrada local con la misma identidad utilizable y consulta nueva correcta. La reentrada sintética no acredita recuperación de una sesión revocada en servidor.

## Regresiones

- 31 comprobaciones integradas de panel completo con sesión/cookie/CSRF y Django aislado aprobadas.
- Ocho comprobaciones de transporte retrasado, nueve de interfaz de consulta y nueve de cola comercial aprobadas.
- TypeScript estricto de ambos componentes sin errores.

Evidencia: `evidencias/implementacion-40.json`, con hashes de fuentes. Se incorpora la suite al workflow; no se ejecutó CI remoto. No se repitieron backend/PostgreSQL: no cambió su código o esquema.

## Pendientes

Pruebas de sesión realmente revocada, desconexión, cachés y múltiples pestañas; dispositivos físicos, build completo y consola Analemática. No se afirma que esta corrección cancele la consulta ya ejecutada en servidor: descarta la respuesta obsoleta en la interfaz. El servidor sigue siendo responsable de comprobar permisos en cada petición.

Sin cambios de datos del usuario, commit, push o despliegue.
