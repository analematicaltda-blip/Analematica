# Nodo 7 · Analemática

Landing corporativa existente, publicada como servicio independiente y conectada a SGA-CD. Conserva el contenido, la paleta y la consola de agentes originales; no instala Muse ni conecta cuentas de redes sociales.

## Abrir en Codespaces

Después de incorporar la rama `codex/analematica-node`:

```bash
cd /workspaces/SGA-CD
python3 Analematica/deployment/start.py
```

El comando actualiza la integración existente de backend y arranca `analematica`. Conserva bases de datos, volúmenes, credenciales, nodos Flet y campañas. Se produce un reinicio breve del backend y de los servicios administrados por su actualizador; no se eliminan datos. Si hay modificaciones incompatibles, se detiene sin sobrescribirlas. Requiere la demo ya instalada en `~/sgacd-demo/compose.json`.

Reenvía el puerto **8090**, con visibilidad **privada**. No requiere instalar WSL ni Docker en Windows; se ejecuta en el terminal del Codespace.

- `/`: landing de Analemática.
- `/sga/`: landing de SGA-CD a través del nodo corporativo.
- `/sga/login.html`: autenticación existente de SGA-CD.
- `/sga/app.html#/admin_general/crm-empresa`: CRM del dueño; incluye las solicitudes corporativas.
- `/admin.html`: administración original de Analemática con comprobación de sesión del dueño.

Cada puerto es un origen web distinto: la sesión abierta en 8080 no se copia a 8090. Inicia sesión una vez desde `/sga/login.html` en 8090 y vuelve a `/admin.html`. No se envían tokens por enlaces ni se crean usuarios o contraseñas adicionales. La autorización efectiva de datos y escritura se verifica en el backend; la página administrativa por sí sola no concede permisos.

Para otro entorno:

```bash
python3 Analematica/deployment/start.py --demo-dir /ruta/demo --port 8090
```

`--prepare-only` prepara la configuración sin actualizar ni arrancar servicios. El puerto escucha únicamente en loopback. Para producción se necesita un dominio, HTTPS y la configuración operativa del alojamiento; Codespaces proporciona una demostración privada, no disponibilidad permanente.

## Conexión y persistencia

Las rutas están bajo `/api/v1/workspace/corporate`. GET `/config` devuelve exclusivamente el contenido público publicado. PUT `/config` permite publicar al dueño, con número de revisión para impedir sobrescribir cambios de otra sesión. Los campos siguen la estructura de los formularios originales, con saneamiento de formato y enlaces. Credenciales y campos ajenos al contenido no forman parte de esta configuración pública.

El editor conserva los borradores locales; **Guardar Todo** publica en PostgreSQL y afecta a todos los visitantes. No se anuncian cambios como publicados cuando falla el servidor. Las configuraciones antiguas de localStorage no se publican automáticamente.

POST `/inquiries` requiere datos válidos y autorización expresa para atender el diagnóstico. Usa un identificador de solicitud para evitar duplicados al reintentar, un campo trampa y limitación de frecuencia en Nginx. No concede autorización para publicidad ni envíos masivos. El prospecto se guarda como `WorkspaceLead`, en el espacio `platform` del dueño; la empresa destinataria no se puede elegir desde el formulario. `created_by` identifica al responsable propietario del registro, no al visitante que lo envió. Las notas guardan el origen y los datos de la solicitud. GET `/inquiries` solo es accesible al dueño. La bandeja conserva el historial; actualizar no borra registros. Los contactos antiguos almacenados únicamente en otro navegador no se migran sin una operación explícita.

El límite de frecuencia corresponde a este nodo; si se expone directamente la API por otra entrada, debe aplicarse una protección equivalente allí. Las tablas existentes no se alteran; `corporate_pages` es adicional. El nodo no envía mensajes, correos ni videos por recibir un formulario.

## Archivos y despliegue

Frontend en `Analematica/`; configuración y despliegue en `Analematica/deployment/`; pruebas y capturas en `Analematica/tests/`. Modelo, API y pruebas de backend en `SGA-CD-BACKEND/`. Nginx solo recibe una lista explícita de archivos públicos, sin documentos internos, código de backend, tests o configuraciones privadas. Cada actualización crea una copia nueva y un respaldo privado de Compose dentro del directorio de la demo.

El acceso SGA-CD bajo `/sga/` utiliza la misma API y la misma base de datos, sin duplicar usuarios. Su service worker y manifest no se ofrecen bajo el nodo corporativo para evitar que un worker con alcance raíz controle la landing de Analemática. La entrada original de SGA-CD y las bases offline de Flet se conservan.

## Verificación

```bash
python3 Analematica/tests/deployment.py
python3 -m unittest discover -s SGA-CD-BACKEND/tests -p test_corporate_node.py
```

La segunda orden requiere las dependencias del backend y carga sus fixtures aislados de prueba. La matriz de navegador usa `Analematica/tests/node.cjs`, Playwright y Chromium. `ANALEMATICA_URL` indica el servidor; `ANALEMATICA_SESSION_FILE` es opcional y debe ser un archivo privado de una cuenta de validación local, nunca un archivo versionado. La prueba de navegador crea una solicitud claramente etiquetada de validación y restaura el contenido publicado al terminar; no publica en redes sociales.

Verificación local del 4 de noviembre de 2026: 4 pruebas de API corporativa, 2 pruebas de despliegue, 16 pruebas de paneles institucionales y 32 regresiones de workspace/campañas aprobadas. Chromium comprobó 7 recorridos con Nginx y PostgreSQL reales: anchos 1440, 768, 390 y 320; acceso administrativo anónimo; recuperación del formulario tras un error y persistencia; publicación compartida y entrada al panel de SGA-CD. El contenido de prueba se restaura al terminar. Las solicitudes de validación se identifican explícitamente y se conservan en el historial. No se enviaron mensajes ni campañas externas.

## Recuperación cuando `web` está detenido

El actualizador inicia ahora `web` explícitamente antes de comprobar y recargar Nginx. La secuencia anterior suponía que ya estaba en ejecución y podía terminar con `service "web" is not running`, interrumpiendo el alta del nodo corporativo aunque backend y nodo 6 estuvieran saludables. Arranca únicamente ese servicio, sin eliminar volúmenes ni forzar su recreación. Si el arranque falla por otra causa, se detiene e indica cómo consultar los registros; no intenta recargar una configuración que no superó `nginx -t`.

Después de actualizar la rama, vuelve a ejecutar `python3 Analematica/deployment/start.py`. Las pruebas de recuperación están en `SGA-CD-BACKEND/tests/test_web_startup.py`.

La recuperación se verificó deteniendo `web` en el entorno de validación y reproduciendo el error original antes de ejecutar el actualizador corregido. SGA-CD y Analemática respondieron HTTP 200 después; el contenido publicado, el contenedor PostgreSQL, sus volúmenes y los contenedores Flet se conservaron. Pasaron 3 pruebas de arranque, 3 regresiones del instalador y 2 pruebas de despliegue corporativo.
