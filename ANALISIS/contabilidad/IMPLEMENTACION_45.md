# Implementación 45 · Reserva a asiento real y contrapartida

**Avance global: 38,89 % (28/72 hitos).** Se añade un tramo operativo sustancial al flujo anterior: revisión de reconocimiento, asiento real y contrapartida desde el panel, con dos confirmaciones por operación. ACC-008 y los hitos contables relacionados ya estaban puntuados como incrementos parciales; la métrica estable no añade crédito por ampliar esos mismos hitos. La aceptación global y el recorrido corporativo Analemática permanecen pendientes.

## Comportamiento funcional

El titular carga reservas con revisión fiscal y el catálogo contable de su empresa. Selecciona expresamente cuenta por cobrar (ASSET), ingreso (REVENUE) e impuesto por pagar (LIABILITY cuando hay impuesto), fecha económica y huellas de evidencia de prestación/política contable. No se infieren códigos PUC ni hechos económicos a partir de una reserva o solicitud de factura.

Primera confirmación: el titular declara SERVICE_DELIVERED y que revisó cuentas, moneda y evidencias. El servidor valida identidad vigente y fuente bloqueada, revisión fiscal actual, bruto exacto, periodo abierto y cuentas activas del plan de la empresa. Solo permite COP, servicios cuyo plazo terminó y fecha económica no futura ni anterior al cierre previsto del servicio. Un plazo vencido no prueba prestación: la declaración y evidencias son del titular, sin verificación independiente.

Las reservas con deposit_paid distinto de cero se rechazan tanto en revisión como en contabilización: necesitan conciliación y política de aplicación de anticipos. No se registra cartera completa ignorando pagos previos.

La revisión se persiste y muestra previsualización: débito por cobrar por el bruto, crédito al ingreso por el neto y crédito al pasivo tributario por el impuesto explícitamente revisado. La segunda confirmación registra el asiento mediante LedgerEngine.post_lines: partida doble, periodo, actor, valoración base, hash v2, auditoría, recibo idempotente y outbox existentes. Una clave estable por reserva impide contabilizarla dos veces bajo revisiones diferentes. La evidencia de origen se guarda en la misma transacción; su fallo revierte asiento/recibo/eventos nuevos.

## Contrapartida y conservación de historia

Desde el asiento contabilizado, el titular revisa motivo/soporte y confirma. Una segunda autorización crea la contrapartida mediante el LedgerEngine existente, vinculada al original. Ambas operaciones son idempotentes con evidencia de origen; no se borra o modifica el original. Si falta esa evidencia en un replay, se bloquea y exige conciliación, sin reconstruirla retrospectivamente.

La API permite contrapartida de un reconocimiento existente aunque la reserva haya sido cancelada. Reintentar el reconocimiento original después de revertir informa reversed=true y no vuelve a cargar el ingreso. Cerrar el periodo o cambiar la fuente/revisión/cuentas bloquea los pasos incompatibles; no se omiten controles para forzar una operación.

El registro contable no acredita factura DIAN ni transfiere dinero. Las revisiones tributarias y de política siguen siendo declaraciones del titular, no validaciones normativas independientes.

## Interfaz y rutas

Nueva sección `Reconocimiento contable de reservas` en el panel ERP existente, con azul/acento claro/blanco. Consume el núcleo de Analemática compartido; ambas confirmaciones son controles separados. Actualiza los indicadores mediante el mecanismo revisionSignal existente y muestra referencia del asiento y de la contrapartida.

Bajo `/api/v1/mi-negocio/contable/contabilidad/cuentas/`, con provider_id autorizado:

- GET `cuentas-reconocimiento/`: cuentas activas de funciones permitidas, máximo 500; si se supera, exige búsqueda paginada en lugar de truncar silenciosamente.
- POST `revisar-reconocimiento-reserva/`: fuente, revisión fiscal, fecha, mapeo, evidencias, hecho declarado, expected_revision y primera confirmación.
- POST `contabilizar-reserva/`: reserva, revisión contable persistida y segunda confirmación.
- POST `revisar-contrapartida-reserva/`: reserva, motivo, evidencia y primera confirmación.
- POST `contrapartida-reserva/`: reserva, revisión de contrapartida y segunda confirmación.

Las rutas de escritura usan JSON estricto de 8 KiB y cabeceras privadas/no-store. Los helpers internos no sustituyen autenticación empresarial. No se añaden tablas o migraciones; se usan modelos y servicios existentes.

## Evidencia de efectos reales en el entorno aislado

- **214 métodos Python aprobados** en quince suites; veinte nuevos prueban revisión sin asiento, contabilización balanceada y reportes, replay, segunda confirmación, fecha/servicio futuro, cuentas incompatibles, fuente cambiada, periodo cerrado, revocación, integridad, impuestos explícitos, contrapartida exacta, cancelación, prohibición de recontabilizar, evidencia perdida y fallos con rollback. Incluyen anticipos existentes o registrados entre revisión y contabilización.
- **29 escenarios contables PostgreSQL aprobados**. Tres nuevos compiten por revisión, contabilización y contrapartida. Queda una revisión, un asiento y una contrapartida, con replay; el beneficio del caso pasa de 100.00 a 0.00, el hash original permanece y la cadena es válida.
- **42 comprobaciones integradas Chromium → sesión/cookie/CSRF → Django/ORM aprobadas**. El usuario completa ambas confirmaciones del asiento y ambas de su contrapartida desde el panel.
- La prueba web parte de movimientos previos por 15 COP: contabilizar 100 COP eleva débitos y créditos a 115; revertir conserva ambos movimientos y eleva el acumulado a 215, dejando la cuenta por cobrar en 0.00. Se verifica igualdad de débitos/créditos, no desaparición de historia.
- Vista móvil de 390 px sin desbordamiento y TypeScript estricto del nuevo componente sin errores. La restauración PostgreSQL conserva los nuevos registros y los controles del ledger.

Evidencia: `evidencias/implementacion-45.json`; captura privada local `/tmp/sgacd-recognition-posted-90.png`. Fuente estable durante el perfil contable final. No se ejecutó CI remoto ni build Next.js completo.

## Límites pendientes para aceptación

La evidencia de prestación/política es una huella declarada: no prueba existencia del documento, vigencia normativa o entrega independiente. El flujo no certifica NIIF, impuestos o DIAN. Falta soporte de anticipos/compensaciones, moneda individual extranjera, retenciones y otros hechos económicos, así como revisión contable profesional y política normativa formal de reconocimiento.

La UI trabaja sobre reservas CONFIRMED con revisión fiscal; el otro modelo turístico, fuentes COMPLETED y navegación paginada completa de reconocimiento requieren integración específica. La API de contrapartida admite canceladas, pero localizar esas reservas en la UI necesita ampliar las fuentes. Reanudar revisiones anteriores y modificar una revisión de contrapartida exige historial/recuperación controlados.

Los reviews y pruebas de origen están en un outbox mutable para operadores privilegiados. El ledger sí utiliza sus controles/hash v2 existentes, pero esto no convierte la declaración humana en atestación independiente ni ZKP. Faltan privilegios/despliegue reales, pruebas de carga, periodos/roles productivos y revisión independiente.

La consola corporativa Analemática aún necesita su puente autorizado y recorrido propio; compartir su LedgerEngine no acredita esa integración completa. Emisión/acuse fiscal y demás pools siguen pendientes. Los cambios permanecen locales: sin datos reales modificados, pagos, commit, push o despliegue.
