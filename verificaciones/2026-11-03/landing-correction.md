# Landing: carrusel, posición y controles

El registro del usuario confirma el fast-forward al commit d5cbfc93 y la
actualización de 17 archivos de la copia web. El index.html y las referencias
al carrusel no fueron eliminados ni modificados por esa entrega.

Se reprodujo la landing con diez slides en una sesión nueva. El bloque
territorial aparecía después de partners; se movió el nodo existente justo
después de carrusel-moderno sin cambiar IDs, opciones, handlers ni contenido.
La prueba de orden falló antes y pasó después. Se mantienen las doce secciones.

Los controles del bloque usan fondo #0D1424, texto #38BDF8, bordes de 12px y
altura mínima de 48px. La cuadrícula acepta anchos pequeños sin desbordar.
La barra social móvil se sitúa horizontalmente al pie para no cubrir títulos.

Se corrigió el índice al reinicializar el carrusel con ajustes del administrador,
el listener repetido de visibilidad, el pausa/reanuda y la navegación por teclado.
Se escapan título, subtítulo y tag. Las URLs de imágenes existentes se conservan;
si una imagen falla se muestra un SVG local explícitamente identificado como
imagen no disponible, en vez de ocultar el elemento.

El worker anterior conservaba scripts con cache-first y no llamaba skipWaiting
ni clients.claim. Esto puede mantener clientes en una versión anterior; no se
ha inspeccionado directamente el caché del navegador del usuario. La regresión
del lifecycle falló antes y pasó después. La versión nueva actualiza primero
HTML, JS y CSS desde red, mantiene fallback offline y excluye API y autenticados.

Validación final: Chromium real a 1440/768/390/320 px mediante Nginx local,
sin errores JS ni desbordamientos. Se verificaron opciones seleccionables,
orden de secciones, una sola slide activa tras reinicio, teclado, fallback
de imagen y ausencia de inyección HTML. Se usaron fixtures API y se bloquearon
recursos externos: no es prueba de backend ni de disponibilidad de Unsplash.
HTTP 200 para HTML, main.js, componente, stylesheet, fallback SVG y worker.
El actualizador web funcionó y repetirlo no modificó archivos ya actualizados.

Los siete archivos de producto protegidos conservan sus bytes de HEAD. No se
eliminaron datos ni se cambiaron credenciales. Evidencia detallada local en
landing-before.log, landing-nginx-final.log, worker-before.log y worker-after.log.
Se añadió frontend-regression.yml; su resultado remoto aún no se comprobó.
El Codespace del usuario no fue operado directamente desde esta sesión.
