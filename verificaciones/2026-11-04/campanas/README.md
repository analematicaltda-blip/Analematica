# Ampliación Nodo 6: campañas multicanal

Validación en contenedores locales separados del Codespace privado del usuario. No se enviaron mensajes, videos ni correos a plataformas externas.

- Backend/actualizador: 32 pruebas de planes, permisos, aislamiento, registro, campañas, audiencia, concurrencia, aprobación, programación, conciliación sin reenvío, bajas, canales cifrados y bloqueo en modo preparación. Incluye verificar la migración en un proceso nuevo para resolver las dependencias de las tablas.
- Nodo 6: 22 pruebas. Los seis nuevos adaptadores usan respuestas HTTPS simuladas; YouTube privado mantiene sus pruebas. Se valida OAuth 1.0a frente a un vector de referencia, MIME individual de Gmail, plantilla de WhatsApp, fases de publicación, URL de carga de TikTok, borrado de secretos de errores y bloqueo incluso con token interno válido cuando el modo de envíos está apagado.
- Video: FFmpeg real verificó los siete perfiles con ffprobe, codec H.264 y yuv420p; se comparó la huella del original antes y después.
- Navegador: 16 flujos completos (general, empresa, jefe de área delegado y Básico × 1440/768/390/320 px) para siete conexiones, borradores por audiencia, aprobación simulada, calendario, adaptación, consentimiento y limpieza de credenciales. Se conservan las 48 combinaciones de los paneles previos.
- Recorrido real nginx → backend PostgreSQL → Nodo 6: se generó un video y se adaptó a WhatsApp 480×854, Gmail 1280×720 y Facebook 1080×1080. El original se conservó. Se guardó un borrador de tres destinos y se comprobó que la aprobación falla con despacho deshabilitado. Detalles sin credenciales en runtime.json.
- El planificador real arrancó saludable con ambos interruptores de despacho en 0; no había campañas pendientes al instalarlo. Navegador real comprobó calendario persistido, siete plataformas disponibles para preparar borradores y descarga autenticada de versiones. Capturas adjuntas.
- Publicador determinista y service worker: preservación de configuración, conflictos y caché verificada. No se cambiaron las plantillas protegidas, módulos Flet, submódulos ni evidencias anteriores.

Se corrigió un problema descubierto en la migración real: el proceso independiente del instalador necesitaba registrar los modelos workspace para resolver sus claves foráneas. La prueba en un proceso nuevo evita que las importaciones previas del conjunto de pruebas oculten ese fallo.

Las conexiones reales de proveedores, OAuth, revisión de aplicaciones, recepción de mensajes y entrega/lectura siguen pendientes. Las capturas y los resultados no afirman activación de esas cuentas. El bloqueo inicial de revisión automática del arranque se resolvió comprobando que no había cola y añadiendo un modo de preparación que impide aprobación y despacho tanto en backend como en Nodo 6.
