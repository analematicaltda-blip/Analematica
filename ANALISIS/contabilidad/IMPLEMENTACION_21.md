# Implementación 21 · Flujo contable con rol PostgreSQL restringido

**Avance: 27,78 % (20/72 hitos).** Refuerza ACC-007/024; no acredita todos los permisos del ERP ni aceptación productiva completa.

## Contrato de permisos

`runtime_profile.describe_profile` describe, sin aplicar grants, las tablas y permisos necesarios para posteo, reintentos, contrapartidas, informes y proyección local del núcleo. El comando `accounting_runtime_profile`, habilitado en `fresh_manage.py`, imprime el contrato para revisión. No incluye DDL, DELETE ni administración de roles.

Las tablas de referencia requieren SELECT y UPDATE únicamente sobre `id`, porque PostgreSQL exige UPDATE sobre alguna columna para `SELECT FOR UPDATE`. Esto permite bloquearlas sin conceder UPDATE de nombre, estado o tipo contable. El permiso de columna sigue siendo un permiso real de escritura sobre ese identificador: no equivale a una autorización de API ni a inmutabilidad SQL de todos los metadatos. Deben conservarse los controles de servicio y revisar alternativas antes de definir la política productiva.

Se separan datos anexables de datos mutables: políticas, recibos y auditoría usan SELECT/INSERT; los trabajos y balances derivados necesitan UPDATE; el outbox solo requiere UPDATE(id) para bloquear la fila en el consumidor local, sin conceder actualización de payload o estado a ese perfil. El publicador externo requeriría otra política y sigue pendiente.

El contrato no concede automáticamente permisos sobre todas las tablas Django, autenticación, catálogo empresarial o administración. No se presenta como un perfil listo para cualquier ruta web ni sustituye RLS o autorización por empresa.

## Prueba funcional

La suite PostgreSQL aplica el contrato a una cuenta temporal, inicia otro proceso autenticado realmente con ella y ejecuta LedgerEngine y el proyector. Comprueba posteo, reintento con efecto único, contrapartida, balance, proyección completa e integridad de cadena. Prueba además que el rol no pueda modificar el nombre de empresa o el tipo de cuenta ni desactivar el trigger. No usa SET ROLE para acreditar el caso positivo.

El fixture crea las tablas de monedas requeridas por el contrato antes de aplicar grants. Se eliminan la cuenta temporal y sus privilegios al finalizar. El ensayo de backup/restore posterior incluye los asientos y recibos generados por ese flujo.

Resultados finales: 112 métodos Python y 18 escenarios contables PostgreSQL aprobados; ver `evidencias/implementacion-21.json`. Sin cambios de esquema productivo, cuentas reales o bases del usuario; sin commit ni push.

## Pendientes

Política completa de permisos para rutas de ambos sistemas, endpoints autenticados bajo el rol real, operaciones de catálogo/cierre/multimoneda, política del publicador y separación operativa de migraciones. Faltan roles y credenciales productivos, revisión de capacidades de bloqueo/escritura de IDs, RLS/funciones privilegiadas, restauración de llaves/medios y RPO/RTO, integración corporativa contable Analemática y restantes pools.
