# Conciliación integral por cuenta tributaria

El reporte nuevo reúne movimientos contabilizados de reservas, compras, ventas y contrapartidas. El endpoint anterior sigue disponible con su alcance original. No se mezclan datos de empresas ni se convierte una diferencia sin origen en impuesto validado.

## Consulta

ERP: GET `/api/v1/mi-negocio/contable/contabilidad/cuentas/conciliacion-tributaria-integral/`, con exactamente un valor por parámetro: `provider_id`, `cuenta_id`, `desde`, `hasta`. Requiere sesión o JWT del titular y vínculo empresarial vigente.

Analemática: GET `/api/v1/workspace/corporate/accounting/report?report=tax_register&account_id=...&since=...&until=...`. Mantiene vínculo corporativo revisado, sesión ERP y comprobación de identidad antes/después de consultar. Un validador puro rechaza campos inesperados, fuentes incompatibles, duplicados de asiento, importes binarios y diferencias aritméticas antes de reenviar el reporte.

## Interpretación

- Se selecciona una cuenta de **activo o pasivo** del plan vigente. No se deduce que todos sus movimientos sean fiscales por el código o nombre de la cuenta.
- El reporte muestra débitos, créditos y movimiento según naturaleza: débito menos crédito para activo, crédito menos débito para pasivo. Es movimiento del intervalo, no saldo acumulado de apertura/cierre.
- `tax_by_kind` distingue IVA descontable declarado (`INPUT_TAX`), generado (`OUTPUT_TAX`) y retención (`WITHHOLDING`). Una contrapartida reduce la atribución correspondiente en su propia fecha económica.
- Las fuentes deben coincidir con revisión, asiento, recibo y documento reclamado. Una prueba comercial ausente o alterada impide una conciliación calificada; no se reconstruye como si existiera.
- Las partidas manuales, bases o saldos de cartera/proveedores que no sean impuestos permanecen sin atribución fiscal. El importe no atribuido se conserva explícitamente, aunque su neto sea cero.
- Se agrupan las líneas por asiento/cuenta para evitar atribuir dos veces varios componentes del mismo impuesto. Se conservan las sumas exactas y referencias, sin inventar vínculo de una línea individual cuando no existe.

Límites: COP; intervalo de hasta366 días; hasta2000 movimientos,250 asientos y20000 líneas completas de sus asientos/orígenes. Un exceso rechaza la consulta y requiere reducir el intervalo. Se utiliza el libro principal con bloqueo por empresa y las comprobaciones de apertura/valoración existentes.

## Paneles

El panel ERP de conciliación admite activos/pasivos y muestra los tres tipos de tributo, atribuidos, pendientes y origen. En Analemática se añade la opción **IVA y retenciones: conciliación integral**, conservando el reporte anterior. Cambiar cuenta, fechas, contexto o sesión retira resultados anteriores. Se conserva azul metalizado/azul claro y texto blanco; vistas móviles y navegación existentes se verifican en Chromium.

No es una declaración, liquidación neta de IVA, deducibilidad certificada, cruce DIAN ni autorización de una operación. Los UUID/hash y las reglas declaradas siguen requiriendo soporte y revisión profesional. Faltan cobertura fiscal completa, documentos/fuentes nativas, pagos/devoluciones parciales y cualificación productiva.

La verificación consulta en lote cabeceras, líneas, revisiones, recibos y documentos, manteniendo el mismo validador de posteo usado por las respuestas individuales. Una prueba automática compara consultas con1 y10 documentos para detectar el retorno de lecturas por documento. No se retira la comprobación criptográfica para mejorar tiempos.
