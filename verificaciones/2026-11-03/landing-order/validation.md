# Orden y presentación de la landing

Orden publicado: carrusel principal, controles territoriales, presentación en
video, instituciones/aliados, portada institucional compacta, monitor, testimonios,
módulos, preguntas, planes, oferta y registro. Se mantienen las doce secciones,
sus IDs y los contenidos originales. La plantilla protegida index.html, style.css,
vanguard.css, el panel admin_general.js y los endpoints del backend no se editan.
El publicador genera la copia desplegada y el JS aplica el mismo orden como respaldo.

El menú es fijo con navegación desplegable en pantallas pequeñas, cierre por enlace,
Escape y clic exterior. Inicio enlaza al carrusel; Actividades a los controles.
Se elimina el mínimo de 80vh de la portada, que ahora permanece después de aliados.
Los controles y el video conservan las esquinas redondeadas y paleta azul.

Las cuatro tarjetas corporativas existentes se conservan y ahora forman un carrusel
horizontal con controles anterior/siguiente y desplazamiento táctil. renderPartners,
que estaba definido pero no se llamaba, vuelve a representar su contenido de respaldo.
No se encontró un catálogo público de empresas afiliadas gestionable en la API actual:
no se inventó un endpoint ni se consultaron datos privados de inquilinos. Esta entrega
no añade gestión de afiliados en administración; conserva la información ya existente.

La respuesta pública de ajustes sigue aplicando título, subtítulo y diapositivas del
administrador; ahora el video de presentación también respeta hero_video_url, sin
sustituirlo después por el enlace de ejemplo. Se aceptan YouTube y archivos de video
HTTP(S)/rutas relativas. Si el archivo no carga se muestra un estado legible.
La ruta predeterminada assets/video/sga_cd_institutional_5min.mp4 no existe en el repo;
se necesita una URL válida o publicar ese archivo para reproducirlo.

Pruebas locales sobre Nginx 18080:
- landing-order: cinco anchos 1440/1024/768/390/320; orden, menú fijo/desplegable,
  anterior/siguiente de aliados, doce secciones, ajustes públicos simulados,
  ausencia de desbordamientos, video ausente y orden sin JavaScript.
- landing.cjs: cuatro anchos, carrusel principal, escape, formularios y geometría.
- landing-resilience: galerías con cinco imágenes en tres anchos, con y sin la
  hoja vanguard.css, filtros y controles; publicación estática del carrusel.
- publisher.py: configuración y plantilla conservadas, repetición segura, conflictos.
- service-worker.cjs: actualización/caché sin conexión y exclusión de API/autorización.

Las respuestas del administrador y los fallos de red se simulan en las pruebas de
navegador. Los servicios externos se bloquean: las capturas no prueban disponibilidad
de fotografías externas ni reproducción de YouTube. No se afirma validación de
escritura del panel ni una prueba visual con todas las CDN disponibles. No se accedió
al terminal del Codespace del usuario ni se afirma un resultado remoto de Actions.
