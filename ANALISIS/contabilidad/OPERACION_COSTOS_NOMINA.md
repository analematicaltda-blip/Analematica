# Distribución analítica de nómina por operación

El backend del ERP atribuye costos de una nómina **ya contabilizada y revisada** a jornadas registradas. No crea otro asiento, no paga, no liquida novedades laborales y no completa una orden operativa. No reemplaza su costo acumulado, que puede incluir otros conceptos.

## Contrato de uso

Las acciones POST de PlanCuentaViewSet requieren sesión/JWT, vínculo empresarial vigente y `provider_id` único en la consulta. Se conserva el aislamiento existente y las respuestas privadas sin caché.

| Acción | Cuerpo |
| --- | --- |
| `fuentes-costos-operativos-nomina` | `payroll_id` |
| `revisar-costos-operativos-nomina` | `payroll_id`, `capacities`, `operation_centers`, `evidence_digest`, `reason_code`, `expected_revision`, `confirmed: true` |
| `registrar-costos-operativos-nomina` | `payroll_id`, `review_id`, `confirmed: true` |
| `estado-costos-operativos-nomina` | `payroll_id` |
| `costos-laborales-operacion` | `order_id`, `since`, `until` |

`capacities` contiene exactamente todos los empleados de la nómina: objetos con `employee_id` y `capacity_seconds`, entero positivo declarado expresamente y limitado a la duración del período. No existe capacidad legal predeterminada. `operation_centers` relaciona cada UUID de operación registrada con un código empresarial explícito, hasta40 caracteres `[A-Z0-9_.-]`. Una declaración no equivale a un catálogo profesionalmente validado.

La primera confirmación guarda una revisión con vencimiento de15 minutos. La segunda debe proceder del mismo propietario, usar la revisión vigente y conservar intactas las fuentes. Repetirla recupera el mismo registro; no restaura autorizaciones. Una revisión posterior conserva la anterior y sustituye únicamente su distribución analítica vigente.

La captura `jornada-operativa` de worker_data_views añade `operation_reference` al contrato existente de jornadas; se registra como declaración MANUAL. No permite declarar procedencia DISPATCH. Esta última requiere las pruebas persistentes de inicio/finalización y el identificador determinista que genera el servicio de despacho.

## Cálculo y cautelas

- Se toma salario, contribución patronal y provisiones de la instantánea contabilizada, sin usar salario neto como costo empresarial.
- Las jornadas se recortan al período civil de nómina en America/Bogota; se ponderan en microsegundos enteros. Los centavos se reparten mediante mayores restos, con desempate estable.
- Horas sin operación y capacidad sin respaldo permanecen sin asignar. No se distribuye automáticamente todo el gasto entre las pocas jornadas conocidas.
- Jornadas abiertas, superpuestas, futuras, capacidad insuficiente, operación ajena, fuente alterada o nómina revertida bloquean la distribución efectiva.
- El informe usa fecha de contabilización de nómina. Si hay fuentes desactualizadas o nóminas contabilizadas sin distribuir, `total_cost` es nulo y la cobertura incompleta queda explícita. `known_current_cost` es solo el subtotal vigente conocido.
- Guardas SQL ausentes bloquean; no se crean tablas, migraciones, aprobaciones ni datos operativos durante el uso.

## Pendientes de aceptación

Faltan comandos del puente corporativo de Analemática, formularios de ambos paneles, reglas revisadas de recargos/deducciones/viáticos, nómina electrónica, cualificación PostgreSQL y concurrencia productiva, volúmenes mayores y evidencia laboral legítima. Límites actuales:10 empleados,100 jornadas superpuestas y20 operaciones por cálculo;1000 revisiones por informe. El flujo no acredita ejecución física ni aptitud profesional.

## Actualización74: puente e interfaces

Los cinco comandos también están disponibles en el puente corporativo autenticado de Analemática bajo `/accounting/commands/`, con los nombres internos `payroll_cost_sources`, `review_payroll_costs`, `record_payroll_costs`, `payroll_cost_state` y `operation_labor_costs`. El `provider_id` se obtiene exclusivamente del vínculo revisado. Los comandos de lectura no precisan aprobación financiera; revisión y registro requieren cada uno su confirmación explícita.

El formulario **Costos de nómina por operación** aparece en los paneles existentes de ERP y Analemática. Cargar nóminas → seleccionar → consultar jornadas → declarar capacidad pagada en segundos y centros → recuperar revisión vigente → completar huella y motivo → primera confirmación/revisión → segunda confirmación/registro. La huella debe corresponder al soporte legítimo conservado por el responsable; no prueba su autenticidad por sí sola. Si cambian fuentes, capacidad o centros, repetir la revisión. El informe financiero por operación está disponible por API; su formulario de consulta dedicado sigue pendiente.

Los pendientes de conexión corporativa/formulario de distribución de la entrega73 quedan subsanados localmente en74. Permanecen las demás limitaciones y pruebas productivas allí consignadas.
