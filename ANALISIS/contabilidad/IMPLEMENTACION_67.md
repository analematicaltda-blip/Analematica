# Implementación67 · Cierre de vías de elusión del despacho genérico

**Avance global:61,11 % (44/72), sin créditos duplicados.** Amplía ACC-012, que ya tenía incremento y verificación acreditados. El plan conserva4 paquetes verificados localmente y16 en ejecución; no se declara cierre total ni producción habilitada.

## Correcciones concretas

- Se retiró la modificación libre de estados por CRUD en las órdenes/procesos genéricos. El titular, proveedor y empresa se validan desde contexto vigente y se rechazan relaciones de otra empresa, incluidas inconsistencias legadas en consultas anidadas.
- Las transiciones permitidas pasan por un servicio transaccional con estado esperado, confirmación y auditoría del usuario real. Se eliminó la atribución a un UUID de responsable inventado. Un fallo de auditoría revierte la escritura.
- El modelo/manager bloquea creación en ejecución, cambios de estado fuera del servicio, reasignación de empresa, tiempos reales inventados, actualizaciones masivas y altas con conflictos que pudieran reescribir estados.
- Se preservaron borradores, preparación y suspensión/cancelación por riesgo. Se añadió diagnóstico de pre-despacho sin clínica e historial privado acotado de transiciones.
- La creación interna ya no inventa contratos ni fechas; la ejecución de tarea ya no devuelve éxito sin persistencia. Los consumidores internos sin contexto autorizado quedan bloqueados hasta adaptarse.

## Límite operativo importante

La activación genérica está bloqueada mientras no exista el recorrido positivo cualificado de aptitud, EPP y jornada. Esta corrección impide eludir su ausencia; no afirma haber implementado o certificado esas comprobaciones positivas. No se cierra H12 con una guarda que simplemente bloquea.

Faltan los módulos especializados, recursos/tareas, reglas profesionales, flujo positivo, integración de consumidores y pruebas PostgreSQL/SQL específicas. Las guardas Python no sustituyen controles de base de datos ni protegen frente a código/SQL privilegiado. No se habilitó un nuevo permiso al motor de control, pagos o agentes.

[Operación, cambios de contrato y límites](OPERACION_GUARDAS_DESPACHO.md). [Evidencia67](evidencias/implementacion-67.json). El [cierre por paquete](CIERRE_20_HITOS.md) conserva la separación entre código pendiente y aceptación externa.

No se hicieron commits, push, cambios de main, migraciones sobre datos reales ni despliegues. No se cambió la identidad visual ni se ejecutaron acciones externas.

## Regresión final ejecutada

- **560 pruebas Python aprobadas, sin omisiones, en36 suites**, incluidas22 nuevas de límites operativos,14 SST existentes y38 del puente corporativo.
- Se verificaron estados por APIRequestFactory/ORM, creación de borradores, planificación y suspensión, rollback de auditoría, limpieza del permiso interno, UUID de alta no reutilizable, relaciones empresariales, rechazo de agentes/vínculo revocado y falsa ejecución de tareas retirada.
- Manifiesto estable y hashes de evidencia comprobados contra el árbol actual. `pip check`, siete pruebas del porcentaje, plan20, pendientes de billetera y `git diff --check` aprobados.
- Una ejecución inicial se canceló expresamente para corregir el indicador `read_only` de un resultado que sí cambia estado operativo; no se cuenta como aprobada. La ejecución final completa usa fuentes estables.
- No se reejecutaron Chromium44 ni PostgreSQL52 de cortes anteriores. No se acredita despliegue HTTP/UI, controles SQL, carrera PostgreSQL de despacho ni cualificación física/profesional.
