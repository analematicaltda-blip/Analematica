# Implementación 30 · Contrato comercial hacia facturación

**Avance: 36,11 % (26/72 hitos).** ACC-008 acredita un incremento funcional acotado y su verificación; queda PARCIAL, sin aceptación completa.

## Incremento compartido

`core_erp/accounting/invoice_intent.py` prepara un contrato puro `sgacd-invoice-intent-v1` desde un snapshot explícito. Admite oportunidad CRM en WON o reserva en CONFIRMED, empresa y origen UUID canónicos, revisión positiva y monedas COP/USD/EUR. La empresa debe coincidir con el contexto recibido del llamador. Esto no autentica al llamador ni verifica el estado real del origen: el futuro productor deberá consultar su fuente autorizada bajo bloqueo/transacción.

Cada solicitud admite entre 1 y 100 componentes únicos, con neto e impuesto en cadenas decimales exactas, dos decimales y límites de magnitud. Se rechazan floats, negativos, NaN, duplicados y campos extra. Cada componente exige categoría tributaria y referencia de política explícitas; EXEMPT/EXCLUDED no admiten impuesto distinto de cero. El contrato no decide por sí mismo tratamientos turísticos ni acredita vigencia jurídica de una referencia.

Genera totales exactos, payload normalizado y digest determinista. La identidad idempotente combina empresa, tipo/origen y revisión. Si el contenido cambia bajo la misma revisión conserva identidad pero cambia digest: un consumidor persistente deberá rechazar el conflicto; este módulo todavía no almacena recibos ni deduplica entregas. Una nueva revisión tiene otra identidad.

La salida declara REQUEST_ONLY, sin aceptación fiscal, asiento, publicación, autoridad del origen o política tributaria verificados. No genera XML/PDF, CUFE, firma o acuse DIAN. No altera estados comerciales existentes.

## Verificación

134 métodos Python aprobados en ocho suites; siete nuevos prueban importes/totales, rechazo de estados y empresas incompatibles, límites/duplicados, clasificación tributaria explícita e identidad/digest. El perfil accounting/core y el workflow incluyen el contrato. El workflow remoto no fue ejecutado. Fuente estable durante la prueba local.

Evidencia: `evidencias/implementacion-30.json`. PostgreSQL no se repitió: este incremento no incorpora persistencia ni cambios de esquema.

## Siguiente integración pendiente

Adaptadores para los modelos comerciales reales, autorización empresarial, lectura bloqueada de estado/revisión, persistencia transaccional del request/outbox y recibo del consumidor con rechazo de payload cambiado. Después, integración fiscal en habilitación y conciliación de rechazo/aceptación real. El contrato compartido aún no acredita recorrido extremo a extremo de Analemática o ERP turístico. No se crean compromisos fiscales ni contables a partir de un snapshot enviado por un usuario sin validación autoritativa.

Sin cambios de datos del usuario, commit, push o despliegue.
