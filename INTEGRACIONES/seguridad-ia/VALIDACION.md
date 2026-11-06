# Validación de la integración · 6 de noviembre de 2026

- Copias completas verificadas por SHA-256, blob Git, modo y conjunto exacto de archivos: **15.598 archivos AiSOC y 4 archivos free-ai-apis**. Sin submódulos ni carpetas `.git` anidadas; licencias originales conservadas.
- Catálogo generado reproduciblemente: **102 entradas en 15 categorías**, todas sin activar y con cuotas/términos no verificados. La comprobación `sync_catalog.py --check` pasa.
- **9 pruebas nuevas** por las rutas autenticadas y base SQLite real de prueba: catálogo, filtros, acceso administrativo, minimización de datos, aislamiento usuario/tenant, paginación, firma/alteración, clave confiada independiente y estado no verificado del SOC.
- **27 regresiones** de asistencia y control: correctas.
- **2 pruebas** de despliegue corporativo y **4 de seguridad** de las vistas: correctas.
- Panel probado con login central real en ambas vistas HTTPS locales (SGA-CD `8100` y Analemática `8101`), a **1440, 390 y 320 px**: búsqueda, filtro de vídeo/Replicate, estado del SOC, descarga firmada explícita, sin desbordamiento ni errores JavaScript. Las solicitudes externas fueron bloqueadas durante las pruebas y no se conservaron descargas de auditoría.
- La API y los recursos públicos se actualizaron únicamente en el entorno local de validación, preservando datos y claves. No se añadieron tablas ni se modificaron bases del SOC.

No se inició AiSOC, no se ejecutó su pipeline, no se descargó Ollama ni se instalaron las ruedas upstream. Falta espacio: el host tenía menos de 1 GiB libre antes de la copia, frente a los 20 GiB que declara requerir CORE. No se ejecutó la suite completa del producto upstream ni se verificaron sus cifras de detecciones/conectores en ejecución.

El batch exportado utiliza los campos de la solicitud de ingestión presentes en el código Go copiado. No se validó la recepción/normalización en un AiSOC vivo, ni alertas o reglas personalizadas SGA-CD. El ledger upstream y el exportador SGA-CD tienen alcances distintos, descritos en README.

No se usaron credenciales externas, no se transmitió telemetría, no se activaron API, no se verificaron ofertas gratuitas y no se generaron imágenes/vídeos con proveedores. No se afirma protección activa ni seguridad absoluta. La exportación expresa información observada de autorizaciones, no incidentes inventados.
