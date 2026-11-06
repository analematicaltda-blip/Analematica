# Asistencia SGA-CD: Open Duet + agent-desktop

El código completo de Open Duet está en `../open-duet`, con 1.172 archivos del commit
`6ec8e0c8360c8f8b6cc282b9d6ec5f563d351b56`. Es una copia real, no un submódulo,
y conserva Apache-2.0, avisos y sus componentes backend, frontend, desktop y mobile.
`open-duet-upstream.json` fija los blobs, modos y SHA-256 de cada entrada. La copia
original de `../agent-desktop` (3.746 archivos) también se conserva intacta.

Este conector une ambos proyectos con el motor interno
`BACKEND/SGA-CD-BACKEND/app/services/assistance`. Comparte su catálogo y política,
prepara un perfil de Open Duet y ofrece un MCP local limitado a asistencia.
No fusiona dependencias o bases de datos de los productos ni agrega privilegios al
agente de este chat. Copiarlo no conecta el portátil ni inicia servicios de Meta.

## Probar la guía

La interfaz usa la cuenta SGA-CD existente y está en `/assistance.html` de las vistas
locales de SGA-CD y Analemática. Tiene 42 guías iniciales y 252 pasos; se amplía en el
catálogo versionado. No representa todas las pantallas presentes o futuras.
Consulta el README del motor para API, esquema, sesión y configuración de Open Duet.

## Puente local sin dependencias npm

Usa Node 22+ en el equipo que vas a observar. Para instalar el runtime oficial de
agent-desktop ya preparado para este repositorio:

```bash
node DESKTOP/agent-desktop-sgacd/install.mjs
node DESKTOP/agent-desktop-sgacd/run.mjs doctor
node DESKTOP/asistencia-sgacd/verify-source.mjs
node DESKTOP/asistencia-sgacd/config.mjs vscode
```

`config.mjs` también genera `claude` o `codex`. Imprime configuración con la ruta
absoluta del MCP; no modifica la configuración privada/global de ningún cliente.
Aplica el bloque en un perfil dedicado de asistencia, conservando sus revisiones
normales de herramientas. El proceso MCP se inicia así:

```bash
node DESKTOP/asistencia-sgacd/mcp.mjs
```

Sus herramientas son únicamente:

- `assistance_catalog`: lista las guías sin acceder a cuentas.
- `assistance_workflow`: lee los pasos de una guía.
- `assistance_desktop_status`: permisos/versión del runtime local, sin leer ventanas.
- `assistance_observe_window`: entrada heredada que rechaza observar; remite al panel con autorizaciones.

No hay herramientas de click, teclado, clipboard, shell genérico, mensajes o gastos.
La lista de comandos nativos está fijada en el servidor y se ejecuta sin shell,
con tiempo y tamaño de salida limitados. Un argumento del modelo no puede elegir
otro comando, ventana o archivo de salida. No se usa `--headed` ni se toman screenshots.
El conector general `agent-desktop-sgacd` conserva capacidades más amplias: **no lo
incluyas como herramienta del perfil limitado si quieres mantener esta separación**.

### Control con autorizaciones

La observación por variables de entorno está deshabilitada. El panel `/control.html`
y el ejecutor verificador implementan el control de escritorio y aplicaciones
Android/iOS, con dos autorizaciones del mismo administrador y una tercera para
interacciones que pueden modificar datos. Consulta [CONTROL.md](CONTROL.md) para
instalación, límites, revocación y pruebas físicas pendientes; [SOURCES.md](SOURCES.md)
explica las alternativas investigadas. Ningún modelo tiene una herramienta para
aprobar sus propias acciones.

## Perfil de Open Duet

El Open Duet copiado incluye instrucciones de instalación en su README; requiere
Python 3.14+, uv, Node 22+ y un motor/proveedor propio. No se instaló Electron ni se
inició un proveedor de IA en este entorno.

```bash
node DESKTOP/asistencia-sgacd/prepare-duet.mjs
```

Crea solamente `.runtime/workspace` y `agent-profile.json`: política, catálogo y
configuración MCP del perfil especializado. No inicia un modelo ni solicita claves.
Para registrarlo por su API, usa `--register` después de configurar `OPEN_DUET_URL`
(origen loopback) y `OPEN_DUET_TOKEN` (token autorizado de tu instancia) fuera de Git.
`OPEN_DUET_ENGINE` selecciona un motor instalado, por defecto `codex`. No se imprime
ni guarda el token. Una inscripción existente se verifica y no se duplica ni cambia
si el usuario alteró sus permisos o workspace.

El registro es local y requiere que Open Duet vea ese workspace en el mismo host.
El agente se crea en modo **plan**, sin memoria/helper/líder automáticos. Algunos
motores no cargan o rechazan herramientas MCP en planificación; en ese caso el
catálogo local y el motor web siguen disponibles. No se aumenta a Ask/Accept edits
para forzar herramientas. Una conexión con Composio no es requisito de estas guías
ni se instala silenciosamente. El adaptador de preguntas desde SGA-CD es opcional,
requiere consentimiento y tiene asignación explícita usuario/tenant para no compartir
una instancia personal entre empresas.

## Pruebas y procedencia

```bash
node --test DESKTOP/asistencia-sgacd/tests/*.test.mjs
```

La prueba nativa adicional usa `SGACD_ASSISTANCE_TEST_NATIVE=1` después de instalar
agent-desktop en la máquina de prueba. Solo pide `status`, no captura una ventana.
Se probaron siete casos del puente (incluido estado real Linux), siete tests
originales de Open Duet y el contrato de sus schemas reales. La integración HTTP
con un proveedor se validó con respuestas controladas; no está cualificada en vivo.
`verify-source.mjs` comprueba todas las entradas de Open Duet sin modificar sus fuentes.
