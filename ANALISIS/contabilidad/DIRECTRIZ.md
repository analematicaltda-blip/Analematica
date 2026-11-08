# Directriz técnica y contratos de los siete pools

Origen: Architecture Blueprint & Work-Pools Specification suministrado por el usuario. Dominio: ERP de empresas prestadoras de servicios turísticos. Nombre de iniciativa: Quantum Ledger-Centric & Zero-Knowledge Architecture. “Quantum” es el nombre del programa; no acredita computación cuántica, una blockchain ni una prueba ZK implementada.

## Principios y alcance funcional requerido

1. **Ledger-first:** los hechos económicos de ventas, reservas, consumos y personal deben afectar el libro mayor de forma consistente y trazable; el evento de negocio no puede marcarse financieramente consumado sin su asiento/régimen de reconocimiento validado. Incidentes no monetarios quedan auditados; no se inventan cargos o provisiones sin regla aplicable.
2. **Bóveda soberana de conocimiento cero:** facturas, soportes y evidencias cifrados en cliente mediante DEK única y KEK bajo control exclusivo del cliente; BYOS Google Drive/OneDrive/PostgreSQL/S3 del cliente. El ERP central no almacena llaves maestras ni documentos fiscales en claro persistidos o en cachés compartidas.
3. **Operación-personas-finanzas:** órdenes, turnos, novedades y riesgos enlazan nómina, SG-SST y costos con reglas vigentes, autorizaciones, evidencia y estados transaccionales explícitos.
4. **Ratios continuos:** cada hecho contable validado actualiza proyecciones financieras y ratios turísticos definidos, con fecha de corte, moneda, fuentes y reconciliación.

## Pool1 · CRM, facturación electrónica y Zero-Vault

- Eventos de oportunidad WON y reserva confirmada con tenant contable verificado, event_id, fecha económica, moneda, versión de contrato y propósito. Kafka/gRPC son transportes, no pruebas de consumo ni reconocimiento fiscal.
- Desglose de paquetes con bases, tarifas, tratamientos gravados/exentos/excluidos y tasas parametrizados por jurisdicción, vigencia y evidencia normativa. No asumir que una categoría turística es automáticamente exenta.
- XML, representación PDF/A-3 cuando corresponda, firma con certificado del cliente y validación ante DIAN/SAT u homóloga. Acuses y rechazos reales determinan el estado legal; no hay emisión efectiva por el mero envío.
- Envelope encryption AES-256-GCM o ChaCha20-Poly1305; DEK aleatoria por documento, nonce único y metadatos autenticados. KEK en HSM/KMS del cliente o derivación local de passphrase; no persistir passphrase/DEK/KEK descifradas en el ERP.
- Google OAuth `drive.file`, Microsoft `Files.ReadWrite.AppFolder`, PostgreSQL bytea o bucket S3 del cliente: cifrar antes de transmitir y validar permisos y límites de cada proveedor. Archivo, sobre DEK cifrado y metadatos mínimos permanecen en almacenamiento autorizado del cliente.
- Aceptación: captura y análisis de logs/cachés/almacenamiento del ERP no recuperan documento ni claves privadas; restauración y rotación verificadas con credenciales del cliente. Esta certificación aún no existe.

## Pool2 · Operación, SG-SST, nómina y costos

- Guías, conductores, tripulación y hotelería: registro móvil georreferenciado de inicio/fin, turnos, pernoctaciones, comisiones y viáticos, con minimización y permisos.
- Recargos, extras, festivos, aportes, prestaciones y tratamientos de viáticos según reglas laborales vigentes, trazables y revisadas. Nómina electrónica solo se acredita con respuesta real de autoridad/proveedor.
- Aptitud, EPP/dotación, riesgos ARL y fatiga antes de rutas/actividades; acceso restringido a información médica. Geolocalización y registros no constituyen por sí solos aptitud ni prueba de servicio cumplido.
- Costo de mano de obra por servicio, centro de costos y paquete; causación/provisión consistente con el hecho reconocido. No se promete precisión de microsegundos ni se contabiliza una estimación como pago realizado.

## Pool3 · Ledger y Legacy Bridge

- Registro append-only de asientos contabilizados; correcciones mediante contrapartidas deterministas vinculadas, sin edición/borrado de originales.
- Eventos versionados, idempotencia con detección de payload divergente, transacciones SQL y outbox; recuperación y reprocesamiento sin duplicados.
- IA propone clasificación PUC/NIIF con confianza calibrada, abstención y revisión humana; objetivo99.8% exige benchmark representativo y medición de errores materiales, no un umbral escrito en código.
- Balances y estados por proyecciones reconciliadas; información continua no elimina cierres, periodos bloqueados ni obligaciones legales.
- Open banking y pasivos/proveedores/patrimonio con permisos explícitos. Fiat, cripto, CBDC y créditos ambientales requieren catálogos, valoración, fuentes y tratamiento normativo; no habilitar activos sin soporte real.

## Pool4 · Integridad y cumplimiento fiscal

- Canonicalización versionada, hashes por asiento, encadenamiento/Merkle y pruebas de verificación. Separar evidencias del autor/firma, orden y controles SQL; una concatenación hash no es triple partida ni una ZKP.
- Pruebas comprador-vendedor-auditor/regulador y contratos inteligentes solo tras definir protocolo, participantes y revisión criptográfica. Nunca afirmar que existe verificación de una entidad sin su participación.
- Detección de anomalías puede proponer retención/revisión; no enviar fondos ni ejecutar aislamiento externo por una inferencia estadística.
- IVA/retenciones, auxiliares y conciliación regulatoria con reglas versionadas, trazas, redondeo explícito y validación oficial. “Cero diferencias” es un criterio a comprobar, no una garantía absoluta.

## Pool5 · Oracle Finance

- Margen por paquete=(ingreso-costos directos)/ingreso; eficiencia de nómina=costo asignado/ingresos operativos; liquidez ácida=(efectivo+equivalentes+inversiones temporales+CxC inmediatas)/pasivo corriente.
- RevPAR=ingreso de habitaciones/habitaciones disponibles; GOPPAR=resultado operativo bruto/habitaciones disponibles. Otros cupos/pasajeros requieren una métrica con nombre/denominador propios.
- Denominador cero se informa como no calculable, sin valores ficticios. Cohortes, impuestos, base contable, moneda y fechas de ocupación tienen que estar definidos.
- Monte Carlo30/90/365d con semillas reproducibles, supuestos y sensibilidad de estacionalidad, clima y tipo de cambio. Recomendaciones fiscales/inversión son revisables; no órdenes autónomas ni predicciones garantizadas.

## Pool6 · Eco-Ledger

- Factores de emisión por km/pasajero, combustible/medio y viajes, con fuente, unidad, versión y fecha. Calcular emisiones no prueba compensación.
- Reservas/pasivos ambientales requieren obligación, política y reconocimiento contable válidos; no deducir un pasivo de cualquier venta sin regla.
- Balance ESG complementario, trazabilidad de capital natural y créditos redimidos sin doble conteo; mapear GRI/SASB aplicables y evidencia antes de etiquetar un reporte como conforme.

## Pool7 · Neuro-Assist

- Consulta textual/voz a proyecciones de solo lectura y herramientas acotadas. No ejecutar SQL libre producido por un LLM; autorización de tenant/rol también en la capa de datos.
- Rentabilidad de ruta/últimas4h con fuentes, ventanas, calidad y costo de nómina/combustible conciliados. Gráficas trazables, no datos de ejemplo presentados como reales.
- RPA de nómina/proveedores basada en comprobación de obligaciones, cuenta y presupuesto, conservando dos autorizaciones separadas del mismo administrador y tercera de impacto. Evidencia satelital no autoriza por sí sola una transferencia.

## Contratos y estados de referencia

`sales.orders.confirmed` → facturación pendiente de validación y asignación operativa.
`ops.movements` → cálculo laboral/controles SG-SST/costos → propuesta de asiento validada.
`accounting.entry.posted.v1` → conciliación fiscal y proyecciones/ratios.

Todo contrato requiere event_id, tenant contable, aggregate_id/version, occurred_at, schema_version, correlation_id, causation_id, idempotency_key, moneda/unidades y origen autorizado. Usar importes decimales como texto; nunca float binario para dinero. La carga de eventos no contiene documentos fiscales, claves, tokens, información médica ni datos personales innecesarios.

Estados: borrador → validado → contabilizado; aprobación operativa, firma/acuse fiscal, pago y conciliación son estados separados. No marcar acciones externas concluidas hasta comprobar recibo/resultado.

## Definition of Done del programa

1. Bóveda: ensayos forenses y revisión independiente del modelo de amenaza; sin artefactos/claves en claro en ERP, con recuperación del cliente probada.
2. Latencia: objetivo≤250ms para el trayecto interno acordado y bajo carga definida; medir p50/p95/p99 y máximo observado, hardware, volumen y fallos. Las dependencias externas/offline se informan aparte; no se certifica el objetivo con un microbenchmark.
3. Determinismo: partida doble exacta, periodos/monedas y reglas correctos, idempotencia, contrapartidas y pruebas criptográficas versionadas; revisar además SQL directo y operadores privilegiados.
4. Offline: cola local cifrada, sincronización idempotente y conflictos revisables. CRDT para campos compatibles; jamás fusionar automáticamente asientos, firmas, pagos o cierres en conflicto.

Todos estos criterios requieren evidencia y continúan abiertos, salvo las correcciones iniciales acotadas señaladas en la matriz.
