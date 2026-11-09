# Implementación 23 · Diagnóstico de conciliación sin reescritura

**Avance: 27,78 % (20/72 hitos).** Se refuerzan ACC-004/006, ya puntuados por incremento y pruebas; no se acredita conciliación completa de los legados.

## Funcionalidad

`reconciliation.inspect_company` inspecciona cabeceras contabilizadas de una empresa en páginas de 1 a 50 y limita cada asiento a 1000 líneas verificables. Si excede el límite indica revisión separada, sin simular una validación completa.

Señala saldos iniciales no conciliados, versiones de hash legadas/desconocidas, hash v2 inconsistente, ausencia de fecha de contabilización, balance o pertenencia de líneas inválidos, plan de otra empresa, moneda de línea diferente, valoración de transacción/base inconsistente y cambios de moneda base empresarial. Usa la tasa registrada, sin consultar cotizaciones de mercado.

No modifica cabeceras, líneas, saldos, hashes ni políticas; tampoco crea asientos de apertura o ajustes. No imprime importes en el diagnóstico. Los códigos son hallazgos para revisión: por ejemplo, un campo de valoración legado pendiente de completar no demuestra por sí solo una pérdida económica. No se decide automáticamente el tratamiento contable.

Cada respuesta mantiene la serialización empresarial existente y devuelve un cursor por UUID. No mantiene un snapshot entre páginas: inserciones concurrentes pueden requerir repetir el recorrido en una ventana estable. No incluye validación global de eslabones de cadena ni certifica todo el ledger, aunque la página no tenga hallazgos. Los indicadores de alcance del resultado son explícitamente falsos para esas garantías.

## Acceso

API ERP, bajo el prefijo contable existente:

`GET cuentas/diagnostico-conciliacion/?provider_id=<UUID>&limite=20&despues_id=<UUID>`

Reutiliza titularidad, usuario activo y vínculo empresarial verificado. El rol interno restringido del núcleo también puede ejecutar la inspección.

Comando de operador: `accounting_reconciliation --tenant <UUID> --limit 20 [--after-id <UUID>]`, disponible en `fresh_manage.py`. Requiere una empresa activa según el servicio actual; no incorpora un bypass administrativo para empresas inactivas. No existe opción de aplicar reparaciones.

## Evidencia

119 métodos Python y 19 escenarios contables PostgreSQL aprobados. Los casos nuevos comprueban alcance del titular, ausencia de cambios, legados sin rehash, ausencia de divulgación de importes iniciales, paginación, límites/cursores y detección de alteración de hash/valoración. El proceso realmente autenticado con rol restringido ejecuta el diagnóstico después de posteo, contrapartida multimoneda y proyección, sin hallazgos sobre su conjunto v2 válido.

Evidencia: `evidencias/implementacion-23.json`. No hay migraciones ni cambios de esquema.

## Pendientes

Interfaz de diagnóstico, snapshot estable entre páginas, revisión autorizada de empresas inactivas, conciliación contable documentada, asientos de apertura/ajustes aprobados, tratamiento de legados y fuentes reales. Los registros no se deben reescribir ni los saldos iniciales poner a cero para hacer desaparecer hallazgos. Continúan integración corporativa de Analemática y demás pools. Sin cambios de datos del usuario, commit o push.
