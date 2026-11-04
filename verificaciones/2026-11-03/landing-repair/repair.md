# Reparación de publicación de la landing

Se reprodujo el apilamiento de las cinco fotografías al bloquear vanguard.css: altura de galería 986 px. La prueba anterior usaba eventos vacíos y omitía este caso. Esto reproduce el síntoma; no demuestra por qué esa hoja no se aplicó en el navegador del usuario.

La publicación ahora genera index.html a partir de la plantilla original, con el carrusel principal renderizado desde su componente existente, el panel territorial inmediatamente después y la hoja sky cargada en head. Los recursos CSS/JS reciben hashes en sus URLs. La plantilla fuente permanece intacta. Las galerías tienen estilos acotados de respaldo y flechas que funcionan sin fuentes externas.

Validación sobre Nginx local, puerto 18080:
- Carrusel principal: navegación, reinicialización, escape de texto y respaldo de imágenes.
- Galerías: cuatro tarjetas de demostración, cinco fotos por tarjeta, anterior/siguiente y filtros; 1440/390/320 px, con y sin vanguard.css.
- Landing: doce secciones y controles conservados, sin desbordamiento; 1440/768/390/320 px.
- Sin JavaScript: diez diapositivas presentes, hoja sky y panel territorial en posición correcta.
- Publicador: configuración conservada, repetición sin cambios, conflictos rechazados antes de escribir.
- Service worker: actualización, caché sin conexión y exclusión de API/autorización.

Las pruebas usan respuestas API e imágenes controladas, y bloquean servicios externos; no verifican disponibilidad de Unsplash, YouTube ni del Codespace del usuario. Las capturas son de esas pruebas. No se ha accedido al terminal del Codespace del usuario. No se afirma que Actions remoto haya pasado.
