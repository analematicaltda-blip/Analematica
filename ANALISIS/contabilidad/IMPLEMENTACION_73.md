# Implementación73 · Costos de nómina trazables por operación

Se implementó en el backend del ERP la distribución analítica de una nómina ya contabilizada entre las operaciones con jornadas registradas. Capacidad pagada y centros son declaraciones explícitas; los costos sin respaldo permanecen visibles sin asignar. Las dos confirmaciones del propietario conservan la fuente y no generan gastos ni pagos adicionales.

## Hallazgos subsanados

1. Nómina y jornadas estaban desconectadas: la distribución enlaza instantánea contable, empleado, período, jornada, operación y centro.
2. Un reparto basado solo en jornadas conocidas podía absorber indebidamente todo el gasto: ahora conserva capacidad sin evidencia y trabajo sin operación como costo no asignado.
3. Recargas y revisiones podían duplicar el costo analítico: identificadores deterministas, recuperación idempotente y selección de última revisión, sin modificar el libro original.
4. Cambios de fuente podían dejar cifras aparentando vigencia: se recalcula su correspondencia, se señala la desactualización y se devuelve total nulo cuando falta cobertura.
5. Jornadas superpuestas, abiertas o DISPATCH sin procedencia podían aparentar respaldo: se rechazan y se exige la cadena persistida de despacho cuando corresponda.
6. Falta de guardas SQL podía debilitar las evidencias: bloqueo explícito sin reparación automática.

## Evidencia y alcance

**747 pruebas Python aprobadas en43 suites, sin omisiones**, incluidas23 pruebas nuevas ORM/API y58 de regresión corporativa. Manifiesto estable y hashes de todos los registros comprobados; navegador no repetido en esta entrega. Las23 nuevas pruebas cubren: reparto exacto, fuente modificada, revisiones, caducidad, falta de guardas, rechazo de superposición, períodos Bogotá, procedencia, reversión, fallos de persistencia, autorización y respuestas privadas. [Contrato operativo](OPERACION_COSTOS_NOMINA.md) y [evidencia73](evidencias/implementacion-73.json).

El flujo nuevo está implementado y probado en el backend del ERP. **No se ha conectado todavía al puente corporativo ni a los paneles de Analemática/ERP.** No se acredita ejecución física, cumplimiento laboral integral, nómina electrónica ni cualificación PostgreSQL.

R10 continúa en ejecución: faltan recargos, deducciones, viáticos, reglas profesionales y el documento electrónico. Los demás criterios pendientes conservan su estado en la matriz de20 hitos.

**Avance global:63,89% (46/72); aceptación completa0/24.** Se amplía un hito ya acreditado y no se duplica su porcentaje. No están cerrados los20 hitos. Sin commits, push, despliegues, pagos ni envíos oficiales.
