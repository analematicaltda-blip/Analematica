# Bloqueos para aceptación completa

## ACC-001 · Validación monetaria exacta y aislamiento de cuentas

3/3 hitos. Pendiente: Ninguno en los cinco criterios funcionales originales deACC-001; cierre evidenciado2026-11-11. No equivale a habilitación productiva, fiscal/bancaria o cierre de otras tareas.

## ACC-002 · UUID de alta y guardas de asientos/líneas

3/3 hitos. Pendiente: Ninguno en los criterios originales deACC-002, cerrados2026-11-11. ORM masivo requiere las guardas SQL del esquema migrado, verificadas enSQLite/PostgreSQL. SQL privilegiado, roles/RLS y despliegue global pertenecen aACC-007/024; no se acreditan aquí.

## ACC-003 · Idempotencia y outbox en una transacción

3/3 hitos. Pendiente: Ninguno en los criterios transaccionales locales originales deACC-003; cierre2026-11-11. No se acredita publicaciónKafka, acuse externo ni exactly-once de red; esos alcances no se deducen del outbox local.

## ACC-004 · Periodos, concurrencia y contrapartidas

2/3 hitos. Pendiente: Reversión neutra y diagnóstico de conciliación probados; faltan conciliación real de legados, aperturas/ajustes aprobados, snapshot e interfaz y fuentes FX/diferencias según alcance. Apertura ampliada2026-11-11: primer libro COP con2..250 cuentas preservadas, revisión paginada y un asiento atómico, probado en ambos paneles y PostgreSQL desechable. No acredita migración de libros existentes/descuadrados, lotes mayores, fuente auténtica ni aceptación profesional/productiva.

## ACC-005 · Puente TourismProvider a Tenant y actor verificables

2/3 hitos. Pendiente: Lectura/escritura y recuperación de resultado incierto probadas entre ambos backends y navegador; faltan provisión/renovación e historia del vínculo, roles/SSO/migraciones reales y aceptación productiva. Sin atomicidad distribuida.

## ACC-006 · Monedas, FX y valoración

2/3 hitos. Pendiente: Valoración inicial revisada, revaluación incremental y liquidación parcial/total USD/EUR-COP contra caja ya registrada operan en ambos paneles; incluyen contrapartida, resto exacto y concurrencia. Pendientes legados/lotes no cubiertos, cargos/comisiones/división/transitorios y otros consumos, snapshots históricos, legitimidad de fuentes/tasas y clasificación profesional, migración/roles/carga y aceptación productiva.

## ACC-007 · Hash canónico versionado y controles SQL

2/3 hitos. Pendiente: Flujo central con rol limitado y backup/restore local probados; faltan permisos/rutas completos, revisión de UPDATE(id), roles reales, RLS/funciones privilegiadas y llaves/medios/RPO/RTO según alcance.

## ACC-008 · Contrato CRM y reserva hacia facturación

2/3 hitos. Pendiente: Revisiones, solicitud, reconocimiento/anticipos/contrapartida y escritura corporativa locales implementados. Falta emisión/acuse DIAN auténticos, conciliación bancaria independiente, múltiples anticipos, política normativa y aceptación profesional/productiva. Implementación68 conecta política declarada versionada a reserva y reconocimiento, con evidencia revalidada; COP/1–5 componentes/un único código de impuesto positivo/fecha igual. Retenciones positivas y múltiples impuestos se rechazan; faltan normativa, interfaz/recuperación completas, SQL/concurrencia específica y aceptación real. Implementación72 conecta proveedores/facturas nativos con captura idempotente, fuente/huella reservadas, dos confirmaciones y contrapartida en ambos paneles. UI de un concepto; pendientes historia sin captura, cambios controlados, devoluciones parciales, fiscalidad completa y cualificación profesional/productiva. Recuperación2026-11-10: historial, correcciones previas a revisión/posteo y devoluciones proporcionales acumuladas con dos confirmaciones y asiento compensatorio local. Conserva fuentes originales; no emite nota fiscal ni ejecuta reembolso. Pendientes retorno por concepto, atribución tributaria de los nuevos ajustes en el registro unificado, normativa e interfaces completas.

## ACC-009 · XML, representación y firma fiscal

2/3 hitos. Pendiente: Borrador UBL COP y representación en memoria en ambos paneles, cuatro documentos sintéticos válidos contra XSD UBL2.1 CS1 de referencia. Faltan anexo DIAN vigente, campos completos, CRM/solicitud y política revisada, PDF-A3, cifrado/custodia, firma XAdES, acuses auténticos y habilitación profesional/productiva. Implementación63 añade firma XAdES local de laboratorio con salida cifrada; no acredita certificado/política DIAN, PKIX/revocación/TSA, custodia hardware ni habilitación fiscal real. Implementación66 inicia H09 con verificación XMLDSig de acuses explícitamente de laboratorio y diario local de reintentos; no habilita transmisión ni estados oficiales, numeración o aceptación DIAN. R04 2026-11-10 conecta fuente comercial revisada a borrador COP en ambos paneles y rechaza alteraciones/obsolescencia; no acredita identidad tributaria, perfil DIAN, representación fiscal, firma o aceptación externa.

## ACC-010 · Envelope encryption cliente y recuperación

2/3 hitos. Pendiente: SDK y paquete cliente recuperable/rotable con HMAC/contexto/versiones, ambos paneles y rechazo de manipulación verificados. Faltan custodia/recuperación hardware o cliente cualificados, referencias/publicación BYOS y última versión/ramas, medios/backup reales, representación y validación física/productiva; sin revocación de copias anteriores. Confirmaciones BYOS inciertas ahora se recuperan por versión/huella exactas y reintento idéntico, con API/SDK y ambos paneles, pruebas PostgreSQL y TLS de laboratorio. Pendientes titularidad/destino/TLS/grants reales, política de custodia/retención, recuperación física y aceptación productiva.

## ACC-011 · Conectores BYOS y OAuth mínimos

2/3 hitos. Pendiente: API independiente/cliente HTTPS y paquetes versionados PostgreSQL probados con rol mínimo, revocación, concurrencia y restore aislados. Pendientes propiedad/dominio/TLS/credenciales/perfiles y ambos paneles provisionados reales, operación/retención/RPO/RTO/commit incierto y escritores privilegiados; sin acreditar OAuth/alternativas no implementadas, propiedad legal, HMAC servidor ni custodia real. Confirmaciones BYOS inciertas ahora se recuperan por versión/huella exactas y reintento idéntico, con API/SDK y ambos paneles, pruebas PostgreSQL y TLS de laboratorio. Pendientes titularidad/destino/TLS/grants reales, política de custodia/retención, recuperación física y aceptación productiva.

## ACC-012 · Órdenes, novedades y controles SG-SST

2/3 hitos. Pendiente: Implementación69 añade datos persistentes de autorización profesional cifrada, EPP, jornadas/descanso y revocaciones; permisos clínicos explícitos; despacho positivo de orden genérica con política provisionada y dos confirmaciones del titular; cierre hacia VALIDACION con jornada registrada, sin costo/nómina. Pendientes datos/habilitación profesional y política laboral legítimos, evidencia física/off-platform, procesos especializados, interfaces, migración histórica, PostgreSQL/concurrencia y custodia cualificada. No habilita producción ni actuación física.

## ACC-013 · Reglas de nómina, costos y provisiones

2/3 hitos. Pendiente: Suplementos por minutos/tasas/divisor y bases declarados operables con16 pruebas ORM nuevas y ambos paneles. Pendientes clasificación laboral oficial por horarios/festivos, enlace individual de minutos a jornadas, otras novedades/ausencias/viáticos, nómina electrónica, datos legítimos y cualificación productiva. Corte2026-11-10: deducción fija declarada por trabajador enlazada al neto/pasivo y recuperación/costos en ambos paneles, sin acreditar consentimiento/eligibilidad/caps legales. Pendientes otras novedades, ausencias, incapacidades, viáticos, DIAN y aceptación profesional/productiva. Corte posterior: deducciones fijas desde NovedadNomina con consumo único y rollback verificadas en ambos paneles y PostgreSQL16 de laboratorio. Sustituye el pendiente de ese subtipo de novedad; otras novedades, ausencias/incapacidades/viáticos, corrección de fuentes consumidas, aceptación profesional y DIAN siguen pendientes. Devengados registrados2026-11-10: bonificaciones/comisiones declaradas enlazadas a planilla, detalle, aportes/bases, neto, asiento y costos en ambos paneles, con consumo único PostgreSQL16 de laboratorio. Sustituye el pendiente de ese subtipo; no acredita clasificación legal automática ni otras novedades, ausencias/incapacidades/viáticos, DIAN o aceptación productiva. Captura nativa2026-11-10: creación desde ambos paneles y recuperación por referencia hasta posteo/costos verificadas, sin novedades precargadas. Sustituye pendiente de captura de ese subtipo. Aún faltan corrección/retiro, custodia de originales automatizada, otras novedades, revisión laboral, DIAN y cualificación productiva. Corrección nativa2026-11-10: sustituido el pendiente de corrección de fecha/importe/soportes para fuentes nativas aún pendientes en planilla BORRADOR; ambos paneles, revisión invalidada, posteo/costos y concurrencia comprobados. Permanecen retiro, ajustes de fuentes consumidas/legado, otras novedades y aceptación externa.

## ACC-014 · Impuestos y conciliación continua

2/3 hitos. Pendiente: Implementación70 añade hecho comercial declarado/revisado: compras/ventas, IVA descontable/generado y retenciones con cuentas por componente, asiento canónico y contrapartida, dos confirmaciones y recuperación. Pendientes fuentes nativas/documentales, deduplicación entre rutas, conciliación fiscal unificada, devoluciones parciales, interfaz, SQL/concurrencia PostgreSQL y revisión normativa/profesional. Las reservas conservan sus restricciones de retención/múltiples impuestos. No hay aceptación oficial, pagos ni emisión fiscal. Implementación71 atribuye reservas/hechos comerciales y contrapartidas en un registro integrado de activos/pasivos visible en ambos paneles; valida sumas y evidencia en lote. No completa normativa, fuentes nativas ni aceptación profesional. Implementación72 conecta proveedores/facturas nativos con captura idempotente, fuente/huella reservadas, dos confirmaciones y contrapartida en ambos paneles. UI de un concepto; pendientes historia sin captura, cambios controlados, devoluciones parciales, fiscalidad completa y cualificación profesional/productiva. Recuperación2026-11-10: historial, correcciones previas a revisión/posteo y devoluciones proporcionales acumuladas con dos confirmaciones y asiento compensatorio local. Conserva fuentes originales; no emite nota fiscal ni ejecuta reembolso. Pendientes retorno por concepto, atribución tributaria de los nuevos ajustes en el registro unificado, normativa e interfaces completas. Registro interno de devoluciones proporcionales recuperadas corregido y probado: IVA/retenciones, cadena, recibo e idempotencia. Continúan notas fiscales, múltiples conceptos, contraste DIAN y revisión profesional. Compras múltiples 2026-11-10: interfaz/recuperación exacta de conceptos y mapas tributarios en ambos paneles, políticas mixtas y tributos adicionales con cotejo del registro integral y contrapartida completa verificados localmente. Pendientes devoluciones por concepto, notas fiscales, lotes extensos, fuentes/reglas profesionales y cualificación productiva; no acredita aceptación completa. Corte posterior: devoluciones por concepto nativas y correcciones con atribución tributaria verificadas localmente en ambos paneles; el pendiente anterior de ese incremento queda implementado. No sustituye nota fiscal ni revisión profesional, PostgreSQL/concurrencia o aceptación completa. PostgreSQL16: concurrencia del flujo de devoluciones por concepto y correcciones verificada con rol restringido de laboratorio. Permisos, migraciones, carga y aceptación productivos siguen pendientes; descarga de historial no sustituye documento fiscal.

## ACC-015 · Legacy bridge y open banking

2/3 hitos. Pendiente: Conciliación COP por filas/período, períodos vacíos, agrupación/asignación parcial acumulada, consolidación de lotes e historia hasta20k ejercitados en ambos paneles. Falta autenticidad/consentimiento del origen bancario, FX/instrumentos/otros formatos y tránsito, snapshots/carga/archivo/migración y aceptación profesional/productiva. Catálogo2026-11-11: retirado truncamiento inaccesible de50 mediante páginas verificadas en ambos paneles; probado53/55 lotes. Persisten1000 confirmaciones por empresa,20 seleccionadas por consolidación,200 filas/200 movimientos,COP; falta snapshots/carga, presentación de429 del puente, fuentes auténticas y aceptación profesional.

## ACC-016 · Proyecciones y ratios turísticos

2/3 hitos. Pendiente: Liquidez y RevPAR/GOPPAR hoteleros sobre cuentas y capacidad revisadas, con cortes temporales verificables localmente. Pendientes fuentes operativas legítimas/independientes, inventario intradía y otros modelos, ocupación/ADR/cupos, paquetes y dimensiones de costos, series/calibración y aceptación profesional/productiva.

## ACC-017 · Monte Carlo y recomendaciones

2/3 hitos. Pendiente: Motor de ventanas múltiples y UI de holdout individual probados; faltan interfaz de ventanas, series reales y cualificación profesional/calibración/rendimiento.

## ACC-018 · Factores de carbono y ledger ambiental

2/3 hitos. Pendiente: Cálculo y registro revisado persistente, versiones de factores y exclusión por código de actividad en ambos paneles/APIs; sin obligación ni crédito. Faltan fuentes/soportes legítimos, integración operativa y duplicados semánticos, búsqueda/cortes/exportación, incertidumbre, cualificación profesional y reconocimiento válido. Implementación65: correcciones append-only con dos revisiones y recuperación de valor efectivo en ambos paneles; faltan formularios de corrección, concurrencia PostgreSQL específica y controles de historia frente a SQL privilegiado. Recuperación2026-11-10: reporte por fechas vuelve a verificar la cadena y conserva la corrección efectiva, fuentes de factores y soportes declarados. Sin autenticidad externa, formulario nuevo ni cierre de aceptación.

## ACC-019 · Reportes ESG y marcos aplicables

2/3 hitos. Pendiente: Incremento local: reporte JSON por período, mapeo GRI/SASB declarado con versión, justificación y soporte; revalida cadenas/factores y usa la corrección efectiva sin doble suma. No certifica autenticidad de soportes, aplicabilidad normativa ni cobertura completa; faltan catálogo/marcos revisados, datos legítimos, duplicados semánticos, exportaciones e interfaces completas y aceptación profesional/productiva. ESG2026-11-11: ambos paneles permiten declarar varios límites, resumir soporte local y exportar actividades efectivas aCSV/JSON con ámbito/hash/aritmética comprobados; vacío explícito sin inventar cobertura. Siguen factores/soportes auténticos, aplicabilidad profesional, duplicados semánticos y snapshots/volumen/aceptación integral.

## ACC-020 · Consultas NLP de solo lectura

2/3 hitos. Pendiente: Consulta determinista ERP y corporativa verificadas con fuentes reales del ledger de prueba y rechazo de inyección. Falta modelo abierto/privado evaluado, dataset, voz, más fuentes/roles, rendimiento y dispositivos reales; sin SQL libre ni acciones financieras.

## ACC-021 · RPA financiera con autorizaciones

2/3 hitos. Pendiente: Primer incremento: ensayo financiero persistente en ERP y puente corporativo con dos confirmaciones del mismo titular y revisión de importe/destino; idempotencia, vencimiento, cancelación y vínculo revocado probados. Sin pagos, trabajador bancario ni integración con motor de escritorio. Faltan UI, proveedor/beneficiario/soportes legítimos, autorizaciones resistentes a suplantación, recibos, concurrencia PostgreSQL, recuperación operacional y aceptación profesional/productiva. Recuperación2026-11-10: reembolso de una transferencia interna ejecutada, financiado por saldo empresarial existente, consentimiento del destinatario y dos firmas separadas; saldos/movimientos/asiento en una misma transacción local. Cancelación/renovación de intenciones vencidas invalidan autorizaciones. Sin pagos bancarios, activación financiera automática, aceptación física ni producción.

## ACC-022 · Offline cifrado y conflictos

2/3 hitos. Pendiente: Borrador ambiental individual cifrado, CAS entre pestañas, exportación/restauración y reanudación online supervisada verificados. Faltan arranque/cache offline completos, más dominios, catálogo/retención/evicción, sincronización ampliada, SQLite/custodia nativa y dispositivos reales; sin liquidación ni autorizaciones offline.

## ACC-023 · Benchmark250ms y precisión IA

2/3 hitos. Pendiente: Primer incremento local: herramienta reproducible de benchmark con dataset/hardware/manifiesto, p50/p95/p99/máximo/errores y evaluador de predicciones con abstenciones.100 compras sintéticas en SQLite en memoria, cuatro flujos, sin HTTP/concurrencia; conciliación máxima547.209ms antes y134.922ms después de la optimización. No acredita250ms extremo a extremo ni99.8% IA: clasificador no ejecutado. Pendientes carga/hardware/dataset autorizados, cualificación y revisión independiente.

## ACC-024 · Recuperación, seguridad y despliegue

2/3 hitos. Pendiente: Flujo central con rol limitado y backup/restore local probados; faltan permisos/rutas completos, revisión de UPDATE(id), roles reales, RLS/funciones privilegiadas y llaves/medios/RPO/RTO según alcance.
