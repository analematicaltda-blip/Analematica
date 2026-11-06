# Clientes de escritorio

`SGA-CD-APP.git/` contiene el cliente Flet de escritorio de SGA-CD.
El traslado conserva los archivos y las bases locales de la aplicación.

El instalador `scripts/setup_flet_previews.py` usa esta ubicación y reconoce el
montaje anterior de la raíz para actualizar solo la ruta del código. Mantiene
el volumen persistente `flet-desktop_state` y rechaza otras configuraciones
personalizadas que no coincidan. El traslado no reconstruye ni reinicia servicios.

## Automatización local para agentes

`agent-desktop/` contiene la copia completa del proyecto de Vercel Labs bajo
Apache 2.0. `agent-desktop-sgacd/` contiene el instalador y conector MCP de SGA-CD.
Consulta su README para instalarlo en el equipo cuyo escritorio quieres operar.
