# Configuración de Meta del nodo Analemática

Los identificadores públicos confirmados están en `config/meta-public.json`.
La configuración de usuario y la de Instagram SUAT se mantienen separadas.
No introducir claves, tokens ni contraseñas en ese archivo.

El panel autenticado calcula el retorno desde `location.origin`, permite copiarlo
y precarga la aplicación sin reemplazar una configuración guardada.
El instalador `deployment/start.py` incluye los nuevos recursos públicos.

Para obtener los datos del despliegue desde el Codespace que sirve el nodo:

```bash
python3 BACKEND/ANALEMATICA-BACKEND/deployment/prepare_meta.py
```

Detecta CODESPACE_NAME y el puerto 8090. Para otro despliegue se puede declarar
ANALEMATICA_PUBLIC_ORIGIN o --origin con un origen HTTPS real. El script no abre
puertos, no cambia permisos y no realiza llamadas externas. Si no existe un
origen conocido, falla explícitamente en lugar de inventar una dirección.

## Límites actuales

Estos cambios preparan los metadatos y la URL, no completan la conexión real.
El callback de Ads y el de Instagram SUAT están separados. El flujo SUAT usa
config_id 1119082880751653, valida el token mediante debug_token, comprueba la app
y los permisos, y cifra el token. No aplica el intercambio de token de usuario
al token de sistema. La cuenta profesional se comprueba y selecciona explícitamente.

El webhook /api/v1/workspace/meta/webhooks/receive comprueba el desafío GET y la
firma HMAC SHA256 del cuerpo POST, limita el tamaño a 1 MiB, filtra los activos
permitidos y archiva cifrado con deduplicación. No responde ni publica contenido.
Este receptor inicial es exclusivo de activos del dueño (scope platform); no
conecta todavía los activos de empresas clientes. Su integración con la bandeja
CRM y los trabajadores de respuesta permanece pendiente.

Faltan credenciales reales, registro de los retornos en Meta, autorización real,
suscripción de campos de eventos y pruebas reales con el proveedor. El panel no
marca la recepción como verificada por haber guardado el verificador.
Un puerto privado de Codespaces impide que Meta valide o entregue webhooks. Se
necesita una URL HTTPS accesible; no se cambiaron puertos a públicos automáticamente.

La restricción del portafolio propietario sigue requiriendo revisión por Meta.
El entorno de Codex no equivale al Codespace del usuario: no se ha actualizado
ese servidor remoto ni se ha probado autorización real.

## Validación

```bash
python3 FRONTEND/ANALEMATICA-FRONTEND/tests/meta_setup.py
python3 FRONTEND/ANALEMATICA-FRONTEND/tests/deployment.py
node FRONTEND/ANALEMATICA-FRONTEND/tests/meta-setup.cjs
node --check FRONTEND/ANALEMATICA-FRONTEND/js/meta-ads.js
python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p test_instagram_login.py
python -m unittest discover -s BACKEND/SGA-CD-BACKEND/tests -p test_meta_webhooks.py
```

## Actualizar el Codespace existente

```bash
cd /workspaces/SGA-CD
git fetch origin codex/analematica-node
git merge --ff-only FETCH_HEAD
python3 BACKEND/ANALEMATICA-BACKEND/deployment/start.py
python3 BACKEND/ANALEMATICA-BACKEND/deployment/prepare_meta.py
```

Si Git detecta divergencia, detener la actualización y resolver preservando los
cambios existentes. No resetear ni borrar archivos. El instalador conserva bases
y volúmenes y genera un respaldo de compose. El panel es /admin.html#tab-meta-ads.

## Verificaciones locales de esta entrega

- Despliegue en /workspace/sgacd-deploy: backend y Analemática saludables; nginx -t correcto.
- Instagram: ocho pruebas de autorización, nonce/cookie, aislamiento, cifrado y errores.
- Webhooks: cuatro pruebas de desafío, firma, cifrado/deduplicación y activos/permisos.
- Regresión: cuatro pruebas corporativas y doce de consola del dueño.
- Preparación: seis pruebas Python, verificación de JavaScript y panel en Chromium
  a 1440, 768, 390 y 320 px, sin solicitudes a Meta ni desbordamiento horizontal.
- Advertencias existentes: DropdownModel duplicado y orm_mode de Pydantic.
- No se probaron envíos externos, campañas, gasto, ni consentimiento real del proveedor.
