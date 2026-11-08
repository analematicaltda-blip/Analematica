# Decisiones iniciales de arquitectura

## ADR001 · Reutilizar núcleo compartido

Analemática y ERP turístico utilizan `apps.core_erp.accounting`, ubicado en `BACKEND/ANALEMATICA-BACKEND/core_erp/accounting`. Se conservan proxies y namespaces de despliegue. Se corrigen defectos con pruebas y se revisa cada consumidor; no se instala un segundo ledger sin reconciliación de saldos/historia.

## ADR002 · Atomicidad local y consistencia entre servicios

Kafka, gRPC y Event Sourcing no proporcionan por sí solos ACID distribuido ni exactly-once de negocio. El agregado contable y su outbox deben confirmarse en una transacción SQL; los consumidores deduplican por tenant/evento y rechazan payloads divergentes. Estados externos pendientes y compensaciones son explícitos. Si se requiere una transacción global estricta, debe diseñarse y probarse su coordinación; no anunciarla como implementada.

## ADR003 · Confidencialidad de bóveda

Cifrado de archivos fiscales antes de llegar al ERP; KEK y firma bajo custodia del cliente. El proveedor fiscal puede necesitar leer XML para validarlo: documentar esa frontera de confianza. El ERP aún conoce hechos contables mínimos autorizados; no afirmar conocimiento cero de toda la base financiera.

`drive.file` y `Files.ReadWrite.AppFolder` no son permisos de solo escritura. Revisar OAuth real y lectura/modificación permitidas. SSE-C por sí solo no sustituye cifrado en cliente ni garantiza que el servicio de almacenamiento nunca conozca la clave. El navegador negocia TLS; no se garantiza TLS1.3 en todos los destinos sin medirlo.

## ADR004 · Integridad no es ZKP

Un hash o cadena local permite detectar ciertas modificaciones, pero quien controla base y hashes puede recalcularlos. Requiere controles SQL, anclaje/firma independiente y separación de privilegios. Merkle, firmas y ZKP son mecanismos distintos. No reescribir hashes históricos: introducir versión y migración/evidencia compatible tras auditar consumidores.

## ADR005 · Cumplimiento y autorización

Conservar periodos y cierres legales aunque existan proyecciones continuas. Reglas fiscales/laborales/ambientales tienen vigencia y evidencia revisada. La IA propone; no contabiliza o envía fondos libremente. Dos autorizaciones del solicitante y tercera de impacto siguen obligatorias para ejecución financiera/control. No se hereda acceso a la billetera por ser empleado del ERP.

## ADR006 · Offline y métricas honestas

CRDT no resuelve la integridad de dinero ni firmas concurrentes. Offline prepara eventos/borradores cifrados; el servidor valida versión, periodo, identidad, saldo y permisos antes de consumirlos. No se liquidan fondos offline. Los objetivos de latencia/precisión/seguridad se miden; “1.000%” se interpreta como exigencia de mejora, no como porcentaje técnico verificable.
