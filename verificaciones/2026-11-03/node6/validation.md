# Nodo 6: implementación y validación

Se añadió un servicio privado independiente, sin modificar bases locales Flet,
la lógica de sincronización, archivos protegidos de la landing ni fuentes de
Matrix-OS/Colibrí. Se corrigió la documentación para explicitar offline-first.
.gitmodules registra las URLs oficiales de ambos submódulos, conservando gitlinks.

El nodo sirve el estudio web en 8606, exige una credencial propia para las
operaciones y los archivos y conserva secretos fuera del checkout. Gemini usa
cabecera x-goog-api-key y errores redactados. Se solicita texto/imagen a modelos
configurables. El render local produce MP4 reales 1080x1920 con FFmpeg y textos
rasterizados mediante Pillow, sin interpolarlos como filtros/comandos de shell.

YouTube está limitado a privacidad private, exige clasificación del contenido y
confirmación explícita. Se valida el destino de subida antes de enviar el token.
El registro de solicitudes evita repetir un envío; no hay reintento automático
ante resultado incierto. La publicación no forma parte de las herramientas MCP.
No se realizaron envíos reales.

Resultados locales:
- 7 pruebas de worker: autenticación/redacción, texto e imagen Gemini simulados,
  protocolo Colibrí con catálogo simulado, render real verificado con ffprobe,
  rutas/límites, borrador y subida privada/duplicados YouTube simulados.
- 1 prueba de preparador: servicios, volúmenes y credenciales preservados,
  permisos 0600, repetición sin cambios y rechazo de configuración personalizada.
- Imagen Docker construida y contenedor healthy, 127.0.0.1:8606.
- SDK MCP instalado en Matrix: initialize/listTools/callTool reales sobre HTTP y
  puente stdio. Esto no certifica registro ni ejecución en el agente Matrix.
- Chromium 1440/390: autenticación, ausencia de desbordamiento, reproducción de
  MP4 generado realmente, borrador y confirmación/clasificación de subida privada.
- CLI: descarga real de un reel de 4 segundos fuera del checkout.

Compose solicita 768 MiB y 1 CPU. El entorno Docker administrado no ofrece
contabilidad de cgroups aislada fiable (stats mostró memoria global y top falló);
no se afirma que esos límites estén aplicados aquí. Uvicorn reportó 63848 kB de
RSS en reposo tras renderizar; no es una medición de pico ni una garantía de coste.
Se retiraron únicamente tres contenedores de validación redundantes, preservando
volúmenes. Los nodos Flet actuales 8501/8502 y los servicios existentes siguen activos.

Límites observados, no ocultados con mocks:
- Gemini API falló en CONNECT del proxy con HTTP403, antes de enviar una clave.
  El valor expuesto en el chat no se guardó ni se probó contra el proveedor.
- Se guardó un borrador de red con generativelanguage.googleapis.com,
  oauth2.googleapis.com y www.googleapis.com, conservando las reglas existentes,
  y requisito GEMINI_API_KEY. requires_publish=true: no es configuración aplicada.
- No hay llamada de inferencia Gemini ni generación de imagen reales verificadas.
- Los reels son montajes FFmpeg; no se implementó generación de movimiento con Veo.
- Falta OAuth youtube.upload del canal; subida verificada solo con transporte simulado.
- Matrix: fragmento de registro preparado; su kernel/configuración siguen pendientes.
- Colibrí: no se descargaron pesos y no se afirma inferencia local.
- No se controló el terminal del Codespace del usuario ni se verificó Actions remoto.

Operación y autorización de canal: docs/NODO6.md.
