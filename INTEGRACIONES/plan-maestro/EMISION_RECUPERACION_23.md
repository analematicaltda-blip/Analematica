# Emisión y rotación de códigos de recuperación — corte 23

Se completó el flujo web de emisión de códigos para cuentas ERP con TOTP.
No se declara completo el plan maestro ni la recuperación con pérdida de ambos factores.

## Implementación

POST /api/v1/erp-session/recovery/issue/ exige una sesión MFA personal,
CSRF, contraseña actual y un TOTP fresco. El contador aceptado al iniciar sesión
no se puede utilizar para emitir. Los fallos comparten el bloqueo persistente
del factor. Se comprueba la política y se rechazan otros tipos de factor.

La operación bloquea usuario, factores y contador, cifra una semilla nueva y
sustituye únicamente los códigos de recuperación de la cuenta solicitante.
Los anteriores quedan invalidados. Se rota la sesión y se registra la versión
nueva de factores, manteniendo los permisos y TOTP.

La respuesta no-store entrega los códigos una vez; no existe lectura posterior
por GET. La UI requiere confirmar la invalidación, solicita contraseña/TOTP y
oculta el conjunto al cambiar de pestaña, después de un minuto o al confirmar
que se guardó. No los guarda en localStorage ni servicios externos. Esto no
impide capturas ni acredita borrado físico de memoria JavaScript.
Una respuesta perdida puede corresponder a una emisión completada; la UI lo
advierte y no reintenta automáticamente ni intenta recuperar los códigos.

ERP_RECOVERY_ISSUANCE_ENABLED está apagado por defecto. Requiere también
ERP_WEB_SESSION_ENABLED y ERP_RECOVERY_CODES_ENABLED. No se habilitaron cuentas
reales, no se enviaron mensajes y no se tocaron bases de clientes.

## Evidencia

- 48 pruebas de sesión, MFA, activación, limpieza y recuperación aprobadas:
  cinco nuevas cubren emisión fresca, cifrado/rotación de sesión, regeneración
  que invalida códigos anteriores, contraseña/CSRF y bloqueo persistente.
- 27 regresiones de identidad y cotizaciones aprobadas.
- Cinco pruebas del gateway aprobadas.
- 22 comprobaciones HTTPS con React, Django y Nginx, incluyendo emisión con
  prueba nueva, ocultación y posterior ingreso con un código recién emitido.
- TypeScript estricto y empaquetado incluidos; vista móvil de 390 px sin
  desbordamiento, azul metalizado/celeste y texto blanco conservados.
- git diff --check correcto; sin nuevas migraciones.

Las pruebas utilizan usuarios y secretos sintéticos. La concurrencia de emisión
en PostgreSQL y múltiples procesos no está acreditada por estos resultados.

## Pendientes para producción

Auditoría y notificaciones de emisión/uso sin registrar códigos; validación
concurrente PostgreSQL; autenticadores físicos; custodia/rotación de claves;
recuperación cuando se pierden ambos factores; contraseña por canal verificado;
identidad común y módulos restantes de los tres productos. Las autorizaciones
del motor y las firmas de billetera siguen siendo independientes.
Sin commit, push ni publicación. Ver issuance-evidence-23.json.
