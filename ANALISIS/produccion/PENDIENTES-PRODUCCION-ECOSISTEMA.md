# Estado y pendientes del ecosistema

Revisión documental: 2026-11-08. Alcance: Analemática, SGA-ERP-TUR y SGA-TUR, con servicios compartidos y billetera. **Plan maestro en curso; producción NO habilitada.** Los bloques entregados contienen implementaciones y pruebas acotadas; no implican cumplimiento integral de cada frente. No se dispone de evidencia para afirmar un porcentaje global de terminación.

El estado por frente se conserva en [tablero del plan](../../INTEGRACIONES/plan-maestro/tablero.json). Este documento reúne pendientes y criterios de cierre, sin sustituir las evidencias ni los registros canónicos de la billetera. Los responsables indicados son áreas propuestas, no personas formalmente asignadas.

## Falta desarrollar o comprobar en local

Estos pendientes no se resuelven simplemente trasladando el código a un servidor.

| ID | Prioridad | Pendiente | Área responsable | Criterio para cerrar |
| --- | --- | --- | --- | --- |
| LOC-01 | Crítica | Builds completos ERP/Turismo: falta `@sarita/shared-ui` y siguen contratos/fuentes incompletos | Frontend/arquitectura | Recuperar o implementar contratos reales, compilar ambos sin ignorar errores y verificar recorridos; conservar identidad azul metalizado/celeste/blanco |
| LOC-02 | Alta | Auditoría funcional integral institucional y ERP | Arquitectura/QA | Verificar requisitos con trazas y pruebas de extremo a extremo, después de inventariar rutas/modelos; no clasificar una función por tener botón o archivo |
| LOC-03 | Alta | Reservas definitivas, interfaz de disponibilidad, tarifas/impuestos y pagos | Backend/comercial | Probar confirmación, concurrencia, cancelación, reglas comerciales e idempotencia; no confirmar un cobro sin recibo real validado |
| LOC-04 | Alta | Identidad común, delegaciones empresariales, jurisdicción, SSO y recuperación completa/WebAuthn | Identidad/seguridad | Matriz y pruebas positivas/negativas por rol, empresa y territorio; no equiparar JWT o UUID de dominios diferentes |
| LOC-05 | Alta | Integración efectiva de telemetría con AiSOC | Seguridad/infraestructura | Recepción, detección de prueba y trazabilidad de eventos sin secretos; respuestas automáticas deshabilitadas |
| LOC-06 | Media | Evaluación de IA y contenido multimedia | IA/QA | Instalar/configurar modelo autorizado y medir calidad, privacidad, licencia, latencia y coste; probar imágenes/vídeo/voz/transcripción antes de habilitarlos |
| LOC-07 | Alta | Cobertura y operación reproducible | QA/infraestructura | Ampliar pruebas a procesos pendientes, resolver fallos, fijar dependencias/imágenes, revisar vulnerabilidades y límites compartidos; `pip check` no es un escaneo de seguridad |

## Requiere infraestructura, proveedores o equipos reales

La infraestructura puede ser de validación; no es necesario activar producción para comenzar estos ensayos. No se autoriza su activación por la mera existencia de este documento.

| ID | Prioridad | Validación pendiente | Área responsable | Evidencia necesaria |
| --- | --- | --- | --- | --- |
| REAL-01 | Crítica | Recuperación integral y continuidad | Operaciones/DBA | Restaurar esquema completo PostgreSQL, datos, adjuntos, configuración y claves hacia un entorno aislado; medir pérdida admisible de datos y tiempo de recuperación; verificar copias externas y retención |
| REAL-02 | Crítica | Seguridad e identidad de billetera | Seguridad/móvil | Cumplir los 19 pendientes canónicos con equipos, proveedores y revisión correspondiente; no cerrar usando fixtures |
| REAL-03 | Alta | Control nativo Android/iOS/escritorio | Móvil/escritorio/QA | Dispositivos físicos, Mac/Xcode para iOS, permisos, cuenta correcta, observaciones cambiantes, dos autorizaciones del solicitante y tercera de impacto, parada y desconexión |
| REAL-04 | Alta | Distribución e integridad | Release/seguridad | Compilaciones firmadas, instalación, actualización, revocación y recuperación en cada plataforma; verificar atestación, biometría, pines y protección de vistas críticas |
| REAL-05 | Alta | Correo y plataformas oficiales | Integraciones/QA | Correo de recuperación entregado y flujos supervisados con cuentas autorizadas de Meta/TikTok/Gmail/YouTube; comprobar permisos, recibos y resultados reales |
| REAL-06 | Alta | Seguridad operativa y carga | Infraestructura/seguridad | HTTPS, secretos y permisos SQL, aislamiento, sesiones, límites entre procesos, métricas/alertas, carga y revisión de dependencias; conservar el cierre seguro ante fallos |
| REAL-07 | Alta | Integraciones comerciales y fuentes oficiales | Producto/integraciones | Validar RNT, pasarelas/conciliación y obligaciones aplicables con fuentes/proveedores autorizados; separar registro institucional de publicación comercial |

## Evidencia existente y límites

- [Auditoría, bloque 1](../../INTEGRACIONES/plan-maestro/AUDITORIA_BLOQUE01_28.md): 161 requisitos inventariados; 153 no verificados, 7 parciales y 1 defecto de fuente en ese corte. No se ha acreditado después una auditoría integral que cierre esa matriz.
- [Operación, bloque 8](../../INTEGRACIONES/plan-maestro/BLOQUE08_OPERACION_35.md): 20 grupos aprobados, 2 con omisiones y 1 fallido. Ambos builds completos fallan. Las omisiones no cuentan como pruebas aprobadas.
- [Respaldos, bloque 9](../../INTEGRACIONES/plan-maestro/BLOQUE09_RESPALDOS_36.md): copias SQLite cifradas hasta64MiB, restauración editorial y contratos PostgreSQL aislados aprobados. No demuestra recuperación productiva del ecosistema ni recuperación financiera integral de la billetera.
- [Guía de operación y reversión](../../INTEGRACIONES/operacion/README.md) y [respaldos](../../INTEGRACIONES/operacion/RESPALDOS.md): procedimientos locales y límites, sin conmutación automática de datos reales.
- [Pendientes canónicos de billetera](PENDIENTES-PRODUCCION-BILLETERA.md): generado desde `WALLET-BACKEND/offline/src/sgacd_wallet_offline/production_pending.json`; producción permanece deshabilitada.

No se ejecutaron pruebas nuevas para crear esta consolidación: se revisaron los informes registrados y la coherencia del documento canónico de billetera. Las evidencias originales distinguen fixtures, modelos reales de datos, transportes simulados y dispositivos físicos pendientes.

## Regla de cierre y entrega

Cerrar cada pendiente con evidencia fechada, responsable identificado, criterio satisfecho y revisión de regresiones. Conservar las funciones existentes y sus datos. No activar cobros, publicación, control de equipos o producción por asumir que un módulo está terminado. No regenerar claves para intentar recuperar datos cifrados.

Los cambios de desarrollo siguen locales y sin publicación nueva en Git por esta revisión. Commits, push y actualización de main quedan sujetos a la instrucción explícita del usuario al terminar la entrega correspondiente.

## Avance contable posterior

[Implementación02 del núcleo compartido](../contabilidad/IMPLEMENTACION_02.md): posteo/outbox local, identidad ERP verificada, hashv2 y reportes en moneda base. Continúan pendientes las migraciones históricas sobre copias reales, consumidores externos, apertura, monedas complejas, impuestos, integraciones, interfaz y controles SQL productivos. No cierra el plan completo.

[Implementación contable03](../contabilidad/IMPLEMENTACION_03.md) añade un consumidor local deshabilitado por defecto. Publicador/broker externo, programación del worker, reconciliación/rebuild y retención siguen abiertos. El acuse local no es una publicación en Kafka ni un pago o validación fiscal.

## Corte 40 · Rentabilidad contable

Consulta empresarial de margen neto implementada localmente; ver `../contabilidad/IMPLEMENTACION_04.md`. Faltan pantalla, clasificación de liquidez e ingresos operativos, integración de habitaciones/paquetes y pruebas con contabilidad real. No habilitar ratios turísticos con denominadores estimados ni considerar este corte una certificación fiscal.

## Corte 41 · Liquidez con clasificación revisada

Ver `../contabilidad/IMPLEMENTACION_05.md`. Antes de producción: revisar con contabilidad la cobertura de cuentas y evidencia; ensayar migración nativa histórica; integrar pantallas; definir políticas por vigencia y protección SQL privilegiada. La clasificación declarada no acredita fondos disponibles ni autoriza pagos.

## Corte 42 · Consulta web contable

Pendientes de producción: recorrido integrado con backend y sesión reales; vínculo contable corporativo de Analemática; compilación completa de ERP; clasificación supervisada y accesibilidad. Ver `../contabilidad/IMPLEMENTACION_06.md`. Las pruebas de contrato UI sintéticas no acreditan estos puntos.

## Corte 43 · Medición y recorrido contable integrado

Línea base: 22,22 % de hitos, sin aceptación productiva. El navegador ERP ya consulta Django/ledger real en fixture aislado. No acredita conexión contable de la consola corporativa Analemática, bancos, DIAN ni datos reales. Ver `../contabilidad/PROGRESO.md` e `IMPLEMENTACION_07.md`.

## Corte 44 · Revisión de liquidez en ERP

Formulario implementado y probado con sesión/CSRF y base aislada. Pendientes: cobertura profesional de cuentas/evidencia, políticas por vigencia, historial completo, accesibilidad/móvil integral, fallos de red y catálogos grandes; vinculación contable corporativa Analemática. Ver `../contabilidad/IMPLEMENTACION_08.md`.

## Corte 45 · Historial contable de clasificaciones

Historial ERP implementado y probado localmente. Pendientes: protección SQL privilegiada/firma independiente, vigencias y selección histórica de política al calcular, auditoría con datos reales y consola Analemática. Ver `../contabilidad/IMPLEMENTACION_09.md`.

## Corte 46 · Revisión histórica explícita

Implementada selección de clasificación para recalcular liquidez. No equivale a snapshot de un informe publicado; faltan vigencias/bitemporalidad según necesidad, consola Analemática y validación profesional con datos reales. Ver `../contabilidad/IMPLEMENTACION_10.md`.

## Corte 47 · Escenarios de caja

Simulación local de datos declarados implementada. Antes de uso predictivo faltan interfaz, sensibilidad, backtesting temporal, series reales, supuestos estacionales y validación profesional/rendimiento. No son saldos oficiales, recomendaciones ni autorización de pagos. Ver `../contabilidad/IMPLEMENTACION_11.md`.

## Corte 48 · Backtesting temporal

Holdout declarado implementado y probado. Pendientes: ventanas múltiples, sensibilidad, interfaz, calibración/procedencia y contraste con series reales. No interpretar un único holdout como precisión certificada. Ver `../contabilidad/IMPLEMENTACION_12.md`.

## Corte 49 · Sensibilidad de escenarios

Comparación aditiva implementada y probada. No confundir con elasticidades o efectos fiscales reales; faltan interfaz, calibración, ventanas múltiples, series verificadas y rendimiento. Ver `../contabilidad/IMPLEMENTACION_13.md`.

## Corte 50 · Interfaz de escenarios ERP

Base y sensibilidad conectadas y probadas en fixture real aislado. Pendientes interfaz de backtesting, cambios múltiples, móvil/accesibilidad completos, fallos de red, procedencia de series y cualificación profesional. Ver `../contabilidad/IMPLEMENTACION_14.md`.

## Corte 51 · Interfaz de backtesting

Interfaz conectada y probada localmente con datos sintéticos. Pendientes ventanas múltiples, procedencia de series reales, calibración y revisión profesional/rendimiento; móvil/accesibilidad y fallos de red integrales. Ver `../contabilidad/IMPLEMENTACION_15.md`.

## Corte 52 · Múltiples ventanas

Motor implementado y probado con escenarios sintéticos. Pendientes interfaz de ventanas, series reales contrastadas y cualificación profesional/calibración/rendimiento. No asumir independencia cuando se solapan periodos. Ver `../contabilidad/IMPLEMENTACION_16.md`.

## Corte 53 · Inmutabilidad SQL contable

Triggers v1 instalados solo en fixture privado. Pendientes: ensayo de migración nativa histórica, roles DDL/DML separados, privilegios mínimos, verificación de presencia/estado tras migrar o restaurar, protección de otras tablas y firmas/auditoría independientes. No protege frente al propietario/superusuario que puede desactivarlos. Ver `../contabilidad/IMPLEMENTACION_17.md`.

## Corte 54 · Disponibilidad y esquema contable

Readiness y protección contra tabla temporal homónima probados localmente. Pendientes: atestación de cuerpos, roles reales, restauración integral con llaves, RPO/RTO, ensayo histórico y enlace del orquestador a readiness. El HTTP503 no bloquea por sí solo todas las APIs. Ver `../contabilidad/IMPLEMENTACION_18.md`.

## Corte 55 · Restauración del ledger

Dump/restore de fixture PostgreSQL verificado con datos, estructura, secuencias IDENTITY, restricciones, índices y guards. Faltan propietario/ACL reales, llaves y medios externos, migraciones históricas, retención/cifrado operativo, RPO/RTO y ensayo independiente. Ver `../contabilidad/IMPLEMENTACION_19.md` y `OPERACION_RECUPERACION.md`.

## Corte 56 · Privilegios contables

Auditor parcial implementado y probado con conexiones de roles temporales. Pendientes: grants/roles de todas las tablas reales, RLS/funciones privilegiadas, operación completa restringida y activación explícita del control de readiness en despliegue. No se modificaron roles reales. Ver `../contabilidad/IMPLEMENTACION_20.md`.

## Corte 57 · Operación contable restringida

Posteo/reintento/contrapartida/informe/proyección probados con cuenta limitada real del fixture. Pendientes todas las rutas ERP/Analemática, roles reales y revisión de UPDATE(id), multimoneda, cierre, catálogo, publicación y separación de migraciones. El contrato no aplica grants. Ver `../contabilidad/IMPLEMENTACION_21.md`.

## Corte 58 · Contrapartida multimoneda

Reversión v2 exacta implementada y probada con valoración original. Pendientes: fuentes FX reales, legados/reconciliación, revaluación/diferencias, operaciones parciales/externas, interfaces y aprobación profesional de casos reales. Ver `../contabilidad/IMPLEMENTACION_22.md`.

## Corte 59 · Diagnóstico de conciliación

Inspección paginada implementada y probada, sin reparar datos. Pendientes interfaz, snapshot de recorrido, empresas inactivas y conciliación profesional con soportes/asientos aprobados. No borrar saldos iniciales ni rehashar legados para ocultar hallazgos. Ver `../contabilidad/IMPLEMENTACION_23.md`.

## Corte 60 · Vista del diagnóstico

Panel ERP implementado y probado. Pendientes snapshot estable, contexto corporativo Analemática, inactivos y revisión profesional con soportes/ajustes autorizados; accesibilidad/red/carga y compilación completa. No interpretar una página limpia como certificación del libro. Ver `../contabilidad/IMPLEMENTACION_24.md`.

## Corte 61 · Sobre cifrado cliente

SDK criptográfico probado con llaves sintéticas. Pendientes uploads existentes, KEK/custodia/recuperación reales, empaquetado XML/PDF, BYOS/OAuth, versiones/antirrollback y auditoría/entrega del cliente. Rewrap no revoca copias antiguas; no se acredita conocimiento cero de las cargas actuales. Ver `../contabilidad/IMPLEMENTACION_25.md`.

## Corte 62 · Preview de sobres fiscales

Contrato estructural probado; no autentica el ciphertext ni valida documento fiscal ni almacena archivos. Pendientes BYOS, KEK/custodia/recuperación, cargas reales/versiones, logs/APM y límites del proxy. No tratar un preview aceptado como archivo almacenado o factura autorizada. Ver `../contabilidad/IMPLEMENTACION_26.md`.

### Contabilidad · Implementación 27 · PostgreSQL BYOS parcial

Validar propiedad y autorización del destino cliente, roles y migración propios, conectividad/TLS, revocación/caídas, backup y restauración documental, custodia/recuperación de KEK y versionamiento/antirrollback. Conector probado solo en una base desechable separada, con AEAD sintético y rol limitado. No está conectado a UI/API. El preview no almacena. La restauración del ledger no acredita la del destino cliente. Otros proveedores BYOS/OAuth pendientes. Véase `ANALISIS/contabilidad/IMPLEMENTACION_27.md`.

### Contabilidad · Implementación 28 · Recuperación documental local

Restauración de sobres cifrados y vinculación probada en base nueva desechable, con controles conservados sin bootstrap. Continúan pendientes ACL/roles recuperados, respaldo cifrado integral y retención, recuperación de KEK por el cliente, grandes volúmenes, fallos parciales y RPO/RTO reales. El ensayo usa datos y llaves sintéticos; no cerrar producción con esta evidencia. Véase `ANALISIS/contabilidad/IMPLEMENTACION_28.md`.

### Contabilidad · Implementación 29 · Revocación y fallos de conexión

Probados SELECT/INSERT revocados sobre rol limitado y sesión terminada, con fallo explícito y replay tras reconexión sin duplicación. Aún pendientes particiones/latencia, timeouts operativos, fallo entre commit y respuesta, OAuth y revocación de credenciales reales. La revocación no elimina copias descargadas ni invalida KEK. No cerrar aceptación productiva con esta fixture local. Véase `ANALISIS/contabilidad/IMPLEMENTACION_29.md`.

### Contabilidad · Implementación 30 · Contrato comercial parcial

Conectar el contrato de invoice intent a fuentes CRM/reserva autorizadas bajo transacción; implementar request/outbox y consumidor persistente con rechazo de conflicto de digest. Verificar referencias tributarias vigentes, rechazo/acuse en habilitación fiscal e integración de ambos sistemas. El contrato puro no acredita emisión, cobro, asiento, DIAN ni autoridad del snapshot. Véase `ANALISIS/contabilidad/IMPLEMENTACION_30.md`.

### Contabilidad · Implementación 31 · Outbox de solicitudes fiscales

Persistencia interna con rollback y concurrencia PostgreSQL probados. Pendientes productor comercial autorizado con origen bloqueado, misma transacción/base, consumidor con recibo deduplicado y acuses fiscales reales en ambos sistemas. Actor activo no equivale a autorización empresarial. Revisar publicación, roles SQL y rendimiento del bloqueo por empresa; no exponer snapshots arbitrarios de usuarios. Véase `ANALISIS/contabilidad/IMPLEMENTACION_31.md`.

### Contabilidad · Implementación 32 · Fuentes de reserva y exactitud

Corregido contrato fiscal para sumar centavos enteros sin depender de la precisión decimal global. Auditar requests anteriores si se acredita contexto alterado; sin reescritura automática. Reservas inspeccionadas carecen de revisión fiscal/desglose autorizado; identificar flujo canónico y resolver fallback SIM-123/creación ausente antes de usarlas como productor. No inferir impuestos desde un total. Véase `ANALISIS/contabilidad/IMPLEMENTACION_32.md`.

### Contabilidad · Implementación 33 · Confirmación de reserva autorizada

Confirmación del modelo domain_business exige titular/vínculo y contexto explícitos; agente legado sin contexto ahora falla de forma cerrada. Propagar identidad desde sesión/misión autorizada antes de habilitarlo, sin IDs confiados al modelo. Pendientes carreras PostgreSQL, auditoría de transición, creación real y disponibilidad, modelo turístico alternativo y desglose/revisión fiscal canónicos. SIM-123 eliminado; creación declara no integrada. Véase `ANALISIS/contabilidad/IMPLEMENTACION_33.md`.

### Contabilidad · Implementación 34 · Concurrencia de reservas

PostgreSQL confirma una transición y un replay ante dos solicitudes simultáneas; revocación confirmada tras lectura inicial bloquea la transición en la segunda validación. Pendientes otros órdenes/intercalados, transferencia/desactivación/cancelación concurrentes, auditoría persistente de estado, origen fiscal y agentes con contexto autenticado. No revierte operaciones consumadas antes de revocar. Véase `ANALISIS/contabilidad/IMPLEMENTACION_34.md`.

### Contabilidad · Implementación 35 · Evento operacional de reserva

Confirmación y evento outbox se guardan/revierten juntos; concurrencia comprobó un solo evento. Legados confirmados sin evento se señalan sin reconstruir historial. Pendientes consumidor deduplicado, publicación/retención, auditoría inmutable, evidencia de legados y revisión fiscal del origen. `fiscal_ready=false`; no habilitar emisión o asiento automático con este evento. Véase `ANALISIS/contabilidad/IMPLEMENTACION_35.md`.

### Contabilidad · Implementación 36 · Observabilidad de cola comercial

Consulta owner-scoped de cantidades por tipo/estado, sin payloads ni aceptación fiscal. Pendientes panel web, consulta PostgreSQL bajo volumen/índices, consumidor idempotente con recibos y acuses reales. PROCESSED no equivale a aceptación DIAN y cola vacía no acredita ciclo completo. Véase `ANALISIS/contabilidad/IMPLEMENTACION_36.md`.

### Contabilidad · Implementación 37 · Panel comercial

Panel ERP conectado y probado con sesión/API aisladas; mantiene pendiente fiscal explícito y limpia resultados por contexto. Pendientes build completo con dependencias, dispositivos reales, consumidor y acuses fiscales, y consola corporativa Analemática. No habilita publicación ni emisión. Véase `ANALISIS/contabilidad/IMPLEMENTACION_37.md`.

### Contabilidad · Implementación 38 · Consulta acotada

API de dos intenciones con vocabulario determinista probada en ORM aislado y alcance titular. Pendientes UI/sesión real, lenguaje abierto/modelo privado evaluado, voz, más roles/fuentes, controles adversariales y límites de ingreso/concurrencia. No genera SQL ni autoriza acciones financieras. Analemática corporativa aún pendiente. Véase `ANALISIS/contabilidad/IMPLEMENTACION_38.md`.

### Contabilidad · Implementación 39 · Interfaz de preguntas

UI ERP conectada a dos herramientas de lectura, probada con sesión/API aisladas, fuente y moneda visibles. Pendientes respuestas tardías/revocación/red del panel, dispositivos reales, build completo, más preguntas/roles y comprensión abierta o voz evaluadas. No es chat general ni autorización de pagos. Consola corporativa Analemática pendiente. Véase `ANALISIS/contabilidad/IMPLEMENTACION_39.md`.

### Contabilidad · Implementación 40 · Contextos y respuestas tardías

Corregidos resultados/errores retenidos y botón ocupado al volver al contexto. Transporte retrasado que ignora cancelaciones probado en Chromium. Pendientes revocación real de sesión, cachés, varias pestañas y dispositivos; descartar respuesta no cancela una operación ya ejecutada en servidor. Véase `ANALISIS/contabilidad/IMPLEMENTACION_40.md`.

### Contabilidad · Implementación 41 · Privacidad HTTP

No-store/private y Vary Cookie/Authorization probados en respuestas contables y errores controlados. Pendientes proxy/CDN/TLS, bfcache/service workers, errores no manejados, revocación real y múltiples pestañas. No borra copias previas ni garantiza conducta de cachés externas. Integración corporativa Analemática pendiente. Véase `ANALISIS/contabilidad/IMPLEMENTACION_41.md`.

### Contabilidad · Implementación 42 · Parser de consultas

Ruta consulta-contable limita lectura a 8 KiB y profundidad a ocho niveles; duplicados/constantes inválidas probados en router real. Pendientes límites previos de proxy/servidor/middleware, concurrencia/rate limiting y coste de reportes bajo carga. El límite del parser no acredita contención de memoria de toda la infraestructura. Véase `ANALISIS/contabilidad/IMPLEMENTACION_42.md`.

### Contabilidad · Implementación 43 · Agregación de rentabilidad

GROUP BY limitado a ingresos/costos/gastos, tras controles generales; fixture comparó siete grupos con uno y resultados iguales. Pendientes EXPLAIN/índices/carga real PostgreSQL, tiempos/memoria y concurrencia. No acredita 250 ms ni un porcentaje de mejora de latencia. Véase `ANALISIS/contabilidad/IMPLEMENTACION_43.md`.

### Contabilidad · Implementación 44 · Flujo de reserva a solicitud

Funciona en ERP: fuente confirmada/titular verificado, desglose exacto revisado, evidencia persistida y segunda confirmación para un request idempotente vinculado a la revisión. UI/API/PG y móvil probados con datos aislados. Pendientes consumidor/emisión/acuse DIAN, normativa/tasas, moneda de fuentes legadas, ajustes/notas, reconocimiento contable, historial/reanudación visual, auditoría independiente e índices/carga. El núcleo compartido está integrado; consola corporativa Analemática aún requiere recorrido propio. Sin aceptación fiscal o ledger automático. Véase `ANALISIS/contabilidad/IMPLEMENTACION_44.md`.

### Contabilidad · Implementación 45 · Asiento de reserva y contrapartida

Flujo ERP genera asiento real y contrapartida con dos confirmaciones por operación; periodo/actor/cuentas, evidencias, idempotencia y rollback verificados en SQLite/PG y navegador. Bloquea anticipos no conciliados, moneda distinta de COP y servicio futuro. Pendientes política normativa/validación profesional, anticipos y compensaciones, fuentes COMPLETED/alternativas, FX/retenciones, historial/reanudación, búsqueda paginada UI y cuentas >500, protección de reviews frente a operadores privilegiados, carga/roles/despliegue reales y consola corporativa Analemática. Prestación y evidencia declaradas no son verificación independiente. Sin emisión DIAN o pagos. Véase `ANALISIS/contabilidad/IMPLEMENTACION_45.md`.

### Contabilidad · Implementación 46 · Lectura corporativa compartida

Analemática consulta balance/rentabilidad reales del ERP con dueño corporativo, cookie ERP y vínculo revisado. UI y ambos backends probados con datos aislados; revocar sesión/rol/vínculo bloquea acceso. Pendientes esquema/vínculo legítimos productivos, renovación/historial, privilegios y PostgreSQL, CA/TLS/origen/gateway/cookies, carga y escritura corporativa con aprobaciones. No es SSO ni aceptación DIAN. El web no hace DDL; herramienta opcional de operador en tools/review_corporate_ledger.py, dry-run por defecto. Asset público incluido en staging; no se desplegó. Véase `ANALISIS/contabilidad/IMPLEMENTACION_46.md` y `OPERACION_PUENTE_CORPORATIVO.md`.

### Contabilidad · Implementación 47 · Aplicación de anticipos

Flujo local ERP de aplicación revisada de un recibo simple completo en COP, dos confirmaciones, cartera neta y prueba determinista de aplicación. Pendientes conciliación bancaria y correspondencia cliente/recibo independientes; bloqueo transversal de contrapartidas posteriores del recibo aplicado; recibos múltiples, división, devoluciones, FX, custodia de evidencia, protección de eventos ante operador privilegiado y validación profesional/productiva. No es dinero transferido ni validación DIAN. Véase `ANALISIS/contabilidad/IMPLEMENTACION_47.md`.

### Contabilidad · Implementación 48 · Corporativo, tributario y DIAN

Escritura corporativa local integrada al ledger con dos confirmaciones y contrapartida; ambos backends y navegador real verificados con fixtures. Falta provisión de vínculos/sesiones reales, homologación con custodia/roles y operación productivos. No hay atomicidad distribuida SQLAlchemy–Django; timeout tras despacho exige consulta/reintento de la misma revisión. Revocación posterior al despacho no deshace un asiento autorizado.

Se resuelve en el servicio compartido el bloqueo transversal pendiente en el corte 47: no se puede revertir un recibo con aplicación vigente antes de contrapartida del reconocimiento. Siguen pendientes conciliación bancaria independiente y protección frente a operador privilegiado/SQL fuera del servicio, múltiples anticipos y reembolsos.

Conciliación tributaria local usa movimientos/cuentas reales y evidencia de fuente, conserva no atribuidos. Falta política normativa/versiones, retenciones/IVA descontable, contraste oficial y aceptación profesional. DIAN ya no devuelve éxito/firma/CUFE simulados. Los históricos aceptados de esas rutas requieren revisión contra acuses auténticos. Firma XAdES/UBL, custodia cliente, proveedor/transportes, credenciales/habilitación y verificación auténtica de acuses continúan bloqueados. Véase `ANALISIS/contabilidad/DIAN_HABILITACION.md` y `IMPLEMENTACION_48.md`.

### Contabilidad · Implementación 49 · Plan de 20 hitos y facturas legadas

H01 restringe el API legado a dueño/empresa vinculada y verifica las dos partes factura/operación; el listado/detalle ya no serializa XML ni URL de documentos. Los estados históricos se conservan con aceptación no verificada. Pendientes inventario/migración soberana del texto claro ya persistido, reconciliación de tenant_id legados y homologación de los consumidores del serializador. La corrección local no modifica datos ni acredita saneamiento de almacenamiento. Plan completo y requisitos externos en `ANALISIS/contabilidad/PLAN_SUBSANACION_20_HITOS.md`.

### Contabilidad · Implementación 50 · Ejecución local y dependencias reales

H02–H04 verificados localmente: recuperación tras respuesta perdida, catálogos paginados e historial, cortes coherentes en primary con referencia al ledger. El snapshot es del estado actual bajo bloqueo, no una publicación histórica. La paginación requiere recarga para incluir inserciones anteriores al cursor; la búsqueda devuelve una página acotada por consulta.

H14 dispone de comparación CSV/ledger de lectura, sin persistencia de archivo/IDs bancarios originales ni asientos. Pendientes importación persistente/idempotente y revisión/confirmación, autenticación bancaria, datos legítimos, FX y cualificación de privacidad/custodia. H17 ya consulta desde Analemática mediante herramientas deterministas ERP; faltan modelo/dataset evaluado, voz y cobertura ampliada. H20 conserva benchmark y operación real pendientes. Los20 paquetes no están cerrados:4 verificados locales,3 en ejecución y13 pendientes. Véase `ANALISIS/contabilidad/IMPLEMENTACION_50.md` y el plan canónico.

Hallazgo adicional para H12: indicador SST con denominador fijo de10 trabajadores y ausencia de guardas de despacho/fatiga acreditadas; revisar también el alcance del acceso médico antes de uso productivo. No se modificaron registros médicos ni se declaró aptitud de personal.

### Contabilidad · Implementación51 · Apertura y política tributaria

H05 incorpora apertura COP revisada o vinculación de un asiento existente exactamente coincidente, sin borrar saldos ni duplicar libros. Pendientes conciliación de legados discrepantes, lotes mayores de100 cuentas, valoración/fuente FX, documentos auténticos y validación profesional. Los eventos de revisión no son una firma independiente ni protección ante operador privilegiado.

H06 incorpora versiones inmutables de política declarada con vigencias no solapadas y cálculo exacto por componente. No contabiliza todavía retenciones ni emite factura/nota crédito. Pendientes conexión al flujo fiscal y reconocimiento, revisión normativa, IVA descontable, rectificaciones de vigencia, historial ampliado del panel y acuses oficiales. No se habilitan tasas legales por defecto ni transmisión DIAN.

Plan conservado:4 paquetes verificados localmente, 5 en ejecución,11 pendientes. Avance global44,44 % sin créditos duplicados; véase ANALISIS/contabilidad/IMPLEMENTACION_51.md.

### Contabilidad · Implementación52 · SST y nómina

H12: acceso médico requiere permiso explícito por acción y empresa propia/vínculo vigente; superusuario no concede acceso. Actividades/planes y parentescos se acotan. No se otorgan permisos clínicos automáticamente; faltan aprovisionamiento profesional, consentimiento, retención/cifrado de históricos y pruebas de roles reales. Observación mensual usa dotación activa actual y no certifica accidentalidad histórica ni aptitud. Suspensión interna es atómica con auditoría, pero falta impedir despacho/reanudación por cualquier ruta sin aptitud/EPP/fatiga válidos.

H13: se retiraron liquidación con constantes2024/2025 y éxito CONTABILIZADA sin posteo real. Acciones devuelven503 sin modificar datos; antes verifican pertenencia de la planilla. Borradores propios siguen disponibles; estado/referencias financieras no se reciben del cliente y no se edita/borra historia con efectos. Pendientes motor laboral vigente, revisión/doble aprobación, puente canónico al ledger, provisiones/costos, documentos oficiales y conciliación de estados históricos; otras rutas laborales todavía requieren auditoría. No se ha pagado ni liquidado nómina y no se acredita ACC-013.

Avance global47,22 % por primer incremento SST verificado;4 de20 paquetes verificados localmente,7 en ejecución y9 pendientes. No hay aceptación productiva.

### Contabilidad · Implementación 53 · Nómina base revisada

Nuevo flujo desde ambos paneles y APIs: revisión persistida de contrato/días/parámetros/cuentas, segunda autorización y posteo canónico con cabecera y proyección atómicas. Reintento recupera el mismo asiento. Política versionada declarada no equivale a normativa laboral aprobada; no se paga ni se genera documento oficial. Las rutas antiguas sin revisión permanecen en503.

Pendientes: reglas laborales vigentes y evidencia legítima de jornada, novedades/ausencias/incapacidades/horas/recargos/contratos especiales, prestaciones reglamentarias detalladas, dimensiones contables de centro/paquete y pipeline de operación–SST–nómina completo. El centro del empleado se conserva como fuente; el asiento agregado no ofrece desglose dimensional. La proyección de detalle es de base y totales: los campos legales restantes en cero no acreditan liquidación de esas obligaciones.

Catálogos acotados20/100/200 con aviso de truncamiento y cálculo1–10 empleados/1–8 componentes requieren ampliar paginación/volumen antes de operación general. Homologar el serializador/históricos legados, reversión y reapertura laboral, migraciones nativas y roles/autorizaciones reales. Revisar auxiliares/indicadores laborales existentes y comportamiento de descifrado legado ante datos corruptos; este flujo no certifica todo el módulo. Custodia independiente de eventos y prueba de soporte/jornada continúan pendientes.

El incremento verificado de ACC-013 eleva el índice estable a50,00 % (36/72), no a aceptación productiva. H13 permanece en ejecución y los20 paquetes no están cerrados. Véase ANALISIS/contabilidad/IMPLEMENTACION_53.md.

### Contabilidad · Implementación 54 · Conciliación revisada

Nuevo flujo de correspondencias COP y liberación append-only, con dos confirmaciones del mismo titular, revisión persistida, reservas por línea/referencia y recuperación idempotente. No cambia el ledger ni genera cobros/pagos. Un movimiento con contrapartida posterior queda pendiente de revisión; liberar no borra evidencia y permite una asociación posterior revisada.

La autenticidad/titularidad bancaria no se verifican: bank_verified=false. Se guardan fechas/importes/digests y vínculos derivados, no el CSV o IDs originales en los registros de este servicio; SHA256 no es anonimización. No se ha cualificado ausencia forense en logs, cachés, respaldos o telemetría de producción. Faltan extractos legítimos, instrumento bancario, saldos inicial/final, soporte BYOS, conectores mínimos, formatos reales, FX/fecha valor/cargos/devoluciones, lotes parciales, ambiguos y fuente independiente.

Exclusividad validada bajo bloqueo del servicio, sin constraint SQL independiente para reservas activas por línea; calificar roles/escritores externos, protección/custodia de eventos, restauración y rendimiento. Límites actuales:30 filas únicas por confirmación,1000 reservas históricas relevantes por revisión y200 cuentas de catálogo con aviso de truncamiento. Ampliar historial/búsqueda de cuentas retiradas y liberación parcial antes de uso general. La confirmación declarada no habilita pagos ni el uso de una evidencia como si fuera verificación bancaria independiente.

H14 sigue en ejecución; índice global50,00 % sin créditos duplicados. Véase ANALISIS/contabilidad/IMPLEMENTACION_54.md.

### Implementación 55 · Cualificación hotelera H15

- Validar series legítimas de disponibilidad diaria, criterios de habitación/noche y clasificación de cuentas con responsables hoteleros y contables. La selección del propietario no equivale a evidencia independiente de ocupación.
- Completar ocupación, ADR, dimensiones por establecimiento y costos por paquete; integrar el modelo alternativo legado solo tras revisar dependencias y migraciones.
- Calificar reconstrucción por fechas de conocimiento, reloj, retención y pruebas independientes; los timestamps de aplicación y hashes outbox no certifican publicación original ni almacenamiento WORM.
- Medir rendimiento y ampliar límites de inventario/ventanas de forma controlada; revisar COP/FX, permisos SQL, respaldo y restauración de versiones. No extrapolar pruebas sintéticas a aceptación de producción.
- Evidencias y límites: `ANALISIS/contabilidad/IMPLEMENTACION_55.md` y `evidencias/implementacion-55.json`. H15 sigue en ejecución; avance global36/72, sin nuevo crédito.

### Implementación 56 · Medición ambiental H16

- Cualificar factores legítimos por territorio, tecnología, gases, vigencia y frontera con revisión profesional; las huellas declaradas no verifican fuentes ni exactitud científica.
- Implementar persistencia versionada/revisada y custodia soberana de soportes, integración operativa real y prevención de doble conteo entre solicitudes. La estimación actual es de lectura y no conserva historial.
- Completar incertidumbre, compensaciones efectivamente retiradas y mapeo GRI/SASB aplicable; sin emitir créditos ni certificar ESG desde estimaciones.
- Solo reconocer obligación contable con fundamento, política, valoración, cuentas y aprobaciones propios. Probar datos legítimos y límites en infraestructura objetivo.
- Evidencias y alcance: `ANALISIS/contabilidad/IMPLEMENTACION_56.md`. H16 sigue abierto; aceptación completa ACC-018 no acreditada.

### Implementación 57 · Historial ambiental revisado

- Cualificar fuentes/soportes legítimos, custodia soberana y validez científica; los hashes declarados no autentican factores o actividades.
- Integrar identificadores de viajes/consumos reales y detectar duplicidad semántica: el servicio actual impide repetir códigos, no reconocer el mismo viaje bajo otro código.
- Completar corrección/contrapartida ambiental con dos revisiones, sin borrar originales; búsqueda/paginación/exportación y cortes históricos. Actualmente se recupera por UUID conocido y no se liberan actividades confirmadas.
- Verificar roles SQL, retención, restauración conjunta de revisión/factores/reservas/confirmación y límites en infraestructura objetivo. Las PK deterministas y los locks del servicio no son un esquema WORM ni validación contra escrituras privilegiadas.
- Alcance y evidencias en `ANALISIS/contabilidad/IMPLEMENTACION_57.md`; no acredita obligaciones monetarias, compensaciones, ESG ni producción. ACC-018 sigue sin aceptación completa.

### Implementación 58 · Borradores cifrados offline H19

- Cualificar KDF y contraseñas, latencia, cuota/evicción y persistencia/restauración del navegador; proveer catálogo/backup/exportación y política de retención/borrado. Conservar UUID y contraseña: no hay recuperación por servidor.
- Completar arranque/caché offline y sincronización de más dominios. El alcance actual es un borrador ambiental individual en un panel previamente cargado y verificado; no sincroniza ni confirma automáticamente.
- Validar Android/iOS/escritorio reales, SQLite cifrado y custodia hardware. WebCrypto/IndexedDB no son Secure Enclave ni Keystore; los strings de JavaScript no tienen borrado forense garantizado.
- Revisar CSP, dependencias y riesgo del mismo origen; mantener controles de identidad y revocación al reconectar. No se guardan autorizaciones en la cola.
- La rotación activa local no revoca copias viejas ni recupera KEK fiscales. H11 sigue separado. Evidencia y límites: `ANALISIS/contabilidad/IMPLEMENTACION_58.md`; ACC-022 sin aceptación completa.

### Implementación 59 · Respaldo local cifrado

La exportación/restauración manual de borradores cifrados de H19 queda implementada y probada en ambos paneles con pérdida sintética del almacén. Esto amplía el punto de backup de la entrega58, pero no cualifica medios físicos, custodia/retención, SQLite nativo ni recuperación de contraseña/KEK fiscales. Siguen pendientes catálogo de borradores, borrado por retención y pruebas físicas; las copias anteriores a una rotación mantienen su contraseña anterior. No se sobrescribe una copia activa diferente. Ver `ANALISIS/contabilidad/IMPLEMENTACION_59.md`.

### Implementación 60 · Borrador UBL H07

- Cualificar anexo y reglas DIAN actuales, identidad/NIT/DV, resolución/rango, software, campos por tipo y tributos con responsables profesionales. El XSD de referencia conserva header UBL2.1 CS1 de2013; no se afirma conformidad DIAN.
- Integrar CRM/reserva y política tributaria con solicitud/documento, representación requerida/PDF-A3 y custodia soberana cifrada. La vista actual es solo un borrador en memoria, sin persistencia ni emisión.
- Completar firma XAdES/certificado/custodia/validación de cadena, transporte habilitado y acuses auténticos. Los esquemas de firma vendorizados son dependencias de tipos, no código firmante.
- Ampliar notas/cargos/descuentos/retenciones/anticipos/FX/cantidades fraccionarias y pruebas físicas/aceptación profesional. Ver `ANALISIS/contabilidad/IMPLEMENTACION_60.md`; ACC-009 sin aceptación completa.

### Implementación61 · Recuperación/rotación local de documentos H11

- Cualificar custodia hardware/HSM/KMS/medios cliente, política de recuperación/escrow y entropía/KDF en equipos reales. El modo portátil usa contraseña local, no atestación de hardware ni recuperación por servidor.
- Integrar publicación/backup/referencias versionadas en destinos soberanos y permisos mínimos (H10); resolver ramas concurrentes y determinación de última versión. El parent digest/HMAC no es WORM ni auditoría independiente.
- Rotar la KEK no revoca archivos/contraseñas viejas o DEK comprometidas. Completar respuesta a incidentes y re-cifrado cuando corresponda, sin borrar evidencia legítima.
- Cualificar representación fiscal/visores, formatos binarios, retención y restauración física; la vista actual recupera texto UTF-8 de documentos sintéticos y no acredita firma ni aceptación DIAN.
- Ver `ANALISIS/contabilidad/IMPLEMENTACION_61.md`; aceptación completa pendiente y sin créditos globales duplicados.

### Implementación62 · API y versiones BYOS del cliente H10

- Aprobar propiedad/destino, perfiles por empresa, dominios/TLS, conexión DB segura, archivos privados y permisos/grants reales; probar ambos paneles provisionados. No existe destino real por defecto.
- La ruta de prueba usa PostgreSQL separado, rol mínimo y HTTPS loopback, con certificado efímero no cualificado. No reutilizar excepciones de confianza de los fixtures en producción.
- Calificar cuotas, límites/timeouts, revocación durante solicitudes, commit/respuesta incierta, administración de grants, respaldo/retención/RPO/RTO y recuperación física. La API admite solo versiones append; no ofrece poda/listado general.
- Los receipts no verifican HMAC/GCM ni propiedad legal del destino. Cliente autentica el paquete; TLS, rol y operación requieren revisión independiente. SQL privilegiado/escritores fuera del servicio no quedan acreditados como WORM.
- Token BYOS temporal distinto del JWT del ERP y de la contraseña del documento; no ponerlos en perfiles públicos o Git. Ver `ANALISIS/contabilidad/OPERACION_BYOS_PAQUETES.md` y `IMPLEMENTACION_62.md`.

### Implementación63 · Firmante XAdES local de laboratorio H08

- Cualificar certificado legítimo, identidad, política/anexo DIAN, PKIX/revocación/OCSP/CRL y sello de tiempo. El perfil actual rechaza producción y certificados ajenos al laboratorio.
- Validar HSM/custodia hardware, protección de memoria, medios y recuperación físicos. PKCS8 cifrado y procesamiento temporal en Python no acreditan aislamiento de hardware ni borrado forense.
- Integrar revisión/autorizaciones de negocio resistentes a suplantación antes de cualquier automatización remota. Las dos confirmaciones de la CLI no subsanan H18 ni autorizan pagos o emisión fiscal.
- Probar recorrido con ambos sistemas, cliente/destino legítimos, firma cualificada y acuses auténticos. La firma sintética verificable y su interoperabilidad con el SDK no son aceptación fiscal ni productiva.
- Ver `ANALISIS/contabilidad/IMPLEMENTACION_63.md` y `OPERACION_FIRMANTE_LOCAL.md`; no se ejecutaron envíos ni se cambió main.

### Implementación64 · Ensayo financiero con revisiones persistentes H18

- Cualificar beneficiario/cuenta/soporte y proveedor bancario legítimos; el UUID y digest aportados por el titular no verifican identidad ni autenticidad.
- Integrar interfaz y broker limitado de agent-desktop/Open Duet solo tras revisión de permisos, presencia/autorización y protección contra sesión comprometida. No se crearon trabajos de escritorio ni un ejecutor de dinero.
- Probar concurrencia específica en PostgreSQL, caída/commit-respuesta incierta, retención/auditoría, permisos SQL, plazos y recuperación en infraestructura real. Las pruebas ORM usan SQLite desechable y el puente usa HTTP local autenticado.
- SIMULATED_ONLY y sus comprobantes no son autorizaciones bancarias, recibos externos ni asientos. Mantener bloqueada cualquier dispersión real y no restaurar aprobaciones desde copias offline.
- Ver `ANALISIS/contabilidad/OPERACION_SIMULACION_FINANCIERA.md` e `IMPLEMENTACION_64.md`. Ninguna modificación de main o publicación Git en esta entrega.

### Implementación65 · Corrección ambiental con historia H16

- Completar formularios de corrección, búsqueda/cortes/exportación, incertidumbre y vínculo con operaciones/soportes reales. Las rutas están integradas y ambos paneles recuperan la revisión vigente; no hay un formulario nuevo de corrección.
- Cualificar factores/fuentes, duplicados semánticos y reconocimiento ambiental profesional. Corregir una estimación no genera crédito de carbono, certificación ESG, obligación, pago ni asiento.
- Probar la carrera específica en PostgreSQL y controles SQL/retención/backup externo. La cadena de hashes interna no detecta por sí sola el borrado privilegiado completo del tramo final ni impide una reescritura coherente.
- Preservar actividades originales y versiones de factores, límites de historia y revisiones concurrentes; no sumar original y corrección ni restaurar autorizaciones desde estado recuperado.
- Ver `ANALISIS/contabilidad/IMPLEMENTACION_65.md` y `OPERACION_CORRECCIONES_AMBIENTALES.md`. H16 permanece en ejecución.

### Implementación66 · Acuses y diario local de laboratorio H09

- Integrar cliente SOAP/WS-Security, endpoints aprobados y controles de transporte reales. El diario local no envía ni acredita una transmisión/timeout; no reservar numeración nueva por un reintento incierto.
- Cualificar el anexo/códigos oficiales ApplicationResponse, certificados/política de confianza, revocación/PKIX y sello de tiempo aplicables, identidad/resolución y acuses auténticos de habilitación. Los códigos LAB_* no son estados DIAN.
- Vincular hashes a bytes originales y solicitudes comerciales/numeración verificadas, cualificar recuperación operacional y concurrencia del flujo completo. El diario solo fija hashes declarados y metadatos locales.
- El SQLite local usa permisos privados y guardas, no cifrado integral, WORM ni protección contra reescritura privilegiada coherente. Resolver retención/backup/recuperación/privilegios de host con el cliente.
- Completar prueba física positiva de CLI/paquete y custodia; no convertir un resumen cliente en aceptación fiscal de servidor. La frontera de envío continúa bloqueada.
- Ver `ANALISIS/contabilidad/IMPLEMENTACION_66.md`, `OPERACION_ACUSES_LABORATORIO.md` y `CIERRE_20_HITOS.md` para faltantes locales y externos de cada paquete.

### Implementación67 · Guardas de estado/aislamiento del despacho genérico H12

- Implementar el recorrido positivo con aptitud profesional, EPP y jornada/descanso verificables. La activación genérica ahora se rechaza porque ese contrato no está cualificado; no presentar este bloqueo como autorización operativa completa.
- Revisar módulos especializados, tareas, recursos y ejecutores; las guardas cubren órdenes/procesos genéricos, vistas modificadas y manager normal. SQL directo, managers alternativos/código privilegiado y operaciones físicas no quedan contenidos por ellas.
- Añadir controles SQL/roles y carreras PostgreSQL específicas, pruebas de revocación/recuperación e integración HTTP desplegada. La suite nueva usa ORM y APIRequestFactory aislados, sin interfaz nueva ni validación física.
- Adaptar misiones legadas al contexto autenticado: proveedor, titular, estado esperado y confirmación. No introducir IDs de usuario como sustituto de autorización real. No restaurar el éxito ficticio de ejecución de tareas.
- Auditar atribuciones históricas de RegistroOperativo; no reescribirlas asignándoles actores inventados. La historia nueva usa AuditLog con actor real; cualificar retención/privilegios y paginación histórica completa.
- Ver `ANALISIS/contabilidad/IMPLEMENTACION_67.md` y `OPERACION_GUARDAS_DESPACHO.md`. H12 permanece EN_EJECUCION; sin pago, despacho cualificado ni cambio de main.

### Implementación68 · Plan restante y enlace política/reserva/ledger

- Cualificar tasas/categorías/fechas/soportes con profesional autorizado. La verificación del vínculo persistido no es verificación normativa ni aceptación DIAN.
- Completar R03: retenciones, IVA descontable y posteo por componente/cuentas. El flujo nuevo rechaza retención positiva y múltiples códigos positivos en lugar de agruparlos silenciosamente.
- Resolver fechas tributaria/contable diferentes mediante un tratamiento explícito; el alcance nuevo exige igualdad y no pretende definir la norma.
- Incorporar interfaz y recuperación/presentación del vínculo en ambos paneles (R18), resolver respuesta incierta sin nuevas aprobaciones y revisar legados que usasen el prefijo reservado SGATP/.
- Cualificar SQL/roles/inmutabilidad específica del vínculo, concurrencia PostgreSQL, identidad y operación/recuperación. Los hashes no son WORM ni una prueba independiente de legalidad.
- Seguir `ANALISIS/contabilidad/PLAN_REMANENTE_20_HITOS.json`; no se cambió la base de72 hitos ni se cierran aceptaciones externas con pruebas sintéticas. Ver implementación68 y operación de reservas/política.

## Implementación69 · Datos laborales y despacho condicionado

- Capturar datos legítimos de cada trabajador: autorización profesional, soporte de EPP y jornadas/descansos; comprobar habilitación/identidad del revisor y política laboral/SG-SST aplicable. No hay semillas de datos, valores legales por defecto ni verificación física automática.
- Provisionar política privada del servidor y permisos clínicos explícitos; validar custodia/rotación de la clave de cifrado, consentimiento y retención de estos datos. El resumen operativo no expone la decisión médica.
- Ensayar migración histórica y reversión operativa sin borrar evidencia; ejecutar los nuevos triggers y concurrencia en PostgreSQL. Solo se migró una base SQLite nueva con seis tablas vacías.
- Completar formularios de captura y recorridos en ambos paneles, procesos especializados y cobertura de trabajo fuera de plataforma. El fin genérico llega a VALIDACION y registra jornada; aún no integra automáticamente nómina/costos.
- No declarar servicio físicamente seguro, licencia validada, aceptación profesional o producción por haber superado las37 pruebas locales. Ver ANALISIS/contabilidad/IMPLEMENTACION_69.md.

## Implementación70 · Hechos comerciales y tributarios revisados

- Integrar fuentes nativas de compras/ventas y validar documentos/terceros; los UUID y hashes declarados no acreditan autenticidad ni responsabilidades fiscales. Resolver deduplicación semántica entre rutas y soportes sin cambiar la historia.
- Completar conciliación unificada de IVA generado/descontable y retenciones, devoluciones parciales y formularios de captura/recuperación. El conciliador anterior solo atribuye reservas.
- Revisar profesionalmente tasas, vigencias, categorías, cuentas y deducibilidad; probar concurrencia PostgreSQL y guardas SQL de los nuevos tipos de evidencia. Mantener separados posteo, documento fiscal y pago.
- Los recorridos locales nuevos no acreditan DIAN, transmisión, identidad de terceros ni producción. Ver ANALISIS/contabilidad/OPERACION_HECHOS_TRIBUTARIOS.md.

## Implementación71 · Registro integral y rendimiento

- Conciliación de movimientos por cuenta disponible en ERP/Analemática con validación de fuentes y sumas; no equivale a declaración, saldo tributario final ni cruce oficial. Completar fuentes nativas, devoluciones parciales y aceptación profesional.
- Benchmark100 documentos secuenciales en SQLite en memoria: máximo de conciliación547.209ms antes y134.922ms después. Medir HTTP, PostgreSQL, carga prolongada/concurrente, hardware objetivo y límites mayores; no presentar este ensayo como SLA250ms.
- No se ejecutó clasificador IA: precisión99.8% no evaluada. Obtener dataset etiquetado autorizado, modelo/versión, política de abstención y revisión independiente antes de calificarla.
- Las nuevas comprobaciones de navegador conservan azul/blanco y móvil en estos recorridos, sin completar todas las interfaces o cualificación física/productiva. Ver ANALISIS/contabilidad/IMPLEMENTACION_71.md.

## Implementación72 · Compras nativas

- Recorrido nuevo operable en ambos paneles: captura, revisión y posteo/contrapartida con dos confirmaciones; no habilita las rutas heredadas ni pagos. Ver ANALISIS/contabilidad/OPERACION_COMPRAS_NATIVAS.md.
- Conciliar facturas históricas sin captura; implementar enmiendas de metadatos capturados, devoluciones parciales, todas las responsabilidades fiscales y formularios multicomponente. La interfaz actual cubre un concepto.
- Verificar documentos, proveedores, recepción y deducibilidad con fuentes/profesionales legítimos. Hash y vínculo nativo no son autenticidad ni aceptación DIAN.
- Cualificar PostgreSQL/concurrencia y guardas SQL de reservas/pruebas, roles de operación, custodia de documentos y migración histórica antes de producción. Nuevos IDs enteros limitados al rango seguro de JavaScript.
- Medición sintética100 documentos sobre fuentes72, sin errores y sin HTTP/dispositivos/carga concurrente: no acredita SLA250ms ni precisión IA. No se realizaron acciones reales, pagos ni publicación.

## Entrega73: nómina y costos operativos

- Conectar las cinco acciones nuevas al puente de Analemática y a los dos paneles, con dos confirmaciones sin restauración automática.
- Validar capacidades pagadas, centros y evidencia laboral con responsables legítimos; las declaraciones actuales no acreditan aptitud ni ejecución física.
- Completar reglas revisadas de recargos, deducciones y viáticos y habilitación de nómina electrónica antes de usar el flujo como liquidación integral.
- Cualificar bloqueos concurrentes, guardas y consultas JSON sobre PostgreSQL; probar volumen superior a los límites declarados antes de ampliarlos.
- La distribución es analítica: no recontabiliza, no dispersa dinero y no sustituye el costo total de una operación.

## Actualización74: conexión corporativa y paneles de costos

Subsanada localmente la conexión de los cinco comandos al puente de Analemática y el formulario compartido de distribución en ambos paneles, con dos confirmaciones. Permanecen reglas laborales/documento electrónico, pruebas PostgreSQL de concurrencia/volumen y revisión profesional. Falta formulario dedicado del informe de costos por operación; la API ya está conectada. Evidencia: ANALISIS/contabilidad/IMPLEMENTACION_74.md.

## Actualización75: suplementos y duplicidad de salario base

Subsanado localmente cálculo/posteo/proyección/costos de horas extra y recargos declarados y bloqueo de segunda planilla superpuesta que volvería a causar salario base. No acredita tarifas legales ni clasificación automática. Pendientes: enlace de minutos a jornadas concretas; calendario/horarios/reglas laborales revisados y vigentes; otras novedades, ausencias, incapacidades, viáticos y deducciones; nómina electrónica; ajuste de nómina por ruta independiente y cualificación PostgreSQL de concurrencia/volumen. Detalle: ANALISIS/contabilidad/IMPLEMENTACION_75.md.

## Actualización76: conciliación parcial de filas

Subsanada localmente la selección de candidatos ambiguos y la persistencia de diferencias con motivos, reservas por referencia, recuperación/liberación y calificación parcial en ambos paneles. Pendientes: saldos completos por período, pagos parciales/agrupaciones, FX, archivos grandes, fuente bancaria auténtica y revisión profesional. Cualificar lector/colas/informesv2 y reversión antes de desplegar; lectoresv1 no interpretan los registros nuevos. Las diferencias no generan asientos ni pagos. Evidencia: ANALISIS/contabilidad/IMPLEMENTACION_76.md.

## Actualización77: saldos de período declarado

Subsanado localmente el cotejo de apertura/cierre y cobertura del libro COP, con dos autorizaciones, cambio retroactivo detectado y recuperación/liberación en ambos paneles. No acredita autenticidad de banco ni integridad del archivo externo por la mera declaración del propietario. Pendientes: fuente legítima/independiente y revisión profesional, períodos sin movimientos, snapshots y volúmenes mayores, pagos divididos/agrupados, FX y cualificación PostgreSQL/concurrencia. Límites:30 filas importadas,200 movimientos del período,2000 líneas históricas de caja. Evidencia: ANALISIS/contabilidad/IMPLEMENTACION_77.md.
