# Implementación 44 · Flujo funcional de reserva a solicitud de factura

**Avance global: 38,89 % (28/72 hitos).** Se completa un tramo funcional sustancial de ACC-008: fuente persistida y autorizada, revisión del desglose, segunda confirmación y solicitud idempotente desde el panel. ACC-008 ya tenía dos hitos parciales acreditados; no se infla el porcentaje por ampliar ese mismo alcance. La aceptación completa exige consumidores/acuses fiscales e integración de ambos sistemas todavía pendientes.

## Lo que ya funciona en el ERP

1. El titular carga una página de hasta 20 reservas CONFIRMED de su empresa verificada; hay cursor para siguientes páginas. Se muestran total, moneda de empresa, revisión vigente y presencia de solicitud; no se devuelven datos personales del cliente.
2. Introduce componentes de neto/impuesto, tratamiento y código/referencia de política, más huella de evidencia. No se precarga un impuesto, exención o neto supuesto.
3. Confirma expresamente la revisión. El servidor vuelve a validar identidad, bloquea empresa/vínculo/prestador/reserva, comprueba estado y contrasta el bruto exacto de los componentes con el total real. Guarda una revisión versionada con actor, evidencia, snapshot normalizado y huella de la fuente.
4. Una segunda confirmación explícita del mismo titular crea la solicitud desde la revisión persistida. El cliente solo envía reserva y review_id, nunca un snapshot alternativo. El outbox incorpora la referencia y digests de la revisión, evidencia y fuente.
5. Repetir la solicitud devuelve el mismo registro. Una revisión antigua, reserva modificada, empresa ajena o autorización revocada bloquean el envío. Después de solicitar, no se permite otra revisión que pudiera reemitir la misma venta; los ajustes tendrán un flujo independiente.

El panel usa azul, acento azul claro y blanco; las confirmaciones son controles separados, con botones deshabilitados hasta aprobar. Se revisó una captura móvil con datos sintéticos y no hay desbordamiento. El resultado indica que es una solicitud registrada, sin factura emitida/aceptada ni asiento.

## Componentes y rutas

Servicio: `apps/domain_business/comercial/services/reservation_fiscal.py`. Reutiliza el contrato y cola del núcleo compartido de Analemática. No requiere tablas ni migraciones nuevas: las revisiones se agregan al outbox existente y el modelo de reserva ya existe en las migraciones nativas/fresh.

Rutas bajo `/api/v1/mi-negocio/contable/contabilidad/cuentas/`, siempre con provider_id autorizado:

- GET `fuentes-reserva-fiscal/`, cursor opcional despues_id.
- POST `revisar-reserva-fiscal/`: reservation_id, items, evidence_digest, confirmed=true y expected_revision.
- POST `solicitar-factura-reserva/`: reservation_id, review_id y confirmed=true.

Las dos rutas de escritura usan el parser acotado de 8 KiB. Un desglose extenso debe respetar ese límite aunque la primitiva de contrato admita hasta 100 componentes. No se reciben archivos fiscales, llaves o documentos en texto claro.

## Verificación

- 194 métodos Python aprobados en catorce suites; doce nuevos del flujo, incluidos total incompatible, cambio de fuente, actor/revocación, estado pendiente, conflicto de versión, revisión antigua, bloqueo después de solicitar, rollback, fallo de persistencia, referencia de revisión y recorrido DRF. Se rechazan campos snapshot extra e identificadores inválidos.
- 26 escenarios contables PostgreSQL aprobados: dos nuevos compiten por revisión inicial y por solicitud. Se conserva una revisión ante conflicto de expected_revision, y un request con una inserción/un replay. La consulta paginada devuelve correctamente revisión y solicitud en PostgreSQL y SQLite.
- 37 comprobaciones integradas de Chromium → sesión/cookie/CSRF → Django/ORM aislado. El usuario completa ambas confirmaciones desde la nueva sección del panel. Se verifican botones bloqueados antes de autorizar y vista móvil de 390 px.
- TypeScript estricto del componente sin errores. Se conserva el procedimiento de restauración PostgreSQL, incluyendo las nuevas revisiones y solicitudes.

Evidencia: `evidencias/implementacion-44.json`. Captura privada local: `/tmp/sgacd-reservation-billing-86.png`. Fuente estable durante el perfil contable. No se ha ejecutado CI remoto ni build Next.js completo.

## Límites contables, fiscales y de producción

La revisión es una declaración del titular con referencia de evidencia; no acredita por sí sola vigencia normativa, tasa oficial, firma fiscal o validación de DIAN. `legal_tax_policy_verified=false` se conserva. Los importes de reserva se interpretan en la moneda configurada de la empresa; este flujo no habilita reservas con moneda individual extranjera ni FX implícito. La política/custodia de moneda de fuentes legadas requiere revisión antes de producción.

Confirmar una solicitud no reconoce automáticamente ingresos: no se modifica el ledger, no se realiza cobro y no se publica a sistemas externos. Pendientes emisor/consumidor fiscal con recibos y acuses reales, rechazo/ajustes/notas, reglas tributarias versionadas y reconocimiento contable según política y hecho económico. No se afirma cumplimiento integral de ledger-first con este tramo.

Los registros de revisión son append-only desde este servicio, pero el outbox no es criptográficamente inmutable contra un operador privilegiado. Su hash detecta incompatibilidades contractuales; no es ZKP ni firma independiente. Faltan autorización/sesiones bajo más intercalados, políticas de retención, índices/carga y auditoría independiente.

La UI permite completar revisión y solicitud en una sesión; retomar visualmente una revisión anterior después de recargar requiere mejorar el detalle histórico. No se reconstruyen aprobaciones automáticamente. El modelo Reservation turístico alternativo y la consola corporativa Analemática siguen pendientes de integración propia; el uso de su núcleo compartido no acredita ese recorrido.

Sin datos reales modificados, emisión fiscal, pagos, commit, push o despliegue.
