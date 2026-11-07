# Clientes móviles

`SGA-CD-APK.git/` contiene el cliente Flet móvil de SGA-CD.
Se conserva el nombre del directorio con APK en mayúsculas.
El traslado no modifica las bases locales ni las funciones de sincronización.

El instalador `scripts/setup_flet_previews.py` usa esta ubicación y reconoce el
montaje anterior de la raíz para actualizar solo la ruta del código. Mantiene
el volumen persistente `flet-mobile_state` y rechaza otras configuraciones
personalizadas que no coincidan. El traslado no reconstruye ni reinicia servicios.

El puente propio de cifrado local está en
[`pool-01-cryptography/flet_bridge`](../pool-01-cryptography/flet_bridge/README.md).
Expone solo metadatos a Flet; conserva documentos y llaves en el cliente nativo.
No está activado en `main.py`: requiere un cliente móvil firmado con la extensión,
pruebas físicas y el vínculo real de organización/cuenta autenticadas. Los IDs
académicos existentes no se convierten automáticamente en identidades financieras.
