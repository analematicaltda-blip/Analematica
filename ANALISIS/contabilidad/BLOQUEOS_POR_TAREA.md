# Bloqueos para aceptación completa

## ACC-001 · Validación monetaria exacta y aislamiento de cuentas

3/3 hitos. Pendiente: Ninguno en los cinco criterios funcionales originales deACC-001; cierre evidenciado2026-11-11. No equivale a habilitación productiva, fiscal/bancaria o cierre de otras tareas.

## ACC-002 · UUID de alta y guardas de asientos/líneas

3/3 hitos. Pendiente: Ninguno en los criterios originales deACC-002, cerrados2026-11-11. ORM masivo requiere las guardas SQL del esquema migrado, verificadas enSQLite/PostgreSQL. SQL privilegiado, roles/RLS y despliegue global pertenecen aACC-007/024; no se acreditan aquí.

## ACC-003 · Idempotencia y outbox en una transacción

3/3 hitos. Pendiente: Ninguno en los criterios transaccionales locales originales deACC-003; cierre2026-11-11. No se acredita publicaciónKafka, acuse externo ni exactly-once de red; esos alcances no se deducen del outbox local.

## ACC-004 · Periodos, concurrencia y contrapartidas

3/3 hitos. Pendiente: Ninguno en los criterios originales deACC-004, cerrados2026-11-11: carreras PostgreSQL y orden de bloqueo de cuentas/períodos. No se acreditan política legal de cierre, rawSQL privilegiado, carga/roles productivos ni reconstrucción de legados/snapshots pendientes enR11.

## ACC-005 · Puente TourismProvider a Tenant y actor verificables

3/3 hitos. Pendiente: Ninguno en los criterios originales del puente internoACC-005, cerrados2026-11-11. Provisión/renovación/historial/SSO/roles y cualificación productiva más amplios siguen en el plan de identidad. No se acredita identidad legal externa ni atomicidad distribuida.

## ACC-006 · Monedas, FX y valoración

3/3 hitos. Pendiente: Ninguno en los criterios originales internos deACC-006. Criterios originales de validación interna cerrados2026-11-11 en USD/EUR haciaCOP: fuente/version/soporte declarados, vigencia, moneda activa, dos confirmaciones, sin fallback global ni float. Autenticidad externa de tasas, legados/lotes, comisiones/división/tránsito, otras monedas y aceptación profesional/productiva permanecen pendientes del alcance global.

## ACC-007 · Hash canónico versionado y controles SQL

3/3 hitos. Pendiente: Ninguno en los criterios originales internos deACC-007. ACC-007 cerrada2026-11-11 en los criterios originales internos: hash v2 detecta identidad/importe/moneda, SQL protege cabeceras/líneas e identidad de cuentas utilizadas; diagnóstico compara estructura y cuerpos esperados. Historia preservada y migración reversible probadas en bases desechables. No acredita dueño/superusuario hostil, firma independiente, RLS/roles desplegados, migración histórica del cliente ni cualificación productiva.

## ACC-008 · Contrato CRM y reserva hacia facturación

3/3 hitos. Pendiente: Ninguno en los criterios originales internos del contratoACC-008. Criterios originales del contrato CRM/reserva cerrados2026-11-11: fuente real ganada/confirmada, vínculo empresarial revisado, revisiones/solicitudes versionadas, idempotencia y sin cobro/acuse fabricado, en ERP y puente corporativo. No acredita emisión/acuse DIAN auténticos, banco independiente, múltiples anticipos, política normativa, formularios CRM completos, recuperación/renovación de vínculo ni aceptación profesional/productiva.

## ACC-009 · XML, representación y firma fiscal

2/3 hitos. Pendiente: NO cerrada. ACC-009 activa y NO cerrada: borrador CRM/reserva en ambos paneles, corrección de doble cabecera XML, dos documentos CRM válidos contra XSD UBL2.1 CS1 de referencia y cifrado local probados. Pendientes perfil/anexo DIAN vigente, representación fiscal/PDF-A3, firma/custodia autorizadas, transporte de habilitación y acuses reales. Laboratorio y formato declarativo no habilitan facturación. Desarrollo pendiente: Concretar perfil fiscal conforme al anexo vigente y al canal de habilitación elegido: campos/catálogos/identidad, numeración/CUFE/QR y representación fiscal/PDF-A3; el borrador estructural no lo sustituye. Cualificar e integrar firma real y custodia autorizada: certificado/política/cadena, validación y revocación/reloj según perfil; el firmador actual sigue LABORATORY_ONLY. Implementar y verificar transporte del canal autorizado y validación de acuses auténticos/resultado incierto con evidencia real de habilitación. Requisitos externos: Confirmar canal DIAN directo o proveedor autorizado y anexo/perfil vigente aplicable. Disponibilidad de certificado legítimo y autorización/custodia del cliente mediante canal seguro; nunca clave/PIN por chat. Resolución/identidad, software/test set y acceso de habilitación configurados de forma segura. Obtener documentos/acuse reales y validación profesional/de proveedor; ningún test sintético acredita este requisito. Decisión expresa posterior: canal DIAN directo confirmado por el usuario; integración con su plataforma aplazada a una etapa posterior. No se confirma disponibilidad de certificado ni set de pruebas y no se cierra el criterio original.

## ACC-010 · Envelope encryption cliente y recuperación

3/3 hitos. Pendiente: Ninguno en los criterios originales del cifrado portátil cliente deACC-010. Criterios originales del cifrado portátil cliente cerrados2026-11-11: DEK aleatoria, KEK cliente, AAD, exclusión de plaintext/llaves ERP y recuperación/rotación probadas en ambos paneles, con referencia exacta opcional. No acredita hardware, titularidad/TLS/grants reales, custodia/backup físicos ni producción. Rotar no revoca copias antiguas; no recuperar sin secreto/archivo. ACC-009 sigue abierta.

## ACC-011 · Conectores BYOS y OAuth mínimos

2/3 hitos. Pendiente: Drive y OneDrive elegidos por el usuario. Adaptadores locales OAuth PKCE y cargas de ciphertext con planes de recuperación implementados; 17 pruebas de contrato con proveedores simulados y 28 regresiones BYOS aprobadas. Pendientes aplicaciones nativas OAuth registradas, autorización/cuenta/propiedad y permisos reales, cualificar creación condicional y descargas, aprovisionamiento de carpeta Drive, integrar flujo nativo/UI de ambos paneles y recuperación/retención operativa. Los scopes drive.file y Files.ReadWrite.AppFolder son lectura/escritura acotadas, no escritura exclusiva. Sin aceptación completa ni validación cloud real; PostgreSQL de laboratorio no acredita titularidad del cliente.

## ACC-012 · Órdenes, novedades y controles SG-SST

2/3 hitos. Pendiente: Órdenes genéricas: aptitud cifrada, EPP, descanso/jornadas, dos confirmaciones y evaluación de riesgo específica por orden verificadas localmente. Nuevos controles de peligros, clase de riesgo por trabajador, EPP adicional y vigencia; cambios invalidan confirmaciones. Pendientes procesos especializados, interfaces completas y conexión operacional de ambos sistemas, datos/roles y autorización profesional legítimos, validación física, PostgreSQL/concurrencia, migración histórica y cualificación productiva. Pruebas sintéticas no acreditan legitimidad profesional ni afiliación ARL.

## ACC-013 · Reglas de nómina, costos y provisiones

2/3 hitos. Pendiente: Trazabilidad de costos v2 por jornada/centro/referencia comercial y ventana operativa implementada; cambio de referencia invalida revisión o calificación actual; reatribución no duplica gasto/provisión. Reglas por minutos, novedades y bases declaradas preservadas. Pendientes enlace individual de minutos de cada recargo a jornadas, clasificación legal por horarios/calendario/festivos, otras novedades/ausencias/incapacidades/viáticos, retiro/ajuste de fuentes consumidas, DIAN nómina y aceptación profesional/datos legítimos. La referencia comercial es un UUID declarado; no prueba por sí sola un paquete vendido ni titularidad externa.

## ACC-014 · Impuestos y conciliación continua

2/3 hitos. Pendiente: Conciliación interna COP de IVA generado/descontable y retenciones con fuentes, devoluciones y contrapartidas; registro v3 explica versión/vigencia/soporte/categoría por concepto en ambos paneles y revalida la política original, sin aplicar versiones futuras a movimientos antiguos. Pendientes fuentes de reservas sin política capturada, marco normativo/turístico revisado profesionalmente, períodos declarativos y conciliación multicuenta, cobertura completa de operaciones, contraste oficial DIAN y aceptación profesional/productiva. El reporte de cuenta seleccionada no es declaración ni autorización de deducibilidad.

## ACC-015 · Legacy bridge y open banking

2/3 hitos. Pendiente: Importación neutral multibanco con bank_id y estados declarados BOOKED/PENDING/REVERSED; pendientes/revertidos bloqueados en conciliación simple, manual y agrupada/entre lotes. 120 cuentas contables empresariales retenidas y aisladas probadas; ese ensayo no constituye alta ni conexión de cuentas bancarias personales. Objetivo del usuario: todos los bancos de Colombia y más de50 cuentas por usuario. Pendientes catálogo/conectores oficiales o agregador autorizado, consentimiento/credenciales y fuentes auténticas, gestión/alta/custodia de cuentas personales independiente de empresa, FX, snapshots/carga y aceptación profesional/productiva. CSV y estados declarados no autentican al banco; no hay pagos sin autorizaciones.

## ACC-016 · Proyecciones y ratios turísticos

2/3 hitos. Pendiente: Liquidez exacta independiente del contexto decimal, desglose de cuentas, moneda/corte/unidad y referencia del ledger implementados; nueva consulta corporativa cotejada con ERP y validada aritméticamente. División por cero/denominador no positivo devuelve no calculable. Pendientes cobertura de ratios por paquete/dimensiones de costos, fuentes operativas legítimas e independientes, series/calibración y aceptación profesional/productiva. RAT, ocupación y ADR siguen diferidos por instrucción expresa del usuario; no se desarrollaron en esta entrega. Las clasificaciones son declaradas por el titular y el corte no reconstruye una publicación histórica original.

## ACC-017 · Monte Carlo y recomendaciones

2/3 hitos. Pendiente: Simulación 30/90/365, semilla y supuestos explícitos, sensibilidad y backtesting de2–4 ventanas operables en ambos paneles; precisión aislada y transporte analítico acotado verificados. Usuario confirmó que no dispone de serie diaria autorizada de al menos379 días. Pendientes obtención/conciliación de series reales, calibración y validación fuera de muestra con datos legítimos, estacionalidad/modelos más amplios, recomendaciones financieras revisadas y cualificación de carga/productiva. Los percentiles son escenarios empíricos, no intervalos de confianza calibrados ni autorización para ejecutar dinero. Auditoría1–18: contrato corporativo coteja huellas/importes de entrada y resultados posteriores, proporciones de déficit y errores; claves React distintas evitan formularios duplicados al cambiar de empresa. Sin crédito adicional ni aceptación externa.

## ACC-018 · Factores de carbono y ledger ambiental

2/3 hitos. Pendiente: Factores/unidades/vigencias explícitos, medición sin reconocimiento financiero y corrección efectiva sin doble conteo implementados. Vínculo opcional a orden propia/segmento impide duplicar ese origen al renombrar actividad o cambiar factor; correcciones preservan vínculo y registros históricos, con guardas de metadatos y precisión independiente. Usuario confirmó ausencia de factores documentados y política/obligación ambiental revisada por contador. Pendientes autenticidad/aplicabilidad de fuentes y factores, catálogo legítimo de segmentos/mediciones y duplicados semánticos fuera del vínculo declarado, obligación/compensación válida y aceptación profesional/productiva. No se crean pasivos, pagos, compensaciones ni créditos de carbono automáticamente.

## ACC-019 · Reportes ESG y marcos aplicables

2/3 hitos. Pendiente: Reportes ESG por período/corte de conocimiento y corrección efectiva, mapeo declarado GRI/SASB/propio, exportaciones JSON/CSV y ambos paneles implementados. Orden/segmento de origen y huella del soporte efectivo se conservan en consulta/exportación y siguen la corrección válida al corte; formatos históricos sin vínculo siguen legibles. Cálculo decimal aislado y rechazo de mapeos mal formados/campos privados inesperados probados. Usuario confirmó ausencia de factores documentados y obligación ambiental revisada. Pendientes factores/soportes auténticos, catálogo y aplicabilidad profesional de marcos, duplicados semánticos fuera del origen declarado, snapshots/volumen/concurrencia y aceptación integral/productiva. No se acredita certificación, obligación, compensación ni crédito ambiental.

## ACC-020 · Consultas NLP de solo lectura

2/3 hitos. Pendiente: Asistente determinista de rentabilidad, liquidez ácida y cola comercial en ERP/Analemática, con herramientas acotadas a empresa/rol, fechas explícitas, fuentes y aritmética revalidadas; rechaza SQL/instrucciones ajenas, respuestas alteradas y falsa aceptación DIAN. Evaluación reproducible sobre41 ejemplos sintéticos, no precisión de un modelo. Pendientes integración/evaluación de modelo local o privado, dataset autorizado representativo, voz, más fuentes/roles revisados y cualificación de rendimiento/dispositivos/privacidad. Sin SQL libre, APIs de IA ni acciones financieras; no se acredita aceptación integral.

## ACC-021 · RPA financiera con autorizaciones

2/3 hitos. Pendiente: Ensayo financiero persistente e interfaz compartida ERP/Analemática: preparación, dos confirmaciones separadas del mismo titular, impacto exacto, estado recuperable por UUID, cancelación idempotente incluso vencido y consulta de historial sin restaurar autorizaciones. Revalida metadatos, vínculo/actor, intención y evidencia de cada etapa; contrato corporativo acotado y sin permisos financieros/desktop. Reembolso interno financiado existente se conserva. Pendientes trabajador de ejecución integrado con agent-desktop/Open Duet, proveedor bancario/beneficiarios/soportes legítimos, autorizaciones resistentes a suplantación, acuses/recibos auténticos, carga/concurrencia de ejecución real e infraestructura objetivo, recuperación operacional ampliada y aceptación profesional/productiva. El ensayo no paga, no crea trabajos de escritorio ni constituye autorización bancaria; no hay aceptación integral. Cuatro carreras PostgreSQL desechables del ensayo, con rol restringido, verificadas sin pagos ni asientos; no cualifican el trabajador bancario/productivo.

## ACC-022 · Offline cifrado y conflictos

2/3 hitos. Pendiente: Capturador ambiental web con formulario y arranque en frío sin red, instalación explícita de worker limitado a archivos estáticos verificados por hash y sin credenciales; catálogo cifrado por empresa, eliminación con contraseña/versión/CAS y límites de100 borradores por empresa/500 por navegador sin evicción automática. Empaquetado reproducible para ERP/Analemática y rutas estáticas públicas exactas verificadas con Nginx, sin abrir panel/API. Exportación/restauración y reanudación online ambiental supervisada conservadas, sin autorizaciones restauradas. Pendientes captura de más dominios, sincronización/colas ampliadas y conflictos por dominio, retención/custodia nativa SQLite, validación Android/iOS/escritorio físicos y carga/actualizaciones/recuperación productivas. No es arranque offline del ERP completo ni liquidación financiera offline; no hay aceptación integral.

## ACC-023 · Benchmark250ms y precisión IA

2/3 hitos. Pendiente: Benchmark ORM y HTTP reproducibles con hardware/fuente/dataset, colas de1/4 clientes, muestras fallidas conservadas, percentiles exactos y conteos fuera de250ms. Se corrige dependencia del contexto decimal, pérdida del informe al fallar una operación y respuesta503 ante429. Optimización opcional de contexto/lectura unificados conserva actor/empresa/sesión/CSRF y revocación, con ruta anterior por defecto. Última medición:100 compras/400 operaciones ORM;240 intentos HTTP comparados; opción unificada sin errores en160 intentos, pero persisten muestras sobre250ms con4 clientes y picos ORM. No se ejecutó clasificador ni se acredita99,8%. Pendientes carga representativa, PostgreSQL/pool/infraestructura objetivo y medición evento-a-ledger/dispositivos/proveedores; modelo/dataset autorizado, evaluación independiente y aceptación productiva. La captura correcta del benchmark no significa cumplir su objetivo de rendimiento.

## ACC-024 · Recuperación, seguridad y despliegue

2/3 hitos. Pendiente: Respaldo SQLite endurecido POSIX y restauración PostgreSQL con integridad/guards/rol restringido verificados localmente; adaptador legado reparado con lecturas explícitamente autorizadas, serialización UUID y bloqueo de escritura/contrapartida alternativa, sin montarlo en rutas públicas. Pendientes rutas/permisos ERP completos, auditoría RLS/funciones privilegiadas, llaves/documentos/medios reales del cliente, RPO/RTO acordados y recuperación/despliegue/reversión en infraestructura objetivo.
