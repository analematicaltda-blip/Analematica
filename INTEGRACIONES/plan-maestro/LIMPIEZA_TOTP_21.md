# Limpieza de claves pendientes TOTP — corte 21

Se cerró el pendiente técnico de eliminación del material cifrado de propuestas
abandonadas. El plan maestro continúa en curso.

## Implementación

Comando `purge_totp_enrollments`, disponible mediante `fresh_manage.py`.
Simula por defecto; `--apply` elimina únicamente el campo `sealed_secret` de
propuestas vencidas o consumidas. Conserva registros y metadatos de auditoría,
autenticadores activos, contadores de uso, sesiones y propuestas aún válidas.
No requiere descifrar el material. Cada lote revalida en SQL la elegibilidad.
El tamaño predeterminado es 500 y admite de 1 a 10000; la operación es repetible.
No se programa una tarea automáticamente ni se ejecuta contra datos de clientes.

## Verificación observada

37 pruebas de sesión/MFA/activación y limpieza aprobadas en 23,7 segundos:
las 34 anteriores y tres nuevas. Las nuevas comprueban simulación sin cambios,
ausencia de secretos en la salida, conservación de propuestas válidas y factores,
lotes limitados, repetición segura y rechazo de tamaños inválidos sin escrituras.
La entrada de gestión real se comprobó en la instalación ERP temporal migrada:
`ELIGIBLE_NO_WRITE 0`. No se limpiaron bases de trabajo ni productivas.
`git diff --check` correcto. Sin cambios de interfaz y sin nuevas pruebas visuales.

## Operación pendiente

Programar y supervisar la limpieza en el entorno definitivo, con política de
retención y alertas por lotes pendientes. El borrado del campo no elimina copias
anteriores de respaldos, WAL o snapshots: su retención y custodia requieren una
política operativa. Las propuestas válidas abandonadas se vuelven elegibles al
vencer; la siguiente ejecución las limpia.

Siguen pendientes recuperación de acceso verificada, WebAuthn, teléfonos
físicos, integración central de identidad, validación completa de los módulos
y pruebas de carga. La limpieza no sustituye esas verificaciones ni certifica
el 100 % del plan. No se creó commit ni se publicó el repositorio.
