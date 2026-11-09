# Datos de autorización profesional, EPP y descanso por trabajador

## Alcance implementado

El ERP turístico dispone de seis registros persistentes nuevos, asociados a empresa, trabajador, autor, fecha, revisión y hash del soporte. No se rellenan datos reales automáticamente ni se deduce aptitud de un texto libre. Los modelos anteriores se conservan.

| Registro | Datos específicos | Responsable de captura |
| --- | --- | --- |
| Autorización profesional | Decisión estructurada cifrada, fecha de evaluación, inicio/fin de vigencia, referencia UUID del documento | Revisor habilitado explícitamente por el servidor y con permiso clínico de alta |
| Entrega de EPP | Código y referencia del equipo, cantidad, entrega y vencimiento | Titular autorizado de la empresa |
| Jornada | Inicio, fin si se conoce, procedencia y referencia operativa cuando corresponde | Titular; el cierre de despacho también registra la jornada |
| Cierre de jornada abierta | Jornada original y fecha de finalización | Titular, sin sobrescribir la jornada original |
| Descanso | Inicio y fin observados | Titular, con soporte explícito |
| Revocación | Tipo y referencia del registro retirado | Titular; no permite borrar horas trabajadas |

La decisión profesional se cifra mediante el mecanismo Fernet configurado en el ERP. La lectura falla si no autentica el cifrado; nunca acepta texto plano como alternativa. Esto no constituye cifrado de conocimiento cero, custodia en hardware ni verificación independiente de licencia profesional. No se cargan diagnósticos ni archivos médicos en estas rutas.

## API autenticada

Base: `/api/v1/mi-negocio/operativa/sst/datos-trabajador/`. Todas las acciones usan POST y un único parámetro de consulta `provider_id=<UUID>`. Requieren JWT o sesión ERP autenticada y comprueban empresa/actor antes de acceder a registros.

Las altas comparten los campos exactos `employee_id`, `request_id` (UUID de idempotencia), `expected_revision`, `evidence_digest` (SHA-256 hexadecimal) y `confirmed: true`. Se añaden exclusivamente los campos correspondientes:

| Ruta | Campos adicionales |
| --- | --- |
| `autorizacion-profesional/` | `decision` (`FIT`, `FIT_RESTRICTED`, `UNFIT`), `evaluated_at`, `valid_from`, `valid_until`, `document_reference` |
| `entrega-epp/` | `equipment_code`, `equipment_reference`, `quantity`, `delivered_at`, `valid_until` |
| `jornada/` | `started_at`, `ended_at` (admite null para jornada abierta) |
| `cerrar-jornada/` | `work_period_id`, `ended_at` |
| `descanso/` | `started_at`, `ended_at` |
| `revocar/` | `record_type` (`FITNESS`, `PPE`, `REST`), `record_id` |

Las fechas llevan zona horaria. No se acepta un descanso o una entrega futura como hecho ya ocurrido. Repetir el mismo `request_id` con el mismo contenido recupera el registro; modificarlo o usar una revisión desactualizada se rechaza. El hash identifica un soporte declarado, pero no demuestra su autenticidad física.

Consultas separadas, sin los campos comunes de alta:

- `trabajadores/`: cuerpo exacto `{"after_id": null}` o cursor UUID. Titular o revisor provisionado; hasta 50 trabajadores de esa empresa con nombre, ID y estado. No incluye datos médicos.
- `resumen-operativo/`: `employee_id`, `kind` (`FITNESS`, `PPE`, `WORK`, `WORK_END`, `REST`, `REVOKE`) y `before_revision` (null o entero). Titular; hasta 20 registros con cursor. Devuelve referencias, fechas y metadatos, sin decisión ni documentos médicos.
- `detalle-profesional/`: `record_id`. Exige tanto habilitación clínica provisionada como permiso clínico explícito de consulta. Devuelve la decisión mínima y sus fechas; no documentos.
- `dossier-despacho/`: `order_id`, `crew`, `expected_revision`, `confirmed`. Solo revisor habilitado. Cada elemento de `crew` contiene exactamente `employee_id`, `fitness_authorization_id`, `ppe_assignment_ids` y `rest_period_id`. Son referencias a registros existentes, no declaraciones booleanas de aptitud o descanso.

Los auxiliares o un superusuario sin los permisos clínicos explícitos no pueden registrar/consultar decisiones por ese solo rol. El administrador operativo ve metadatos y resultados de validación; no obtiene la decisión clínica mediante el resumen.

## Política y despacho

Por defecto no hay una política habilitada. El servidor puede provisionar `OPERATIONAL_DISPATCH_POLICY_FILE`, un archivo JSON privado absoluto sin enlaces simbólicos, limitado a 64 KiB. El objeto raíz relaciona UUID canónico de proveedor con su política. No se añaden permisos ni políticas desde el navegador.

Cada política exige `enabled`, `version`, `reviewer_ids`, `required_ppe`, `max_shift_minutes`, `min_rest_minutes`, `review_ttl_seconds`, `valid_from`, `valid_until`, `evidence_digest`. Las horas de trabajo y descanso deben ser definidas y revisadas para la actividad; no se suministran supuestos legales predeterminados. Los revisores necesitan adicionalmente el permiso Django explícito de alta de salud ocupacional. El archivo no acredita su título o habilitación profesional.

La ruta positiva implementada cubre **OrdenOperativa genérica**. En sus rutas existentes, el titular ejecuta `revisar-despacho` y después `registrar-inicio`, cada una con confirmación explícita; la segunda referencia la revisión anterior. Ambas revisan datos, política, trabajador, fuente y vigencias. Se bloquea si:

- Falta un registro, está revocado o pertenece a otra empresa/trabajador.
- La última autorización no es `FIT` vigente durante toda la operación. `FIT_RESTRICTED` requiere evaluación adicional y no se acepta como aptitud irrestricta.
- Falta EPP exigido o vence antes del fin previsto.
- Falta descanso suficiente, hay trabajo abierto o trabajo registrado durante ese descanso.
- Cambia la orden/política, vence la revisión, se retira el permiso del profesional o el trabajador continúa ocupado en otro despacho.

`estado-despacho` recupera el resultado sin volver a ejecutar. `revocar-requisitos` añade una revocación auditable; no detiene físicamente un vehículo o servicio ya iniciado. El fin exige `revisar-fin` y `registrar-fin`, registra la jornada efectivamente declarada y libera la reserva lógica del trabajador. La orden queda en **VALIDACION**, o INCIDENCIA ante cambios de fuente: no se finge cierre contable, nómina, pago ni servicio COMPLETADO.

## Instalación y pendientes

Se incluyen migraciones iniciales del nuevo app `sg_sst` tanto para el perfil fresco como para el árbol canónico. Se verificó una **base SQLite nueva**, las seis tablas vacías, sus guardas SQL y ausencia de diferencias de modelo/migración. No se migró una base existente. Actualizaciones y borrados históricos se bloquean en ORM y por triggers; las correcciones se añaden como nuevos registros. El administrador privilegiado del motor de base de datos sigue fuera de una garantía WORM.

Pendientes de aceptación: datos legítimos de cada trabajador, habilitación profesional comprobada, política laboral/SG-SST revisada, evidencia física de entrega/descanso, migración de bases históricas, cualificación PostgreSQL del flujo nuevo, formularios en ambos paneles y cobertura de procesos especializados. El historial registrado no demuestra que no exista trabajo fuera de la plataforma. No hay sincronización automática de inventario EPP, nómina o costos por este incremento.
