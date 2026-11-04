# Arranque de nodos Flet

Se crearon en el entorno de trabajo los servicios sgacd-flet-nodes-flet-desktop-1
y sgacd-flet-nodes-flet-mobile-1, en 127.0.0.1:8501 y 127.0.0.1:8502.

Imagen Docker construida con éxito (capas de dependencias reutilizadas).
Los dos contenedores están healthy. Se comprobaron HTTP 200 y sesiones WebSocket
reales, vista inicial de bienvenida y controles con azul cielo. Se repitió el
arranque con los mismos contenedores y volúmenes.

La prueba automatizada verifica carpetas correctas, publicación solo en loopback,
preservación del servicio PostgreSQL, repetición sin cambios y rechazo de una
configuración personalizada antes de escribir.

No se inició el Codespace del usuario desde este entorno. No se verificaron
paquetes nativos, login contra el backend web ni todas las rutas de la aplicación.
No se afirma haber completado revisión gráfica de CanvasKit ni Actions remoto.
