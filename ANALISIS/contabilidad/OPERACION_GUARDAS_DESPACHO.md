# Guardas de estados operativos genéricos · H12

Alcance: `OrdenOperativa`, `ProcesoOperativo` y sus vistas genéricas en `BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa`. No equivale a una autorización de trabajo, aptitud médica profesional o control de todos los módulos especializados.

## Defectos subsanados

El CRUD permitía escribir estados sin un control de despacho; las acciones de estado enviaban misiones y devolvían éxito de envío sin demostrar transición persistida. El ejecutor interno buscaba una orden globalmente, asignaba el estado recibido y podía inventar el UUID del responsable. El registro de ejecución de tarea devolvía True sin persistir ejecución.

Ahora el CRUD selecciona un titular personal activo y su proveedor/empresa con vínculo vigente. La empresa se deriva del contexto, no del cuerpo. Las relaciones tarea/proceso e incidente/orden se comprueban dentro de la misma empresa. Las relaciones legadas inconsistentes se excluyen de consultas y de las colecciones anidadas. Borradores nuevos y ediciones permitidas se auditan atómicamente; borrar por API se rechaza para conservar historia.

## Operación disponible

Bajo las rutas existentes `operativa/ordenes` y `operativa/procesos`:

- Las altas solo crean PENDIENTE/PLANIFICADO con empresa explícita, sin tiempos reales ni costos reales introducidos por el formulario. Las fechas de una orden deben formar una ventana positiva.
- La acción `cambiar-estado` de orden o `avanzar_estado` de proceso exige exactamente `nuevo_estado`, `estado_esperado`, `motivo` y `confirmado:true`. El titular se obtiene de la sesión autenticada, nunca del cuerpo.
- Orden: PENDIENTE→PREPARACION; las rutas de incidencia/cancelación admitidas conservan el estado anterior en auditoría. No se reabre un estado terminal.
- Proceso: planificación/ejecución→SUSPENDIDO o FALLIDO según el grafo explícito. La suspensión SST existente usa el mismo servicio y conserva sus pruebas de rollback, aislamiento y descripción intacta.
- GET `pre-despacho` devuelve estado, tres bloqueos de cualificación y ninguna información clínica. GET `historial-transiciones` devuelve las últimas50 transiciones auditadas propias, con `has_more` explícito, actor real y sin motivo libre ni contenido clínico. Falta paginación histórica completa de esta ruta nueva.

`state_changed=true` con `read_only=false` informa una escritura operativa; `ledger_written=false` aclara que no se contabiliza. `service_started=false` y `service_started_by_this_call=false` significan que la llamada no inicia un servicio. `physical_service_state_verified=false` impide interpretarlos como prueba del estado físico de una operación histórica.

## Activación bloqueada

No existe todavía un contrato cualificado de aptitud/EPP/jornada. Por ello EJECUCION, EN_EJECUCION, VALIDACION y finalizaciones que impliquen ejecución se rechazan explícitamente. No se interpreta un concepto clínico libre como “apto”, ni se inventan EPP, límites de fatiga o autorizaciones positivas. La cancelación/suspensión conserva su utilidad sin convertirla en una contención física demostrada.

El modelo y su manager también rechazan estados iniciales activos, cambios de estado fuera del servicio, reasignación de empresa, tiempos reales inventados, UPDATE/bulk_update de campos protegidos y bulk_create con conflictos, incluidos argumentos posicionales. Un UUID ya utilizado no se reutiliza para sobreescribir una operación. Si falla AuditLog, la transición revierte y el permiso interno se limpia.

Estas guardas cubren las rutas HTTP genéricas, el manager normal y los auxiliares modificados. No son triggers de base de datos ni protección frente a SQL directo, managers alternativos, código privilegiado o RCE. El contexto privado de Python es una frontera interna de implementación, no un token de autorización remoto.

## Compatibilidad y consumidores internos

`SargentoOperativo.actualizar_estado` requiere proveedor, actor real, estado esperado y confirmación explícitos. Las misiones legadas que no aportan ese contexto quedan rechazadas; no deben arreglarse introduciendo un ID de titular sin verificar su autorización en el broker. La ruta HTTP ya no delega ese cambio a una misión sin resultado verificable.

`crear_orden_servicio` exige actor, referencia contractual y ventana explícita; no genera un contrato aleatorio. La referencia todavía es declarada y se devuelve `contract_independently_verified=false`. La ejecución ficticia de tarea se bloquea hasta contar con un flujo persistente y cualificado. Los RegistroOperativo históricos no se reescriben; las transiciones nuevas registran el usuario verdadero en AuditLog. Su integridad histórica necesita revisión, no una atribución retroactiva inventada.

## Pendientes de cierre H12

Implementar el recorrido positivo con aptitud profesional vigente, EPP y jornada/descanso verificables, asignaciones y recursos concretos, reglas y vigencias revisadas, aprobaciones y revocación. Extender controles a transporte/agencias/alquileres y otros módulos especializados, sus tareas/recursos y ejecutores; no se afirma haberlos cubierto todos. Añadir guardas SQL/roles, carreras PostgreSQL específicas y recuperación/contención física donde aplique.

Faltan además adaptación de consumidores, prueba de integración HTTP desplegada con sesiones reales y aceptación profesional. Las pruebas actuales usan APIRequestFactory y ORM aislados, no un recorrido UI/servidor productivo. No hay formularios nuevos ni cambios de paleta; H12 sigue EN_EJECUCION.
