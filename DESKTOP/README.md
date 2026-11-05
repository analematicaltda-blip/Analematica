# Clientes de escritorio

`SGA-CD-APP.git/` contiene el cliente Flet de escritorio de SGA-CD.
El traslado conserva los archivos y las bases locales de la aplicación.

El instalador `scripts/setup_flet_previews.py` usa esta ubicación y reconoce el
montaje anterior de la raíz para actualizar solo la ruta del código. Mantiene
el volumen persistente `flet-desktop_state` y rechaza otras configuraciones
personalizadas que no coincidan. El traslado no reconstruye ni reinicia servicios.
