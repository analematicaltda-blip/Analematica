# Compras nativas revisadas · fuente persistente y ledger

## Hallazgos corregidos

El módulo conserva proveedores/facturas en sus modelos originales. Sus rutas heredadas estaban deshabilitadas y una señal de alta referenciaba `instance.provider`, inexistente en `FacturaCompra`, e intentaba seleccionar cuentas/crear un asiento legado sin revisión. La señal ahora no contabiliza implícitamente. Se implementó una ruta explícita en el motor canónico; los pagos y las rutas antiguas no se habilitaron.

También se corrigió un bloqueo de interfaz: el catálogo de reconocimiento de ventas excluía gastos. El catálogo de compras es ahora independiente (activo, gasto y pasivo), con la misma paginación/acotación por empresa. El catálogo de ventas conserva sus tipos anteriores.

## Recorrido disponible en ERP y Analemática

1. Cargar las cuentas propias; consultar proveedores/facturas si ya existen.
2. Capturar proveedor, identificación declarada y soporte. Esta captura no verifica su identidad oficial.
3. Capturar número, fecha, vencimiento opcional, subtotal, impuestos y total de la factura. El servidor exige importes exactos y subtotal+impuestos=total.
4. Seleccionar cuentas y política tributaria persistida. Confirmar recepción de bienes/servicios y revisar. El desglose debe coincidir con la factura guardada.
5. Dar una segunda confirmación para contabilizar. No se realiza pago ni se marca la factura PAGADA.
6. Recuperar el resultado después de recargar la página; las autorizaciones locales quedan desmarcadas. La contrapartida exige revisión y segunda confirmación propias.

Los formularios comparten implementación y conservan azul metalizado/azul claro/texto blanco. La interfaz cubre **un concepto**; el adaptador backend admite el contrato acotado de componentes del motor. No se presenta esta interfaz como cobertura de todas las compras turísticas.

Los soportes se leen localmente, con límite10MiB, para calcular SHA-256; no se suben ni se almacenan en texto claro en el servidor. Solo se envían metadatos y huellas. Calcular una huella no autentica el documento ni acredita DIAN. Las políticas de compras ofrecen `INPUT_TAX` explícito, sin reinterpretarlo como impuesto generado o retención ni imponer tasas legales predeterminadas.

## API ERP

Base `/api/v1/mi-negocio/contable/contabilidad/cuentas/`; proveedor único en `provider_id`, sesión/CSRF o JWT del titular y vínculo contable vigente. No hay bypass por superusuario, agente o selección de empresa enviada en el cuerpo.

| Ruta | Método / campos específicos |
| --- | --- |
| `cuentas-compras-nativas/` | GET; `paged=1`, `despues_id`, `buscar` opcionales |
| `proveedores-compras-nativas/` | POST; `after_id` (null o entero) |
| `registrar-proveedor-nativo/` | POST; `request_id`, `name`, `identification`, `evidence_digest`, `confirmed` |
| `registrar-factura-compra-nativa/` | POST; `request_id`, `supplier_id`, `number`, `issue_date`, `due_date`, `subtotal`, `tax`, `gross`, `document_digest`, `evidence_digest`, `confirmed` |
| `fuentes-compras-nativas/` | POST; `after_id` |
| `revisar-compra-nativa/` | POST; `invoice_id`, `selection`, `settlement_account_id`, `economic_fact`, `evidence_digest`, `expected_revision`, `confirmed` |
| `contabilizar-compra-nativa/` | POST; `invoice_id`, `review_id`, `confirmed` |
| `estado-compra-nativa/` | POST; `invoice_id` |
| `revisar-contrapartida-compra-nativa/` | POST; `invoice_id`, `reason_code`, `evidence_digest`, `confirmed` |
| `contrapartida-compra-nativa/` | POST; `invoice_id`, `review_id`, `confirmed` |

`economic_fact` debe ser `GOODS_OR_SERVICES_RECEIVED`, una declaración expresa del titular, no una comprobación física independiente. `selection` usa el contrato de componentes de [hechos tributarios](OPERACION_HECHOS_TRIBUTARIOS.md). Las cantidades monetarias son cadenas exactas de dos decimales, nunca floats. Los IDs de proveedor/factura son los enteros de los modelos existentes, acotados al rango entero seguro de JavaScript; los UUID documentales se derivan en el servidor. Los modelos/IDs históricos no se reescriben.

Analemática usa los comandos equivalentes `record_native_supplier`, `record_native_purchase`, `native_supplier_sources`, `native_purchase_sources`, `review_native_purchase`, `post_native_purchase`, `native_purchase_state`, `review_native_purchase_reversal` y `reverse_native_purchase`. El catálogo se consulta mediante `sources/purchase_accounts`. Mantienen la doble identidad corporativa/ERP y el origen fijo existentes.

## Integridad y recuperación

- Capturas idempotentes por UUID de solicitud y contenido; un cambio de datos no sobrescribe la solicitud original. La factura queda vinculada a proveedor, importes, fechas, autor y huella.
- El servidor reserva tanto la identidad documental como su hash. La ruta genérica no puede revisar/postear/ajustar una fuente reservada saltándose el adaptador nativo, ni reutilizar ese hash con otro UUID.
- El permiso interno es temporal, ligado a empresa, documento, actor, instantánea y operación; no procede de un parámetro del cliente y se retira al salir, incluso ante error.
- Cambiar proveedor, factura o estado entre confirmaciones bloquea el posteo. Un período cerrado, una política/cuenta incompatible o un vínculo retirado también lo impiden.
- Asiento, recibo y prueba de origen nativa se escriben en una transacción. Si falla la prueba, se revierte todo el posteo; no se adopta un asiento sin origen reconstruyendo la evidencia.
- Un reintento devuelve el mismo asiento. Después de contabilizar, una fuente modificada puede consultarse con advertencia, pero no genera una nueva causación. La contrapartida conserva el original y tiene sus propias confirmaciones.

`native_source_verified=true` significa vínculo y consistencia con la fila nativa persistida. **No significa** identidad tributaria del proveedor verificada, documento auténtico, deducibilidad aceptada o servicio físicamente recibido.

## Límites pendientes

Facturas históricas sin captura vinculada requieren conciliación revisada: no se supone que estén sin contabilizar. La deduplicación incluye número/proveedor y huella dentro del alcance; no identifica todos los documentos distintos que representan el mismo hecho real. Faltan corrección/ampliación controlada de metadatos capturados, devoluciones parciales, todos los tipos de responsabilidad fiscal, integración comercial completa y formularios multicomponente.

Se usan modelos/tablas existentes, sin nueva migración ni reescritura de datos. Faltan migración/conciliación de bases históricas, pruebas PostgreSQL/concurrencia, guardas SQL específicas de estas evidencias, revisión profesional y aceptación productiva. No hay pagos, DIAN, emisión fiscal ni actualización de cuentas reales. `POR_PAGAR` es el estado legado del documento: el asiento confirmado y su recuperación se consultan separadamente; no equivale a pago o aceptación fiscal.
