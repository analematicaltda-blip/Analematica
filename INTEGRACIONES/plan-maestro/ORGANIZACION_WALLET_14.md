# Organización y clientes offline de la billetera

Las fuentes se centralizan en WALLET-BACKEND, WALLET-FRONTEND, WALLET-MOVIL y WALLET-DESKTOP en la raíz. Inventario de138 archivos reubicados con SHA anterior: `WALLET-BACKEND/move-inventory.json`. Se preservan imports apps.wallet, etiqueta/modelos y nombres de migración mediante adaptadores mínimos; Docker/CI apuntan al nuevo código. No se trasladan bases, credenciales o llaves. Los informes anteriores conservan sus rutas históricas de referencia; usar los README nuevos para comandos actuales.

Se implementan aplicaciones Flet compartidas para apuntes y borradores cifrados. Un caché local separado de las llaves financieras usa AES256-GCM/PBKDF2, nonces nuevos, límite de tamaño y revisión optimista de concurrencia. Se bloquea al salir, por inactividad y ante transporte web; un desbloqueo que coincide con el cierre no resucita la sesión. Se exigen revisiones locales separadas y se reinician al editar. No son firmas del servidor; no existe pago desconectado ni cola de liquidación automática.

Ocho trabajadores de reglas locales y ocho perfiles limitados/MCP se apoyan en el conector existente Open Duet/agent-desktop. El conector solo expone equipo, pendientes, política y diagnóstico fijo. No aprueba ni ejecuta pagos o acciones genéricas. Los perfiles no se registraron en un proveedor ni se vincularon con equipos físicos; ese paso conserva sus autorizaciones y pendiente específico.

El panel web de consulta funciona con archivos locales, sin CDN ni campos de contraseña o rutas privadas. Se probó en Chromium con red externa bloqueada, navegación, búsqueda y viewport móvil. La vista Flet web opcional no pudo renderizar sin CanvasKit/fuentes externas; está registrado como pendiente de empaquetado, no como UI Flet offline acreditada.

## Evidencia

- 131 ejecuciones Python correctas:7 política de acceso,28 atestación,15 billetera,13 protocolo/imports anteriores,18 bases migradas,15 caché/ejército offline,10 interfaz Flet,11 puente y14 comprobación de distribución.
- Cuatro pruebas Node del conector y una suite visual Chromium sobre el panel de consulta sin solicitudes externas.
- 283 aserciones Java de los cuatro pools (232 cifrado,9 mensajes,16 integridad,26 red) y cinco escenarios TLS reales en loopback.
- Tres wheels construidos: offline0.1.0, UI0.1.0 y puente nativo0.4.0;19 recursos canónicos comprobados. No son APK/IPA/EXE.
- Dos bases locales siguen en166 migraciones/587 tablas. No hubo migración nueva ni modificación productiva por reubicar código.

Registro vivo: `PENDIENTES-PRODUCCION-BILLETERA.md`, generado del JSON canónico y mostrado también en clientes/panel.18 puntos abiertos con responsable, aceptación y evidencia. Binarios/ACL/hardware, cuenta financiera, confianza real, proveedor local y automatización autorizada siguen pendientes; no se declara producción habilitada.

## Aclaración de acceso

Alta personal voluntaria para cualquier persona de Colombia. Solo el administrador
empresarial verificado puede gestionar la billetera de su empresa. El equipo
administrativo conserva únicamente su perfil personal si se inscribe.
Ver WALLET-BACKEND/ACCESS-MODEL.md y pendiente WAL-019: el adaptador real y
los paneles empresariales siguen pendientes, cerrados por defecto.
