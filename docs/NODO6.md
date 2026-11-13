# Nodo 6: estudio de pruebas con Gemini, Matrix-OS y Colibrí

El nodo usa Gemini por API: no descarga pesos y puede funcionar en el Codespace
actual de dos núcleos. Los identificadores iniciales son `gemini-2.5-flash` para
texto y `gemini-2.5-flash-image` para imágenes; son configurables y su disponibilidad
se debe comprobar con la cuenta real. No se afirma que esos modelos estén incluidos
en una cuota gratuita ni que la clave proporcionada en el chat sea válida.

## Estado comprobado

| Función | Estado |
| --- | --- |
| Estudio web, acceso privado y descarga de archivos | Probados en 1440 y 390 px |
| Reel MP4 1080 × 1920 con FFmpeg | Render y reproducción reales verificados |
| Gemini: guiones e imágenes | Adaptador probado con respuestas simuladas; falta llamada real |
| Video generativo con Veo | No implementado; una clave de Gemini no lo habilita por sí sola |
| YouTube privado | Envío implementado y probado con transporte simulado; falta autorizar el canal |
| MCP para Matrix-OS | Inicialización, herramientas e invocación probadas con su SDK instalado, por HTTP y stdio |
| Registro en Matrix y ejecución de su agente | Pendiente; no se sustituyó su kernel |
| Colibrí | Adaptador OpenAI preparado; no hay inferencia local sin un modelo instalado |

Matrix-OS conserva su arquitectura de agentes y configuración propia; una clave
Gemini no reemplaza automáticamente las credenciales de su kernel. El puente MCP
permite solicitar tareas al nodo. Colibrí sigue siendo un motor local separado:
**Gemini no se ejecuta dentro de Colibrí**. No se retoman las descargas anteriores
de Qwen o GLM.

Las bases SQLite de móvil/escritorio se conservan para trabajar sin internet.
Su sincronización con el servidor no se sustituye por el nodo 6 ni se modifica en
esta entrega. Esta prueba no certifica esa sincronización.

## Arrancar en el Codespace existente

```sh
python3 BACKEND/tools/start_node6.py
python3 BACKEND/tools/node6_client.py status
```

En **Puertos**, agrega **8606**, conserva **Private** y abre su dirección reenviada.
Para obtener la clave de acceso del estudio, solo en tu terminal privado:

```sh
python3 BACKEND/tools/node6_client.py access
```

Cópiala en «Clave privada de acceso al nodo». No es la clave de Gemini ni debe
pegarse en el chat. El navegador la conserva solo en memoria, no en URL ni en
almacenamiento local. La API y los archivos requieren esa clave; salud y los
archivos estáticos del estudio no exponen credenciales.

El preparador añade únicamente el servicio `node6`, respalda Compose y conserva
servicios y volúmenes existentes. Se puede repetir; una configuración distinta
del servicio se rechaza. El volumen `node6_state` guarda archivos y registro de
envíos. No ejecutar `down -v`.

Este es un nodo privado para pruebas de operador, no un servicio público
multiinquilino. Su acceso no sustituye JWT, roles ni planes del backend comercial.

## Configurar Gemini

Crea o reemplaza la clave expuesta usando https://aistudio.google.com/apikey.
La suscripción o la aplicación de Gemini no equivalen necesariamente a acceso a
los modelos de la API. Guarda la nueva clave mediante entrada oculta:

```sh
python3 BACKEND/tools/start_node6.py --set-gemini-key
python3 BACKEND/tools/node6_client.py models
```

El archivo privado `~/sgacd-demo/node6/node6.env` tiene permisos 0600. Ninguna
credencial se copia a la imagen o al repositorio. Si el entorno administrado ya
proporciona `GEMINI_API_KEY`, se importa solo cuando el campo privado está vacío.
Para cambiar modelos, edita `GEMINI_TEXT_MODEL` y `GEMINI_IMAGE_MODEL` en ese archivo
usando identificadores disponibles en la respuesta de `models`, sin `models/`.
Repite el arranque para aplicar cambios.

```sh
python3 BACKEND/tools/node6_client.py script --prompt 'Escribe un guion de 15 segundos para invitar a un taller cultural'
python3 BACKEND/tools/node6_client.py image --prompt 'Cartel deportivo azul cielo y azul oscuro, sin texto'
python3 BACKEND/tools/node6_client.py reel --title 'Talleres culturales' --caption 'Conoce nuestras actividades'
```

Los reels de esta versión son montajes con plantilla y opcionalmente una imagen
generada. **No se presentan como video generativo ni como material filmado.**
El cliente descarga los resultados en `~/sgacd-demo/node6/downloads`.

En este entorno de Codex, el acceso a Gemini falló antes de enviar credenciales:
CONNECT del proxy devolvió 403. Se guardó un borrador con
`generativelanguage.googleapis.com`, `oauth2.googleapis.com` y `www.googleapis.com`,
conservando las reglas anteriores, y el requisito privado `GEMINI_API_KEY`.
Guardar ese borrador no aplica la red: revisa, guarda y publica desde la
configuración del entorno para realizar pruebas reales desde aquí. En un entorno
administrado con CA de proxy puede usarse `--proxy-ca /ruta/al/bundle.pem`;
se mantiene la verificación TLS. Codespaces normalmente no necesita ese argumento.

## YouTube: exclusivamente videos privados

La clave de Gemini no autoriza tu canal. Necesitas habilitar **YouTube Data API v3**
en tu proyecto Google, configurar consentimiento OAuth para tu usuario de prueba
y obtener `client_id`, `client_secret` y un `refresh_token` con el permiso
`https://www.googleapis.com/auth/youtube.upload`.

Para una prueba manual sin desarrollar otra pantalla de consentimiento puede
utilizarse la herramienta oficial https://developers.google.com/oauthplayground:

1. Crea un cliente OAuth **Web** en Google Cloud y registra
   `https://developers.google.com/oauthplayground` como URI de retorno.
2. En el engranaje de OAuth Playground activa **Use your own OAuth credentials**
   e introduce las credenciales de tu propio cliente.
3. Autoriza únicamente el permiso `youtube.upload` con la cuenta/canal de destino
   y canjea el código. Copia el refresh token al preparador privado, nunca al chat.

```sh
python3 BACKEND/tools/start_node6.py --set-youtube-oauth
```

La pantalla del estudio permite clasificar si el contenido está creado para niños,
confirmar el envío y subir. La API fija `privacyStatus=private`, no admite un
parámetro público/unlisted, verifica la privacidad devuelta y evita repetir la
misma solicitud. Ante un resultado incierto se exige comprobar el canal antes de
repetir: no se hacen reintentos de subida automáticos.

También se puede preparar un borrador sin autorizar ninguna cuenta:

```sh
python3 BACKEND/tools/node6_client.py draft --filename NOMBRE_DEL_REEL.mp4
```

Sustituye `NOMBRE_DEL_REEL.mp4` por el nombre devuelto al renderizar. Para una
subida real autorizada, selecciona explícitamente la clasificación apropiada:

```sh
python3 BACKEND/tools/node6_client.py upload-private --filename NOMBRE_DEL_REEL.mp4 --made-for-kids no
```

Ese último comando envía contenido: úsalo solo después de autorizar y comprobar tu
canal y de elegir la clasificación correcta. No se realizó ninguna publicación
real durante esta implementación. Las demás redes solo tienen borradores.

## Conectar Matrix-OS y Colibrí

Se incluye `.gitmodules` con los repositorios oficiales, conservando los gitlinks
existentes. Si necesitas restaurar su código fuente:

```sh
git submodule update --init matrix-os colibri
```

Esto restaura fuentes; no instala modelos ni configura el kernel de Matrix.
El preparador genera `~/sgacd-demo/node6/matrix-mcp.json`, un fragmento MCP stdio
que ejecuta `BACKEND/tools/node6_mcp_stdio.py`. El puente lee la credencial desde el
archivo privado, sin incrustarla en la configuración del cliente. Incorpóralo
mediante el mecanismo MCP admitido por tu cliente/SDK Matrix. No se sobrescribe
la configuración ni la proyección administrada de Matrix y no se afirma que el
agente Matrix ya esté ejecutando estas herramientas. La publicación de YouTube
no se expone como herramienta MCP: requiere una acción explícita del operador.

Herramientas: estado, guion, imagen, reel y borrador. El SDK instalado en Matrix
verificó ambos transportes. La invocación del agente completo sigue requiriendo
su configuración y credenciales.

Si más adelante hay un Colibrí con un modelo compatible realmente cargado,
configura `COLIBRI_BASE_URL` y, si corresponde, `COLIBRI_API_KEY`. El adaptador
consulta `/v1/models` para usar el ID anunciado, y envía texto a
`/v1/chat/completions`. No prueba ni supone compatibilidad de un GGUF concreto.

## Pruebas

- `BACKEND/tests/node6/test_node6.py`: proveedor simulado, errores sin credenciales en
  mensajes, imagen válida, reel real/ffprobe, límites y rutas de archivo,
  protocolo Colibrí simulado, privacidad y duplicados YouTube simulados.
- `BACKEND/tests/node6/test_setup.py`: preservación de servicios, volúmenes y credenciales.
- `BACKEND/tests/node6/mcp.cjs`: SDK MCP instalado en Matrix, HTTP y stdio.
- `BACKEND/tests/node6/studio.cjs`: estudio real, vista móvil/escritorio, reel y borrador.

No se modifican los archivos protegidos de la landing, el panel de administrador,
las bases locales Flet ni los repositorios internos de Matrix/Colibrí.
