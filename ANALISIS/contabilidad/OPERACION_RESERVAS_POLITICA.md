# Reserva ligada a una política tributaria persistida

Código: `BACKEND/SGA-TUR-BAKEND/apps/domain_business/comercial/services/reservation_tax_policy.py`. Comparte el motor tributario y el ledger existentes; no crea otro libro ni interpreta automáticamente la legislación.

## Recorrido

1. El titular revisa y registra una política de su empresa mediante las dos confirmaciones ya existentes. Las tasas, categorías, vigencias y componentes son declarados y quedan versionados; no se certifica su legalidad.
2. En el router contable ERP, POST `revisar-reserva-con-politica/` exige exactamente `reservation_id`, `selection`, `economic_date`, `evidence_digest`, `confirmed:true` y `expected_revision`.
3. Cada selección exige `item_id`, `net`, `tax_category`, `policy_code` y `policy_revision`. El cliente no introduce el impuesto calculado. El servidor recupera la política, aplica el redondeo exacto por componente y comprueba el total con la reserva confirmada bloqueada transaccionalmente.
4. Se persiste una revisión fiscal y una evidencia ligada a empresa/reserva/revisión/actor/fuente/importes/políticas. La referencia reservada `SGATP/` contiene código, versión y digest. Si falla la evidencia, toda esa revisión revierte.
5. La solicitud de factura sigue requiriendo su segunda confirmación. Revalida fuente, política y evidencia; no emite una factura ni obtiene aceptación DIAN.
6. El reconocimiento del servicio y su posteo usan sus dos revisiones existentes. Antes del asiento vuelven a comprobar el vínculo tributario. El asiento canónico carga cuentas por cobrar y abona ingreso/impuesto según las cuentas revisadas. El reintento recupera el mismo asiento, sin pago ni duplicación.

Analemática ofrece la misma revisión mediante el comando corporativo `review_reservation_policy`. Mantiene origen fijo, sesión ERP y CSRF, vínculo entre ambos sistemas y validación de correspondencia del resultado. El puente HTTP no convierte las dos bases en una transacción distribuida; la atomicidad descrita pertenece al servidor ERP/ledger.

## Alcance explícito

- COP, entre1 y5 componentes, con contratos y tamaño canónico acotados.
- Un único código de impuesto de salida con importe positivo; la contabilización actual tiene una sola cuenta de pasivo tributario. Más impuestos positivos exigen el desarrollo por componente de R03 y se rechazan.
- Retención distinta de cero se rechaza: no se descuenta ni se omite para aparentar un flujo completo. Cotizarla no implica disponer de su contabilidad.
- El reconocimiento ligado a política exige fecha contable igual a la fecha tributaria declarada. Tratamientos con fechas diferentes requieren un flujo explícito revisado; no se presenta esta restricción del software como regla tributaria universal.
- Las revisiones manuales anteriores siguen disponibles y diferenciadas. Una referencia `SGATP/` sin su evidencia se rechaza. Antes de producción deben revisarse legados que hubieran utilizado ese prefijo; no se reescriben silenciosamente.
- No hay formulario nuevo ni una ruta específica nueva de recuperación del detalle del vínculo; las fuentes/revisiones existentes conservan sus identificadores. Integrar recuperación/presentación completa en R18 y resolver los casos de respuesta perdida sin inventar nuevas confirmaciones.

## Evidencia y límites

Las pruebas nuevas incluyen un asiento de100,00 COP: débito de100,00 a cuentas por cobrar, créditos de84,03 a ingreso y15,97 a impuesto. La tasa1900 bps es un dato sintético declarado, no una recomendación tributaria. También se prueba una composición gravada/exenta y rechazo de versión inexistente/vencida, total incompatible, soporte alterado/ausente, duplicados, retenciones y fecha diferente.

Faltan validación normativa/soportes legítimos, retenciones/IVA descontable/múltiples cuentas, representación fiscal y homologación DIAN, interfaz y recuperación completas, guardas SQL específicas del nuevo vínculo, concurrencia PostgreSQL y aceptación profesional/productiva. Los hashes internos no son WORM ni inmunidad frente a reescritura SQL privilegiada coherente.

`stored_policy_link_verified=true` solo prueba coherencia interna con una política persistida. `regulatory_verified`, `fiscal_accepted`, `withholding_posted`, `fiscal_document_created` y `money_transferred` permanecen falsos. `ledger_written` solo es verdadero en el posteo explícito del servicio, nunca en esta revisión/solicitud. No se alteró la frontera DIAN.
