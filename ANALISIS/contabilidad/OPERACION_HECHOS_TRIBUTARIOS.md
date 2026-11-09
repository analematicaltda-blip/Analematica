# Compras, ventas, IVA y retenciones revisados

## Cambio funcional

El servicio canónico `commercial_tax_posting.py` añade un flujo explícito al motor existente. Recibe un hecho económico declarado con referencia documental, calcula sus componentes desde políticas persistidas y escribe el ledger únicamente después de revisión y segunda confirmación del mismo titular. No crea un segundo libro ni modifica asientos existentes.

| Operación | Débitos | Créditos |
| --- | --- | --- |
| Compra | Base a gasto/activo; IVA descontable declarado a activo | Retención practicada a pasivo; saldo a cuenta por pagar |
| Venta | Saldo a cuenta por cobrar; retención sufrida a activo | Base a ingreso; IVA generado declarado a pasivo |
| Contrapartida | Inverso exacto del asiento original | Inverso exacto del asiento original |

Todas las cuentas se seleccionan explícitamente en el plan de esa empresa. El sistema no inventa tasas, responsabilidades fiscales, deducibilidad, terceros o medios de pago. No contabiliza contra efectivo ni liquida dinero. La selección de una cuenta con tipo ASSET/LIABILITY no acredita por sí sola la clasificación fiscal profesional de esa cuenta.

## Contrato de captura

El objeto `fact` contiene exactamente:

- `document_id`: UUID canónico de la referencia documental.
- `document_digest`: SHA-256 hexadecimal declarado del soporte.
- `counterparty_id`: UUID declarado del tercero; no constituye verificación de su identidad tributaria.
- `direction`: `PURCHASE` o `SALE`.
- `entry_date`: fecha económica ISO, no futura.
- `settlement_account_id`: cuenta por pagar (pasivo) o por cobrar (activo).
- `items`: de 1 a 20 componentes, sujeto al límite de tamaño del contrato canónico existente.

Cada componente requiere `item_id`, `net` (cadena monetaria exacta con dos decimales), `tax_category` (`TAXABLE`, `EXEMPT`, `EXCLUDED`), `policy_code`, `policy_revision`, `basis_account_id` y `tax_accounts` (código de impuesto/retención → UUID de cuenta). El mapeo debe contener exactamente los componentes aplicados cuyo importe redondeado sea positivo. No se agregan cuentas de impuesto ficticias para componentes nulos.

La política tributaria existente incorpora el tipo explícito `INPUT_TAX`, además de `OUTPUT_TAX` y `WITHHOLDING`. Una compra rechaza impuesto generado positivo y una venta rechaza IVA descontable positivo. La cotización de venta anterior rechaza políticas de IVA descontable: no lo reinterpreta como retención. Se conserva el contrato de las cotizaciones anteriores.

El cálculo usa centavos enteros y redondeo HALF_UP por componente según la política declarada. La segunda confirmación vuelve a comprobar vigencia, cuentas, período y cotización. La revisión expira a los 15 minutos como límite técnico de aprobación; no es una regla legal.

## Rutas ERP

Base: `/api/v1/mi-negocio/contable/contabilidad/cuentas/`. POST autenticado con sesión ERP/CSRF o JWT; un único proveedor autorizado y vínculo empresarial vigente. Se conserva la frontera de titular existente.

| Ruta | Cuerpo exacto |
| --- | --- |
| `revisar-hecho-tributario/` | `fact`, `evidence_digest`, `expected_revision`, `confirmed: true` |
| `contabilizar-hecho-tributario/` | `document_id`, `review_id`, `confirmed: true` |
| `estado-hecho-tributario/` | `document_id` |
| `revisar-contrapartida-tributaria/` | `document_id`, `reason_code`, `evidence_digest`, `confirmed: true` |
| `contrapartida-tributaria/` | `document_id`, `review_id`, `confirmed: true` |

Analemática utiliza el puente corporativo existente, con vínculo revisado y sesión ERP del titular: comandos `review_commercial_tax`, `post_commercial_tax`, `commercial_tax_state`, `review_commercial_tax_reversal` y `reverse_commercial_tax`. No se acepta sobrescribir empresa, proveedor u origen desde el cliente.

## Recuperación, integridad y ajustes

Una revisión no contabiliza. El posteo enlaza referencia, políticas, componentes, actor, período, asiento, recibo canónico y prueba de origen. El reintento recupera el mismo asiento, incluso después de su contrapartida; no lo vuelve a causar. Una prueba ausente o alterada no se reconstruye automáticamente. Cambiar cuentas, retirar el vínculo, modificar evidencia o cerrar el período impide nuevos posteos.

Dentro de este flujo, tanto la referencia documental como el digest reclamado evitan repetir el documento. La reclamación sigue ocupada después de la contrapartida. Esto no demuestra deduplicación semántica con otras rutas heredadas ni permite identificar documentos diferentes que representen el mismo hecho real.

Las contrapartidas tienen su propia revisión y segunda confirmación, verifican el original y se contabilizan en el período vigente conforme al motor existente. No reescriben el original ni emiten una nota crédito fiscal. Una contrapartida externa sin el vínculo revisado no se adopta como si hubiese sido autorizada por esta ruta. El fallo al guardar las pruebas revierte también el asiento y el recibo dentro de la transacción.

## Pendientes de aceptación

Este es un **hecho declarado y revisado**, no una importación automática de compras, factura verificada o documento fiscal aceptado. Faltan integración con las fuentes nativas y documentos/cuentas de terceros, deduplicación entre flujos, pagos y devoluciones parciales, clasificación de todas las responsabilidades tributarias, conciliación fiscal unificada (el conciliador anterior solo atribuye reservas), interfaz de captura, revisión profesional, pruebas de concurrencia PostgreSQL y controles SQL específicos de estas pruebas de origen. No se acreditan DIAN, validez del soporte o autenticidad de un tercero por un UUID/hash declarado.

No se relajaron las restricciones anteriores de reservas con retenciones o múltiples impuestos: estas requieren adaptar su propio reconocimiento y prevenir doble causación. La nueva ruta permite el posteo explícito de hechos revisados, sin activarlo automáticamente sobre una reserva ya causada.
