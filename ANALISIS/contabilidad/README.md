# Plan de implementación contable · Analemática y ERP turístico

Directriz base: matriz de siete pools recibida del usuario el 2026-11-08. Estado: **inicio de implementación, no producción**. Se conserva y refuerza el motor compartido; no se sustituye el sistema ni se ejecutan migraciones sobre datos reales.

- [Directriz y contratos](DIRECTRIZ.md).
- [Matriz de implementación](matriz-pools.csv): tareas, prioridad, dependencias, responsables por área y criterios verificables.
- [Hallazgos y primera corrección](HALLAZGOS_01.md).
- [Decisiones de arquitectura](DECISIONES.md): consistencia, cifrado, regulación, autorizaciones y límites de medición.
- [Entrega al repositorio](../entregas/ENTREGA_MAIN_37.md): consolidación, pruebas y estado de publicación.

Código canónico contable: `BACKEND/ANALEMATICA-BACKEND/core_erp/accounting`. Los modelos contables de Analemática y ERP turístico son proxies de ese núcleo. `BACKEND/deployment/tourism_bindings.py` preserva los namespaces originales. El UUID de TourismProvider no equivale al UUID de Tenant contable: usar el vínculo verificado antes de conectar nuevos flujos.

## Orden de ejecución

1. **Fundación y seguridad del ledger (Pool3/4):** invariantes monetarias, ámbito empresarial, periodos, idempotencia, auditoría, concurrencia y reversión. Primera corrección entregada con nueve pruebas ORM; todavía falta integrar el flujo completo de posteo y sus efectos.
2. **Eventos y ciclo comercial (Pool1/3):** outbox transaccional, contratos versionados y consumidores idempotentes; después facturación y bóveda cliente/BYOS.
3. **Operación, personal y costos (Pool2):** novedades verificadas, aptitudes/permisos, reglas laborales vigentes y causaciones trazables.
4. **Fiscalidad e integraciones (Pool1/4):** adaptadores oficiales de habilitación con secretos del cliente y estados pendientes/aceptados/rechazados; sin comprobantes inventados.
5. **Analítica explicable y sostenibilidad (Pool5/6):** proyecciones reproducibles, ratios definidos, simulaciones y factores versionados.
6. **Asistencia supervisada (Pool7):** consultas de solo lectura y sugerencias con evidencia; ejecución separada con dos autorizaciones del solicitante y tercera de impacto.

En cada corte: reproducir hallazgo → evaluar dependencias → corregir en alcance limitado → probar aislamiento e integridad → registrar evidencia y actualizar matriz. Un archivo, una regla declarada o un hash no acreditan un proceso operativo. No se presupone un 99.8% de precisión, latencia250ms ni inmunidad a vulneración.

Las tareas pendientes del plan anterior siguen en [el registro del ecosistema](../produccion/PENDIENTES-PRODUCCION-ECOSISTEMA.md). La contabilidad no habilita por sí sola pagos, DIAN, bancos, nómina electrónica, publicación, datos de salud, automatización de cuentas ni billetera empresarial para empleados.
