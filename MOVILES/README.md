# Clientes móviles

`SGA-CD-APK.git/` contiene el cliente Flet móvil de SGA-CD.
Se conserva el nombre del directorio con APK en mayúsculas.
El traslado no modifica las bases locales ni las funciones de sincronización.

El instalador `scripts/setup_flet_previews.py` usa esta ubicación y reconoce el
montaje anterior de la raíz para actualizar solo la ruta del código. Mantiene
el volumen persistente `flet-mobile_state` y rechaza otras configuraciones
personalizadas que no coincidan. El traslado no reconstruye ni reinicia servicios.
