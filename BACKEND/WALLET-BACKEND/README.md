# BACKEND/WALLET-BACKEND

Ubicación canónica de la billetera:

- `apps/wallet/`: aplicación Django, modelos, APIs, autorizaciones y verificación de dispositivos.
- `fresh_migrations/wallet/`: migraciones del perfil local nuevo, sin cambiar nombres/etiqueta ni el historial de bases.
- `BACKEND/tests/`: pruebas financieras, de dispositivos y atestación antes alojadas en deployment/tests.
- `offline/`: paquete `sgacd-wallet-offline`, caché AES-256-GCM de apuntes/borradores y ocho trabajadores de reglas locales.
- `tools/update_pending_doc.py`: genera y comprueba el registro humano de pendientes.
- `move-inventory.json`: rutas anteriores/nuevas y SHA-256 anterior para revisión de la reubicación.

`apps.wallet` y `fresh_migrations.wallet` conservan pequeñas entradas de compatibilidad en las rutas previas. No son otro repositorio ni una segunda copia de los servicios; apuntan a estos archivos del mismo checkout. La etiqueta Django sigue siendo wallet y las tablas existentes conservan sus nombres. Docker incluye esta carpeta en los servicios turísticos. No se movieron bases SQLite, credenciales, llaves ni el grafo histórico de migraciones.

Los informes históricos del plan maestro se conservan en `INTEGRACIONES/plan-maestro`; las vistas React originales de los otros sistemas no se reescriben ni se presentan como conectadas a los clientes nuevos.

## Comprobar desde la raíz

```sh
python BACKEND/WALLET-BACKEND/tests/wallet_security_check.py -v
python BACKEND/WALLET-BACKEND/tests/device_approval_check.py -v
python BACKEND/WALLET-BACKEND/tests/attestation_security_check.py -v
python -m unittest discover -s BACKEND/WALLET-BACKEND/offline/tests -v
python BACKEND/WALLET-BACKEND/tools/update_pending_doc.py --check
```

Las tres primeras usan el entorno Django de deployment; la suite offline usa sus dependencias propias. Ninguna debe apuntar a producción. Los ejecutables anteriores de deployment/tests siguen funcionando como adaptadores de compatibilidad.

## Límites del modo offline

Se guardan y consultan apuntes y borradores reales ingresados por el usuario. Se puede modificar un borrador y realizar dos revisiones locales del mismo espacio; modificarlo reinicia ambas. Se conservan identidad local y estado cifrados, no tokens bancarios, claves privadas de hardware o saldos supuestamente confirmados.

El espacio local **no autentica al administrador financiero**. La preparación para el servidor contiene únicamente source/destination/amount/currency/idempotency_key; nunca se convierte una revisión local en device_proof o confirmation. No hay envío automático ni liquidación fuera de internet. Para mover fondos hacen falta sesión verificada, intención nueva y las dos firmas frescas del backend, además de todas las validaciones pendientes.

La contraseña local debe tener12–128 caracteres; PBKDF2-SHA256/600000 deriva una llave distinta de las financieras, con salt aleatorio y nonces GCM nuevos. El blob incluye AAD de espacio/revisión, límite1MiB y control optimista para impedir sobrescrituras concurrentes. No hay reinicio automático ante contraseña equivocada o archivo alterado. La protección contra rollback completo del dispositivo no se acredita con este caché: precisamente por eso no otorga autoridad financiera.

En POSIX se exigen directorios700/archivos600. En Windows se utiliza el perfil de aplicación y herencia del SO; la validación de ACL y almacenamiento nativo sigue pendiente. El borrado de buffers Python/Java/Swift es un esfuerzo limitado, no una garantía de eliminación física. Proteger y respaldar el espacio; perder la contraseña no genera una recuperación automática.

Pendientes y criterios únicos: [PENDIENTES-PRODUCCION-BILLETERA.md](../../ANALISIS/produccion/PENDIENTES-PRODUCCION-BILLETERA.md).
