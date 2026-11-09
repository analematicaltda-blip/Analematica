# Implementación 20 · Auditoría de privilegios PostgreSQL

**Avance: 27,78 % (20/72 hitos).** Refuerza ACC-007 y ACC-024 sin cerrar su aceptación completa.

## Auditor de solo lectura

`db_privileges.inspect_privileges` inspecciona las identidades de conexión y activa (`session_user` y `current_user`) y sus roles alcanzables. La evaluación de membresías es conservadora e incluye capacidades de roles asociados, aunque una configuración particular limite su uso.

Detecta atributos administrativos, propiedad de base/esquema/tablas/funciones de guardia, capacidad de crear objetos, objetos temporales y privilegios excesivos sobre las tres tablas protegidas. Comprueba el DML mínimo para cabeceras/líneas y consulta/inserción de políticas, sin conceder UPDATE/DELETE del historial. Examina ambas identidades para no acreditar una conexión administrativa que se disfraza mediante `SET ROLE`.

El resultado se limita a códigos de hallazgo y conteos; no imprime nombres de usuario, claves, SQL de conexión o datos contables. No concede, revoca ni modifica permisos. SQLite devuelve no cualificado para separación de roles PostgreSQL; no se presenta como una validación equivalente.

Comando: `accounting_db_privileges`, disponible desde `fresh_manage.py`, con `--require-ready` para devolver error si la auditoría no pasa. El comando no instala protecciones ni modifica roles.

## Integración operativa

La opción `ACCOUNTING_ENFORCE_DB_PRIVILEGES=1` incorpora los hallazgos a `/readyz`; un rol no cualificado produce 503. Está desactivada por defecto para no convertir las cuentas locales de migración en una interrupción inesperada. Debe configurarse y verificarse en el despliegue real tras preparar roles. No se activó producción ni se alteraron cuentas reales.

La auditoría solo cubre la frontera de los objetos contables protegidos; un resultado ready no prueba permisos completos para ejecutar todo Django, aislamiento RLS, revisión de funciones SECURITY DEFINER ajenas, SQL arbitrario seguro ni la corrección de todos los objetos del servidor. Otras tablas requieren inventario y una política específica. No reemplaza LedgerEngine ni la autorización empresarial del API.

## Pruebas

111 métodos Python y 17 escenarios contables PostgreSQL aprobados. La suite crea una cuenta temporal restringida en el contenedor desechable, verifica la auditoría mediante una conexión autenticada realmente con esa cuenta y comprueba que ALTER TABLE/DISABLE TRIGGER falla por permisos. No usa SET ROLE para acreditar el caso positivo. El caso negativo verifica que el administrador de sesión siga detectándose detrás de SET ROLE. La cuenta y sus grants se retiran al finalizar el ensayo.

13 regresiones de instalación ERP: incluye activación explícita del control en SQLite, HTTP503 por falta de cualificación y regreso a ready al retirar la opción de prueba. La consulta de privilegios no repara accesos.

Evidencia: `evidencias/implementacion-20.json`.

## Pendientes

Roles y grants reales para todas las tablas/secuencias del backend, ensayo de operación completa con esos roles, política de funciones privilegiadas y RLS, configuración del orquestador, revisión independiente y migraciones bajo una identidad separada. La auditoría parcial no acredita despliegue completo. Siguen pendientes llaves/medios externos y RPO/RTO, integración corporativa contable de Analemática y restantes pools. Sin migraciones, cambios de datos del usuario, commit o push.
