# Implementación 07 · Medición estable y recorrido contable integrado

Se inicia el seguimiento numérico del motor: **22,22 % (16/72 hitos)**. Esta es la primera línea base, no una disminución respecto de una medición anterior. El detalle y las reglas están en [PROGRESO.md](PROGRESO.md).

Se mantienen 24 tareas y tres hitos por tarea: incremento funcional, verificación automatizada y aceptación de todo el alcance. Ocho tareas tienen los dos primeros hitos; ninguna reúne todavía todos sus criterios. La documentación sola no suma. La aceptación completa requiere todas las condiciones de la matriz, ambos sistemas cuando corresponda y las validaciones reales exigibles. El índice no representa horas, líneas de código, cobertura, certificación fiscal ni inmunidad a ataques.

## Avance técnico

Se incorporó un recorrido de navegador con React real, autenticación mediante contraseña, cookie y CSRF de Django, listado empresarial autorizado, DRF y consultas al ledger ORM. Usa identidades y asientos sintéticos en una base aislada, sin datos del usuario ni respuestas contables simuladas en el navegador.

El recorrido comprueba consulta de rentabilidad y liquidez revisada, cuenta de origen, rechazo de un prestador no autorizado y desaparición de resultados tras cerrar sesión. Complementa las pruebas anteriores de interfaz con respuestas sintéticas; no las reemplaza.

La consulta contable incorpora cierre de sesión directo: oculta las cifras al solicitarlo y muestra reintento si el servidor no confirma el cierre, reutilizando las garantías del hook existente. El recorrido prueba este control desde la propia pantalla contable.

Se reutilizó el servidor de prueba existente mediante una opción exclusiva de fixture contable. No se cambió la autenticación productiva ni se añadieron credenciales al código. Los secretos del fixture se generan y eliminan durante la prueba. La prueba está preparada en el workflow, pero no se ejecutó en GitHub ni se publicó código.

## Seguimiento

`progress-registry.json` conserva las evidencias evaluadas por tarea. `tools/update_progress.py` genera `progreso.json` y `PROGRESO.md`; `--check` detecta resultados desactualizados. El denominador no cambia automáticamente y rechaza tareas duplicadas, pruebas sin implementación y referencias ausentes o externas al repositorio. Duplicar archivos de evidencia no concede puntos adicionales. Se añadieron pruebas de estas reglas.

El índice se mantendrá en cada corte. Reforzar un incremento ya verificado no suma un hito nuevo. Para alcanzar el 100 % se deben cerrar también los pools aún pendientes, en lugar de reclasificar pruebas locales como habilitación productiva.

## Límites y siguientes tareas

El recorrido prueba el ERP contra un backend real, con datos sintéticos. No acredita integración contable de la consola corporativa de Analemática, fiscalidad DIAN, bóveda BYOS, bancos, nómina, SG-SST, sostenibilidad, NLP, dispositivos reales, objetivos de latencia ni datos contables de producción. El grafo de migraciones nativo histórico y la compilación completa siguen sujetos a los pendientes previos.

Continúan pendientes el formulario de clasificación, políticas por vigencia y fuentes operativas por paquete/habitación. La versión actual requiere iniciar sesión desde el acceso seguro existente.

Ver evidencia local en `evidencias/implementacion-07.json`. Sin commits, push, cambios de bases del usuario ni habilitación productiva.
