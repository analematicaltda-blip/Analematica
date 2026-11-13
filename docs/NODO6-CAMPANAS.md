# Nodo 6: campañas, calendario y adaptación multicanal

La creación y distribución se gestionan dentro del panel SGA-CD, en **CRM y comunicación · Full**: Campañas y envíos, Calendario, Audiencia, Adaptar videos y Canales de la organización. No hace falta entrar en el puerto 8606 ni entregar la clave del trabajador a los usuarios.

## Qué integra esta entrega

| Canal | Operación | Requisitos de cuenta |
|---|---|---|
| YouTube | Video privado, conservando la restricción de pruebas | OAuth con youtube.upload; clasificación infantil explícita |
| Instagram, Meta | Crear Reel, comprobar procesamiento y publicar | Cuenta profesional vinculada a Página, Facebook Login y permiso de publicación; URL HTTPS pública del video |
| Facebook, Meta | Cargar video a la Página y consultar su procesamiento | Token de Página y permisos de administración/publicación |
| WhatsApp Business, Meta | Subir video y enviar una plantilla aprobada por destinatario | Phone number ID, token autorizado, plantilla con cabecera de video y audiencia con consentimiento |
| X, independiente de Meta | Carga segmentada de medios y publicación de post | Credenciales OAuth 1.0a de usuario, escritura y acceso a las APIs de medios y publicaciones |
| TikTok | Consultar opciones del creador, cargar video y consultar estado | Content Posting API, permiso video.publish y cuenta/aplicación autorizadas; solo yo por defecto |
| Gmail | Un mensaje individual por destinatario, con MP4 adjunto | OAuth con gmail.send, refresh token y correo del remitente autorizado |

Instagram, Facebook, X, TikTok y YouTube publican en la cuenta conectada; no se implementan mensajes directos masivos a seguidores. WhatsApp y Gmail usan la audiencia seleccionada. Esta versión mantiene una cuenta por proveedor y organización, según el modelo de canales existente.

Los conectores se implementaron y probaron con transportes simulados. No se han autorizado cuentas reales ni verificado publicaciones en las plataformas. Los permisos, revisión de aplicaciones, cuotas y posibles requisitos comerciales de cada proveedor siguen siendo necesarios. X no pertenece a Meta.

## Flujo de trabajo

1. El administrador configura las cuentas de su organización en **Canales**, sin pegar credenciales en el chat. Se cifran en el servidor y no se vuelven a mostrar.
2. En **Audiencia**, un usuario con permiso CRM registra correos o teléfonos internacionales, con origen del consentimiento. Se pueden importar hasta 100 destinatarios por lote. Registrar una baja bloquea envíos posteriores. Los contactos del CRM no se consideran automáticamente suscritos a campañas.
3. En **Campañas**, selecciona un video del estudio, plataformas, destinatarios, copia y fecha. Guardar crea un borrador; no envía nada. Puedes preparar borradores aunque todavía no hayas conectado las cuentas.
4. Revisa las opciones específicas: plantilla e idioma de WhatsApp, texto de X, privacidad e identificación de IA en TikTok y clasificación de YouTube.
5. Cuando las cuentas y el despacho estén habilitados, aprueba la programación. El servidor comprueba nuevamente plan, delegación, cuenta, consentimiento y cuota antes de cada envío.
6. El calendario permite revisar, cambiar fecha de trabajos no iniciados y detener pendientes. Cambiar fecha devuelve la campaña a borrador y exige aprobarla de nuevo. Un envío ya iniciado no se puede retirar desde el calendario.

El calendario muestra horas en la zona del navegador; cada campaña conserva el instante UTC y la zona IANA declarada al crearla. La cola empieza a procesar a partir de esa fecha; no garantiza envíos simultáneos a todos los destinos ni reserva cuotas futuras de las plataformas.

## Planes, cuotas y separación por empresa

Básico conserva la operación institucional y no accede a estas funciones. Full vigente habilita al administrador de empresa; su equipo necesita permisos delegados. CRM administra audiencia, multimedia permite adaptar videos y publicaciones permite preparar/aprobar campañas y seleccionar audiencia. El administrador general tiene el espacio propio de la plataforma.

Las credenciales, videos, campañas y contactos se resuelven a partir de la identidad real de base de datos y su organización. No existe fallback al canal del dueño. Cambiar las credenciales o desconectar una cuenta bloquea las programaciones pendientes vinculadas a su configuración anterior. Suspender a un autor o revocar su permiso bloquea sus envíos programados.

No se modificaron precios ni cuotas existentes. Cada destino consume una operación de `social_posts` al iniciar el despacho, una sola vez aunque haya consultas de procesamiento. La preparación de formatos reutiliza el video existente y no factura una nueva generación creativa. Un borrador admite hasta 200 destinos; aprobarlo no permite superar la cuota mensual del plan. La reserva atómica al despachar evita sobrepasarla entre campañas concurrentes. Los intentos inciertos conservan su consumo para evitar reintentos gratuitos y duplicados.

## Adaptación de video

| Perfil | Encuadre de esta demo | Máximo de duración | Tamaño máximo |
|---|---|---|---|
| Instagram | 1080 × 1920 | 90 s | 40 MB |
| TikTok | 1080 × 1920 | 60 s | 40 MB |
| YouTube | 1080 × 1920 | 180 s | 40 MB |
| Facebook | 1080 × 1080 | 90 s | 40 MB |
| X | 1280 × 720 | 140 s | 40 MB |
| WhatsApp | 480 × 854 | 60 s | 15 MB |
| Gmail | 1280 × 720 | 140 s | 15 MB adjuntos |

Son límites conservadores del sistema de pruebas, no una garantía de todos los límites comerciales de las plataformas. Se genera H.264, píxeles yuv420p, AAC cuando existe audio, y MP4 con faststart. Se ajusta con bandas para conservar el encuadre y nunca se recorta silenciosamente la duración. Si un archivo no cumple, se conserva el original y se pide preparar un clip más corto. Las versiones se guardan por video/perfil y se reutilizan.

Los reels actuales continúan siendo montajes FFmpeg; esta entrega no afirma disponer de generación de movimiento con Veo ni replica todas las funciones de Predis AI.

## Despliegue en Codespaces

```bash
bash -e <<'SH'
cd /workspaces/SGA-CD
git fetch origin codex/node6-campaign-calendar
git merge --ff-only FETCH_HEAD
python3 BACKEND/tools/integrate_workspace.py --start
SH
```

El actualizador conserva configuración web, usuarios, credenciales, volúmenes y bases offline de Flet. Añade seis tablas de campañas y el servicio **campaign-scheduler**, sin puerto público. Actualiza únicamente backend, nodo 6, calendario y copia web; recarga nginx. Conserva el mecanismo previo de respaldos privados. No borres volúmenes ni fuerces Git si detecta una divergencia.

El despacho nuevo queda inicialmente **deshabilitado**: `CAMPAIGN_DELIVERY_ENABLED=0` en el archivo privado `~/sgacd-demo/workspace.env`; el instalador sincroniza `NODE6_CAMPAIGNS_ENABLED=0` en el trabajador. Con estos interruptores se pueden revisar formularios, generar/adaptar videos y guardar borradores, pero no aprobar ni despachar campañas. La validación local se hizo en este modo, sin enviar mensajes reales.

Cuando existan cuentas autorizadas y se decida comenzar pruebas de envío, el operador cambia explícitamente `CAMPAIGN_DELIVERY_ENABLED` a `1` en ese archivo y repite el actualizador. Sigue haciendo falta aprobar cada campaña. No actives ese modo solamente para inspeccionar la interfaz.

El servidor debe permanecer encendido para procesar la programación. Codespaces puede detenerse por inactividad y no sustituye un servicio permanente de producción. Los trabajos persisten en PostgreSQL; si una campaña lleva más de 24 horas de retraso, queda bloqueada para revisar antes de enviar contenido antiguo.

## Instagram y acceso público al video

Meta necesita descargar el video desde una URL HTTPS alcanzable sin autenticación de GitHub. Un puerto privado de Codespaces no cumple este requisito. El administrador general puede configurar **Canales → Dominio público para medios** cuando exista un dominio que sirva esta API; guardar el dominio no prueba su conectividad. Alternativamente se admite `PUBLISH_MEDIA_ORIGIN` como configuración inicial del servidor.

El backend emite enlaces firmados de 12 horas para el video adaptado de una campaña aprobada de Instagram. No publica el directorio de archivos del trabajador ni revela su token. Comprueba el trabajo, espacio, permisos y estado antes de servir el MP4, y admite HEAD y rangos de descarga. Gmail usa adjuntos; TikTok, X, Facebook, WhatsApp y YouTube cargan archivos directamente y no necesitan ese origen público para el video.

Gmail incorpora baja de un clic cuando existe origen público; sin él se incluye la opción de responder BAJA al remitente. La importación no reactiva automáticamente un contacto dado de baja. La bandeja de entrada, el procesamiento de esas respuestas y las respuestas automáticas requieren integrar los webhooks/autorizaciones de entrada; no se presentan como operativos en esta entrega.

## Fiabilidad e historial

El backend reclama cada destino atómicamente. Nodo 6 conserva además un diario privado por organización, trabajo y fase: repetir una solicitud no repite el mismo POST al proveedor. Una interrupción deja el resultado en comprobación. El planificador puede consultar ese diario para confirmar una respuesta tardía, sin reenviar. Solo los rechazos inequívocos por frecuencia se esperan con un plazo antes de continuar; no se reintenta ciegamente un envío incierto.

Se distingue **publicado**, **aceptado por la plataforma**, **en procesamiento**, **rechazado**, **bloqueado** y **requiere comprobación**. La aceptación de Gmail/WhatsApp no demuestra entrega ni lectura. Cambiar de plan o permisos no borra el historial. Los clientes Flet conservan su funcionamiento offline y sus bases locales existentes; este estudio nuevo se integra en los paneles web y en la API compartida.

## Referencias para registrar las aplicaciones

- [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages)
- [Instagram con Facebook Login](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/content-publishing)
- [Facebook Video API](https://developers.facebook.com/docs/video-api/guides/publishing)
- [X: carga de medios](https://docs.x.com/x-api/media/upload-media/uploading-media/chunked-media-upload)
- [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [Gmail: envío de correo](https://developers.google.com/workspace/gmail/api/guides/sending)

La salida de red necesita, según el proveedor, `graph.facebook.com`, `graph-video.facebook.com`, `upload.twitter.com`, `api.x.com`, `open.tiktokapis.com` y el host de carga oficial devuelto bajo `*.tiktokapis.com`, `oauth2.googleapis.com`, `gmail.googleapis.com` y `www.googleapis.com`. El entorno administrado actual no tiene autorizadas/configuradas estas cuentas; las pruebas de contrato no sustituyen validar OAuth y los permisos reales.
