# Implementación 17 · Inmutabilidad del ledger en la base de datos

**Avance: 25,00 % (18/72 hitos).** Refuerza ACC-002 y ACC-007, ya puntuados por incremento y verificación. No acredita su alcance completo ni despliegue productivo.

## Protección añadida

Migración aditiva `core_erp.0005_accounting_sql_guards`, en los árboles nativo y fresh. Instala triggers v1 en PostgreSQL o SQLite. No cambia filas, hashes ni saldos existentes.

- Rechaza UPDATE/DELETE de cabeceras ya contabilizadas, incluido intentar descontabilizarlas o actualizar solo su descripción.
- Rechaza INSERT/UPDATE/DELETE de líneas cuyo asiento ya está contabilizado; impide reasignar líneas a otra cabecera.
- Obliga a crear cabeceras nuevas como borradores, antes de contabilizar.
- Rechaza UPDATE/DELETE de políticas históricas de clasificación; permite insertar nuevas revisiones.
- PostgreSQL rechaza TRUNCATE de las tres tablas, incluso solicitado con CASCADE.

El servicio normal puede seguir creando borradores, valorando líneas, contabilizando, respondiendo a reintentos idempotentes y creando contrapartidas nuevas. PostgreSQL bloquea la cabecera al comprobar el estado de una línea. Mutaciones SQL concurrentes fuera del servicio pueden ser rechazadas por los triggers o por resolución de bloqueos; no deben tratarse como una interfaz de edición admitida.

La reversión de la migración retira explícitamente los controles, sin borrar datos. No debe usarse como mecanismo operativo de edición. Cambios futuros de esquema o reconstrucción de tablas requieren comprobar que los triggers continúan instalados. La implementación v1 debe conservarse al añadir versiones posteriores de migración.

## Frontera de seguridad

No es blockchain, firma independiente ni protección frente a un propietario/superusuario capaz de desactivar triggers, alterar funciones, editar el archivo SQLite o restaurar una base diferente. Tampoco valida por sí sola toda la transición de borrador a contabilizado mediante SQL directo: el posteo autorizado debe seguir usando LedgerEngine. No impide todavía todos los cambios SQL sobre cuentas, periodos, auditoría o recibos. Faltan separación de roles DDL/DML, privilegios mínimos, verificación de instalación, auditoría independiente y ensayo del grafo nativo histórico.

Los controles no certifican que los datos legados ya congelados sean correctos; se mantienen los pendientes de conciliación y apertura. No se reescribe su historia.

## Pruebas

Se instaló la migración únicamente en el fixture privado de instalación ERP. Se verificó ausencia de deriva de modelos, idempotencia de migración y 11 regresiones de esa instalación.

Se añadieron seis pruebas SQLite con triggers realmente instalados, operaciones SQL/bulk que eluden el ORM, inserción directa de cabecera contabilizada, políticas históricas, instalación idempotente/reversión explícita y contabilización/reversión normales.

La suite PostgreSQL aislada añade un contrato de 11 operaciones bloqueadas —incluido TRUNCATE— y comprueba contabilización y contrapartida con integridad válida. La primera ejecución detectó que faltaba un periodo fiscal en el nuevo fixture; se añadió el periodo y se repitió la verificación. Resultados finales en `evidencias/implementacion-17.json`.

No se tocaron bases del usuario, servidores productivos o cuentas reales. Sin commit ni push.
