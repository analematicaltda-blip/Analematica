# Implementación 18 · Disponibilidad condicionada a las protecciones SQL

**Avance verificable: 27,78 % (20/72 hitos).** ACC-024 incorpora un incremento operativo —verificación de controles de base antes de declarar disponibilidad— y sus pruebas automatizadas. Es distinto de los triggers de ACC-007: aquí se comprueba que sigan presentes/activos y se informa la indisponibilidad. No se acredita aceptación completa, recuperación integral ni habilitación productiva; no cambia la base de 24 tareas.

## Control operativo

La comprobación `/readyz` integra una inspección de los controles contables si están presentes las tablas del núcleo. SQLite comprueba nombres, asociación a tabla y existencia de definición; PostgreSQL comprueba presencia, estado activo para operaciones normales, eventos/tipo, función asociada, ausencia de argumentos/condiciones/restricción de columnas y coherencia de esquema. Si falta un control, está deshabilitado o su estructura no corresponde, devuelve `not_ready` y el HTTP existente responde 503. No instala ni repara controles desde la consulta.

La inspección es estructural, no una atestación del texto de las funciones. Un propietario capaz de reemplazar cuerpos, desactivar controles, manipular catálogos o restaurar otro archivo sigue fuera de esta garantía. El despliegue real debe conectar su orquestador a readiness y conservar una comprobación de privilegios/definiciones independiente. La respuesta 503 de readiness no bloquea por sí sola todas las APIs ni reemplaza permisos.

## Endurecimiento de PostgreSQL

Se detectó que la consulta del padre usaba un nombre de tabla no cualificado. La migración aditiva `core_erp.0006_accounting_guard_schema`, en los árboles nativo/fresh, resuelve el padre en `TG_TABLE_SCHEMA` y usa `pg_catalog.format` con identificadores y UUID parametrizado. Una tabla temporal homónima no puede sustituir la cabecera del ledger en esta comprobación.

Se conserva la migración anterior; no se cambian filas, importes ni hashes. SQLite no necesita ese parche de esquema. La reversión vuelve a los controles v1 y reduce esta protección; requiere evaluación operativa antes de aplicarse. El grafo nativo histórico y los privilegios reales siguen pendientes de ensayo.

## Evidencia

- 106 métodos Python del perfil contable aprobados: incluye detección de control faltante, ausencia de reparación automática y control asociado a una tabla incorrecta.
- 15 escenarios contables PostgreSQL: detección de trigger deshabilitado, habilitación restaurada y modificación de línea bloqueada aun con cabecera temporal homónima.
- 12 regresiones de instalación ERP, incluida retirada temporal de un trigger, HTTP 503, comprobación de que la consulta no lo recrea y retorno a ready tras rollback del fixture.
- Ocho pruebas previas de readiness aprobadas, sin fuga de detalles internos ni ejecución de migraciones.

La migración solo se aplicó a la instalación privada de pruebas; PostgreSQL utiliza una base desechable. Evidencia: `evidencias/implementacion-18.json`.

## Pendientes

Verificación de cuerpos/firma independiente, separación de roles DDL/DML y privilegios mínimos; pruebas de restauración integral de ledger y claves cliente, RPO/RTO y configuración real del orquestador; ensayo de migraciones históricas y revisión independiente. Continúan la integración contable corporativa Analemática y los demás pools. No se modificaron bases del usuario ni servidores reales; sin commit ni push.
