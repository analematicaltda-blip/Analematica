# Seguimiento único · Motor contable y20 hitos finales

Actualización:2026-11-11. Este archivo concentra desde ahora las novedades, hallazgos, bloqueos y siguientes acciones. No crear un informe Markdown por entrega o análisis. Los documentos anteriores se conservan como historia/evidencia; las matrices JSON y sus verificadores mantienen sus contratos.

## Estado real

**79,17% (57/72 hitos de la matriz original). Aceptación completa9/24 tareas (ACC-001 aACC-008 yACC-010;ACC-009 abierta). Producción no habilitada.** Las24 tareas tienen incrementos verificados;15 conservan alcance pendiente. Los cortesR01–R20 anteriores son históricos y no sustituyen la matriz actual de24 tareas. La existencia de código o una prueba sintética no sustituye aceptación profesional, de proveedor o física.

## Recuperación verificada · 2026-11-10

Base preservada: main `81dccf79c`, coincidente con origin/main al consultar el remoto antes del cierre. Los44 archivos locales originales (ZIP y respaldos web) se copiaron a `/tmp/sgacd-recuperacion-20261110T014547Z/locales.tar`; manifiesto SHA-256 verificado antes de publicar. No se incorporan al commit. La entrega tiene autorización expresa para un único commit consolidado y avance normal de main, sin force ni reescritura.

- ACC-019: motor de reporte JSON acotado por fechas y empresa; mapeo GRI/SASB declarado con versión, justificación, marco/límite y soporte. Verifica la integridad de observaciones/factores y usa la corrección efectiva, sin sumar dos veces el original. El reporte conserva unidades y fuentes; declara borrador, autenticidad externa y aplicabilidad no verificadas, y ausencia de certificación. Acredita incremento funcional y verificación local, nunca aceptación completa.
- Ambiental: se conservaron las correcciones append-only y sus dos confirmaciones existentes; las nuevas consultas/reportes revalidan su cadena. No se reconstruyó una función ya disponible ni se reconocen obligaciones, compensaciones o créditos ambientales.
- Banco: agrupación de varias filas y líneas, asignación parcial explícita con remanente, rechazo de reutilización, estado recuperable y liberación con dos confirmaciones. La reserva de una línea parcial es completa: para agregar otras coincidencias se libera y revisa el conjunto. No se acredita consumo incremental entre lotes, conciliación de período agrupada, FX ni fuente bancaria auténtica.
- Compras: correcciones controladas antes de la revisión/posteo, instantáneas anterior/posterior y cadena histórica; devoluciones proporcionales acumuladas con dos confirmaciones, sin exceder el original ni aceptar fracciones de centavo. El asiento compensatorio y su prueba son atómicos. No se emite nota fiscal, paga dinero ni completa la atribución de estos ajustes en el registro tributario integrado.
- Billetera: cualquier persona registrada conserva su acceso personal, sin exigir actividad turística. El reembolso financiado exige transferencia interna original ejecutada, fuente empresarial verificada, fondos existentes, consentimiento del destinatario y dos autorizaciones separadas del emisor. Saldo, movimientos y asiento comparten una transacción; un fallo contable revierte todos. Sin depósito, retiro o pago bancario simulado. Políticas declaradas por versión/vigencia y días de anticipación; no son una afirmación de normativa aplicable.
- Intenciones: cancelación incluso vencidas e invalidación de desafíos pendientes; renovación con otra clave y vínculo único al original, sin recuperar consentimiento, token o firmas. Un reembolso renovado recalcula la fecha de solicitud para revisar su política vigente. La migración wallet0005 conserva datos/saldos históricos desechables y exige consentimiento nuevo.

Validación de esta entrega: **232 pruebas en19 suites**, con ORM/API SQLite desechables, firmas ECDSA de software y HTTP real entre los dos backends. Incluye regresiones ambientales, bancarias, compras, alta/acceso personal, saldos y firmas por dispositivo. Las pruebas HTTP necesitaron permiso para sockets locales, bloqueados en el sandbox; completaron correctamente fuera de él. Las232 no se suman a los conteos históricos para inflar hitos. Evidencia automática con comandos/rutas y hashes: `evidencias/recuperacion-2026-11-10.json`.

Límites vigentes: no se añadieron formularios nuevos ni se acreditó aceptación visual/móvil de los flujos nuevos; se entregan APIs y puente corporativo autenticado conservando las interfaces actuales. Pendientes soportes/marcos legítimos, catálogo de aplicabilidad ESG revisado, duplicados semánticos, notas fiscales/atribución tributaria de ajustes, PostgreSQL/concurrencia y migración histórica real, dispositivos físicos y aceptación profesional/productiva. Las autorizaciones de firma de pruebas usan claves de software; no prueban atestación física. Reservas, RAT y ADR quedaron fuera de las modificaciones. Ningún pendiente de identidad, proveedor, dispositivo o release se cerró con evidencia sintética.

## Entrega consolidada autorizada anterior

El usuario autorizó actualizar main con todo el trabajo acumulado, en una sola entrega. Antes de preparar el commit, main local y main remoto coincidían en `16bf4fa99d25695559f5502b5c9d45a503d5494c`. No se sustituye ni descarta trabajo externo; el push debe ser normal, sin force. Las cachés/bytecode generados no forman parte de esta publicación.

La publicación del código no significa despliegue productivo ni cierre de los20 hitos. La confirmación definitiva de publicación se realiza comparando el SHA local con `refs/heads/main` del remoto después del push.

## Novedades funcionales acumuladas

- Compras nativas: proveedor/factura persistentes, revisión tributaria contra su fuente, dos confirmaciones, posteo/recuperación/contrapartida en ambos paneles; protección frente a elusión por rutas genéricas.
- Operación/nómina: jornadas y capacidad explícita permiten distribuir costos de una nómina contabilizada, dejando visible el costo sin asignar, sin repetir gastos ni ejecutar pagos. Puente corporativo y formulario compartido disponibles.
- Nómina: horas extra y recargos por minutos, divisores y tasas declarados; bases de aportes/provisiones explícitas; asiento, detalle y costo concilian. Planillas de salario base superpuestas bloqueadas, incluso si ambos borradores se revisaron antes del primer posteo.
- Banco: selección de coincidencias ambiguas, motivos por diferencias pendientes, reservas de referencia/línea y liberación con dos autorizaciones. Estado parcial no se presenta como conciliación completa.
- Períodos bancarios: contraste de apertura/cierre y cobertura del libro COP, detección de omisiones compensadas y cambios retroactivos; calificación de período separada de la asociación de filas. La fuente bancaria sigue sin autenticación independiente.
- Entrega/recuperación: paquete verificable de cambios y aplicador con detección de conflictos, respaldos y reintento; videos locales de los componentes existentes con datos sintéticos. No se han usado cuentas bancarias reales.

## Verificaciones disponibles

La última regresión contable ejecutada aprobó **820 pruebas en46 suites**, incluidas84 del puente corporativo, con manifiesto estable y hashes comprobados. Se verificaron78 comprobaciones Chromium de período/regresión parcial y tipos estrictos de componentes seleccionados. Las herramientas de entrega aprobaron26 pruebas (12 específicas nuevas) y una aplicación/reintento de562 archivos sobre base desechable, sin cambios en main durante esa prueba. No se presentan estas comprobaciones como aceptación productiva ni como pruebas completas de Next.js o de dispositivos físicos.

Evidencias históricas: `evidencias/implementacion-77.json`, `../entregas/evidencias/ENTREGA-78.json`. Al añadir pruebas o resolver hallazgos, actualizar este archivo y las matrices existentes sin abrir nuevos informes de análisis.

## Matriz vigente de los20 hitos restantes

| Hito | Estado de código | Hallazgo/acción todavía pendiente | Validación externa |
|---|---|---|---|
| R01 · Recuperar y verificar el corte interrumpido | Verificado local | La interrupción dejó código tributario sin pruebas y no permitió confirmar la creación del archivo de tests. | Conservar verificación de fuentes y regresión. |
| R02 · Conectar política tributaria, reserva y ledger | Verificado local | La política versionada cotizaba impuestos mientras el desglose de la reserva seguía siendo manual; la integración escrita quedó sin verificar. | Tratamiento tributario y soportes legítimos revisados profesionalmente; la coincidencia interna no equivale a legalidad fiscal. |
| R03 · Completar retenciones, compras e IVA descontable | En ejecución | Implementación72 añade captura nativa de proveedores/facturas, instantánea, cotejo exacto contra política y reserva de documento/huella, impidiendo bypass por rutas genéricas. Posteo/recuperación/contrapartida probados desde ambos paneles; Recuperación2026-11-10 añade historia, correcciones previas al posteo y devoluciones proporcionales con asiento. Formulario de compras múltiples y recuperación de cuentas/tributos disponible en ambos paneles. Pendientes devolución por concepto, atribución tributaria integral de ajustes, nota fiscal, interfaces de ajustes y revisión profesional. | Reglas tributarias vigentes, responsabilidades y revisión de un profesional autorizado. |
| R04 · Completar documento fiscal y representación | En ejecución | Fuente comercial revisada y revalidada, API/puente corporativo/formulario en ambos paneles; importes fijados al origen, tasas declaradas cotejadas y referencia en XML. Pendientes perfil DIAN, numeración, notas/anticipos, PDF/A-3, firma y aceptación legítimas. | Anexo DIAN vigente, resolución e identidad legítimas, formatos/ejemplos autorizados y revisión fiscal. |
| R05 · Cualificar firma y custodia del cliente | Pendiente | Adaptar firma al perfil aprobado, cadena/política/revocación/reloj y custodia cliente, con recuperación y revocación controladas. | Certificado legítimo, política de confianza, medios/HSM/equipos y revisión independiente que correspondan. |
| R06 · Completar transporte DIAN y acuses auténticos | Pendiente | Implementar cliente de habilitación con destinos fijos, límites, autenticación aprobada, seguimiento y reintentos de resultado incierto ligados a numeración. | Acceso DIAN/proveedor autorizado, credenciales mediante canal seguro, test set, resolución y acuses auténticos. |
| R07 · Completar almacenamiento soberano operativo | En ejecución | API/SDK y ambos paneles recuperan cargas BYOS inciertas por versión/huella y reintento idéntico; PostgreSQL/HTTPS de laboratorio verificados. Pendientes destino/grants/certificados reales, custodia/recuperación física, retención y aceptación. | Destino propiedad del cliente, consentimiento, TLS/roles/grants y retención/backup legítimos. |
| R08 · Completar recuperación y rotación de custodia | En ejecución | API/SDK y ambos paneles recuperan cargas BYOS inciertas por versión/huella y reintento idéntico; PostgreSQL/HTTPS de laboratorio verificados. Pendientes destino/grants/certificados reales, custodia/recuperación física, retención y aceptación. | Política/medios reales del cliente y pruebas físicas de recuperación/hardware cuando aplique. |
| R09 · Implementar despacho SG-SST positivo y transversal | En ejecución | Datos laborales estructurados, cifrado estricto y ruta positiva para órdenes genéricas verificados en37 pruebas locales; migración SQLite fresca de6 tablas vacías. Pendientes procesos especializados, interfaces, datos/reglas/habilitación profesional y cualificación PostgreSQL. Sin aceptación completa. | Reglas SG-SST, roles profesionales y evidencia de aptitud legítima; nunca inferirla de texto libre ni exponer clínica. |
| R10 · Completar nómina y costos por operación | En ejecución | Distribución analítica de nómina contabilizada contra jornadas, capacidad explícita, dos confirmaciones, costo sin asignar y revisiones sin doble gasto:23 pruebas ORM/API. Pendientes puente corporativo, interfaces, reglas laborales completas y habilitación externa. Entrega74: puente corporativo con contrato, formulario compartido ERP/Analemática y dos autorizaciones;12 nuevas pruebas HTTP/contrato y40 comprobaciones Chromium. Faltan reglas laborales completas, aceptación profesional y producción. Entrega75: cálculo exacto de horas extra/recargos declarados, bases explícitas de contribuciones, detalle y posteo canónicos en ambos paneles; bloqueo de segunda planilla de salario base superpuesta.16 casos ORM y un recorrido HTTP corporativo nuevos;68 comprobaciones Chromium (suplementos y regresión base). No cubre clasificación legal automática ni otras novedades/DIAN. | Reglas laborales revisadas, datos legítimos de personal y habilitación de nómina electrónica para aceptación oficial. |
| R11 · Completar legados, lotes y valoración FX | En ejecución | Valoración inicial y revaluación acotada de posiciones monetarias dedicadas USD/EUR a COP; dos confirmaciones, ajuste incremental, ambos paneles y tres escenarios PostgreSQL16 desechable. Pendientes liquidaciones/consumos parciales, diferencias realizadas, lotes/legados, fuentes/clasificación profesionales y cualificación productiva. | Saldos/soportes originales, fuente FX autorizada y revisión contable profesional. |
| R12 · Completar conciliación bancaria y casos parciales | En ejecución |  Entrega76: selección de candidato ambiguo y diferencias explícitas por fila, conciliación parcial sin falsa completitud, reservas de referencias pendientes, recuperación/liberación y eventosv2;17 casos ORM/API,2 HTTP corporativos y6 de contrato nuevos. Pendientes saldos completos, pagos divididos/agrupados, FX y aceptación bancaria/profesional. Entrega77: cotejo de apertura/cierre y cobertura completa de libro para período declarado COP, con fuente revalidada, omisiones compensadas detectadas y ambos paneles.14 casos ORM,1 HTTP y4 de contrato nuevos. Recuperación2026-11-10 añade agrupación y asignación parcial explícita, remanentes, reservas y liberación. Pendientes banco auténtico, volúmenes/snapshots, períodos sin movimientos, consumo incremental entre lotes, período agrupado y FX. | Extractos legítimos; permisos/consentimiento bancarios si se integra API; revisión profesional. |
| R13 · Completar ratios turísticos y calibración | Pendiente | Implementar observaciones operativas versionadas, costos por producto y ratios con corte económico/de conocimiento y fuente verificable. | Series operativas reales y supuestos financieros revisados. |
| R14 · Completar corrección ambiental y reportes ESG | En ejecución | Recuperación2026-11-10: reporte por fechas con fuentes, unidades y mapeo GRI/SASB declarado; cadenas y corrección efectiva revalidadas en ORM/API y HTTP corporativo. Faltan aplicabilidad profesional, autenticidad de soportes, duplicados semánticos, exportación e interfaces completas; medición separada de obligación contable. | Factores, soportes y marcos revisados; obligación/compensación legítima si se reconoce financieramente. |
| R15 · Completar asistencia contable privada evaluada | Pendiente | Incorporar modelo local/privado mediante herramientas de lectura acotadas, evaluación reproducible y respuestas con fuentes; sin SQL libre ni permisos de escritura. | Dataset consentido, capacidad del equipo y revisión de calidad/privacidad; no afirmar99,8% sin medición. |
| R16 · Completar orquestación supervisada del motor | Pendiente | Conectar tareas al motor agent-desktop/Open Duet mediante permisos mínimos, dos autorizaciones separadas del mismo solicitante y revisión adicional de impacto. | Beneficiario/cuenta/proveedor/recibos legítimos y autorización explícita de cada acción real; no pagar por predicción, ubicación o simulación. |
| R17 · Completar operación offline y sincronización nativa | Pendiente | Implementar captura y cola cifrada por dominio, arranque sin red, conflictos visibles, sincronización idempotente y almacenamiento nativo requerido. | Dispositivos Android/iOS/escritorio y herramientas de compilación/hardware para pruebas físicas. |
| R18 · Completar recorridos e interfaces de ambos sistemas | En ejecución | Compras nativas compartidas en ambos paneles, soporte hash local sin subir archivos, confirmaciones separadas y recuperación tras recarga. Catálogo propio de compras con gastos, preservando ventas. Formulario de hasta veinte conceptos sujeto al límite de solicitud; conserva tributos adicionales al recuperar. No completa las otras interfaces pendientes. Entrega74: puente corporativo con contrato, formulario compartido ERP/Analemática y dos autorizaciones;12 nuevas pruebas HTTP/contrato y40 comprobaciones Chromium. Faltan reglas laborales completas, aceptación profesional y producción. Entrega75: cálculo exacto de horas extra/recargos declarados, bases explícitas de contribuciones, detalle y posteo canónicos en ambos paneles; bloqueo de segunda planilla de salario base superpuesta.16 casos ORM y un recorrido HTTP corporativo nuevos;68 comprobaciones Chromium (suplementos y regresión base). No cubre clasificación legal automática ni otras novedades/DIAN. Entrega76: selección de candidato ambiguo y diferencias explícitas por fila, conciliación parcial sin falsa completitud, reservas de referencias pendientes, recuperación/liberación y eventosv2;17 casos ORM/API,2 HTTP corporativos y6 de contrato nuevos. Pendientes saldos completos, pagos divididos/agrupados, FX y aceptación bancaria/profesional. Entrega77: cotejo de apertura/cierre y cobertura completa de libro para período declarado COP, con fuente revalidada, omisiones compensadas detectadas y ambos paneles.14 casos ORM,1 HTTP y4 de contrato nuevos. Pendientes banco auténtico, volúmenes/snapshots, períodos sin movimientos, importes divididos/agrupados y FX. | Aceptación de usuarios/roles reales cuando corresponda; no sustituirla por fixtures. |
| R19 · Medir rendimiento y endurecer seguridad | En ejecución | ACC-023: mediciones ORM/HTTP, propagación429 y contexto unificado opcional verificados;100 compras/400 operaciones ORM y240 intentos HTTP. Persisten muestras sobre250ms y clasificador no evaluado; no acreditaSLA ni99,8%. | Hardware/carga objetivo, dataset autorizado y revisión de seguridad independiente para cualificación productiva. |
| R20 · Restauración integral y aceptación final | Pendiente | Restaurar datos/archivos/referencias con roles reales, comprobar RPO/RTO, reversión y operación; consolidar entregables y preparar publicación revisable. | Medios/llaves/grants reales, aceptación profesional y de proveedor; publicación/producción solo con la autorización correspondiente. |

## Bloqueos de cierre prioritarios

1. Fiscal/DIAN: completar documento y representación, custodia/firma cualificadas, transporte/WS-Security y resultados inciertos con datos, certificado, resolución, test set y acuses legítimos. No convertir borradores de laboratorio en facturas aceptadas.
2. Banco/legados: completar consumo incremental entre lotes y calificación de período agrupado, FX y valoración, períodos sin movimientos y snapshots para más volumen; autenticidad del extracto y aceptación profesional pendientes. Límites locales actuales:30 filas importadas,200 movimientos por período y20000 líneas históricas de caja; lectura por lotes implementada, snapshots/carga objetivo pendientes.
3. Nómina/SG-SST: enlazar minutos individuales con jornadas y calendario/reglas laborales revisados; otras novedades, ausencias, incapacidades, viáticos, deducciones y nómina electrónica; completar despacho especializado y cualificar PostgreSQL.
4. Bóveda/recuperación: destinos reales del cliente, consentimiento, conectores/grants/retención, publicación de versiones y custodia/recuperación física.
5. Analítica/ESG/IA: datos legítimos y calibración, marcos/factores revisados y evaluación consentida del modelo privado; no afirmar precisión99,8% o certificación ambiental por pruebas sintéticas.
6. Multiplataforma/orquestación/producción: completar recorridos y sincronización nativa, validar Android/iOS/escritorio, cuentas/recibos reales con autorizaciones, carga/seguridad y restauración integral en infraestructura objetivo.

## Regla de mantenimiento

Actualizar aquí cada novedad con problema, solución, prueba y pendiente concreto. Actualizar estados/evidencias de las matrices existentes y regenerar PROGRESO.md cuando cambie el crédito verificable. No aumentar porcentajes por repetir pruebas o ampliar una tarea ya acreditada. No crear nuevos `IMPLEMENTACION_NN.md` ni documentos de cierre por entrega. Los registros técnicos automáticos y evidencias de pruebas pueden mantenerse en sus carpetas, sin duplicar análisis narrativos.


## Reconexión y hallazgo de originales · 2026-11-10

Se recuperó el acceso de esta conversación al entorno gestionado y se comprobó conexión Git real con `https://github.com/analematicaltda-blip/SGA-CD.git`. `git ls-remote` devolvió main `db754af1630b99bd89c602b02c252ee16fe92835`; después de fetch, una copia de trabajo nueva quedó en ese mismo SHA, rama `codex/conectado-20261110`, ruta `/workspace/SGA-CD-conectado`. El verificador de progreso del commit publicado aprobó `--check`:24 incrementos,24 verificaciones registradas y0 aceptaciones completas,48/72 (66,67%). Esto comprueba coherencia del registro, no vuelve a ejecutar la regresión funcional ni acredita producción.

**Hallazgo:** el directorio original `/workspace/SGA-CD` conserva modificaciones y archivos nuevos posteriores a `81dccf79c`, incluidos devoluciones, billetera y pruebas. No corresponde tratar ese trabajo como desaparecido ni reemplazar la recuperación publicada sin comparación. Antes de fetch o preparar la copia nueva, se respaldaron184 archivos existentes modificados/nuevos (59 son cachés `.pyc`, no184 funciones ni archivos de código nuevos), junto con diff binario, estado Git y manifiesto. Archivo privado `/workspace/recuperacion-original-sgacd-20261110T110746Z/archivos-locales.tar`, SHA256 de cada archivo cotejado contra el contenido del TAR. Permisos del directorio0700 y archivos0600; contiene configuración privada y no debe publicarse ni añadirse a Git. Sigue siendo un respaldo en el entorno, no una copia externa descargada.

Pendiente: comparar semánticamente los originales con el commit recuperado y con las siguientes entregas de Codespaces antes de integrar diferencias; no sobrescribir cambios del otro entorno ni publicar cachés o credenciales. La conexión es de esta conversación a GitHub mediante Git y su copia de trabajo gestionada; no es control directo del Codespace `glowing sniffle`. No se crearon commits ni se modificó main durante esta reconexión.


## Preservación consolidada de originales · 2026-11-10

Comparación real contra main remoto `db754af1630b99bd89c602b02c252ee16fe92835`:
124 archivos originales de fuente/evidencia, de los cuales 71 no estaban en el árbol
publicado, 52 diferían y uno coincidía. Se preservan íntegros, con sus rutas
canónicas dentro de `ANALISIS/entregas/evidencias/recuperacion-originales-20261110/originales.tar.gz`.
El manifiesto contiguo registra tamaño, SHA-256 individual y comparación contra
ese corte; todos los miembros fueron leídos y sus hashes comprobados. Se excluyen
bytecode/cachés, el archivo privado de credenciales Bold y el respaldo privado
previo. El directorio original de trabajo permanece intacto.

**Preservación no equivale a integración funcional.** Los originales no se
instalaron encima de los servicios de main: la comparación encontró contratos
incompatibles para las mismas operaciones y una colisión de migraciones wallet
0005. También hay motores alternativos de devolución/conciliación que requieren
controles cruzados antes de activarse, para no duplicar devoluciones, asientos o
consumo de líneas bancarias. La integración semántica, su regresión conjunta y
la activación de los formularios originales siguen pendientes. RAT, reservas y
ADR continúan diferidos. Los documentos dentro del paquete son instantáneas
históricas, no sustituyen este seguimiento vigente.

Los «44 archivos» del Codespace descritos anteriormente eran otro conjunto de
ZIP/respaldos locales. Esta sesión recuperó los originales de `/workspace/SGA-CD`;
no inspeccionó ese conjunto de 44 en la máquina Codespace y no afirma haberlo
publicado ni eliminado. No se deben confundir ambos inventarios.

Se incorpora directamente el recordatorio de elegibilidad personal universal de
billetera en AGENTS.md y la prueba de progreso original: detectó que main esperaba
46/72 aunque su registro ya contabilizaba 48/72. Ahora verifica 48/72 y conserva
una comprobación del corte anterior de 46/72 retirando únicamente los dos créditos
ACC-019. El porcentaje sigue siendo **66,67 %**, aceptación completa 0/24,
producción no habilitada. La preservación no acredita hitos adicionales.

Validación de esta preservación: hashes de los 124 miembros comprobados, búsqueda
de formatos de tokens sin coincidencias, `update_progress.py --check` correcto,
8 pruebas del registro aprobadas y `git diff --check` sin errores. No se ha
ejecutado ni se acredita aquí una nueva regresión funcional de los originales
archivados. El cierre de publicación se confirma comparando el SHA local y remoto.


## Integración funcional de originales · 2026-11-10

Esta sección actualiza el estado posterior a la preservación anterior: las
fuentes y formularios recuperados ya se incorporaron a las carpetas canónicas;
no se consideran integrados por estar dentro del TAR. Se compararon los 124
originales contra main f4c6220fa: 84 están presentes/restaurados con el mismo
contenido y 19 se integraron conservando compatibilidad. Nueve archivos de
ADR/hotelería permanecen diferidos por instrucción del usuario, once instantáneas
históricas de análisis se conservan en el paquete y la migración original 0005
queda cubierta por 0005_consent_refund_lifecycle ya publicada, sin duplicarla.
No se descartó ningún original. El inventario técnico detalla cada ruta.

Cambios incorporados: formularios compartidos de historia de compras, devoluciones
parciales, corrección de devoluciones y contrapartida final; agrupación bancaria
y abonos parciales; reporte ESG con corte histórico/exportación; políticas de
cancelación por anticipación y reembolso financiado a billetera con gestión de
vigencia. Se preservan los contratos de la recuperación publicada mediante
adaptadores y rutas compatibles. Las dos variantes de conciliación validan sus
reservas cruzadas; los protocolos alternativos de devolución de una misma compra
no se mezclan automáticamente. La liberación corporativa recuperada dispone de
alias explícito v2, conservando el contrato anterior.

La billetera mantiene acceso personal independiente del ERP. El consentimiento
confiable del beneficiario se vincula al resumen exacto; la renovación invalida
consentimiento/desafíos/autorizaciones anteriores y conserva la fecha económica
y política originales. Las rutas genéricas de transferencia no pueden cancelar,
renovar ni ejecutar un reembolso ligado al flujo contable. Se conserva la
configuración opt-in deshabilitada por defecto: no se activaron pagos bancarios,
retiros, DIAN, fondos reales ni servicios pagados. Las credenciales Bold se leen
del entorno o archivo privado existente; no se publican en fuentes ni evidencias.

Validación consolidada sobre fuentes estables: **1120 pruebas en 64 suites**,
**100 comprobaciones de navegador** en recorridos ERP/Analemática y gestión de
billetera, e instalación ERP-TUR desde SQLite vacío con comprobación de sistema
sin incidencias y migraciones wallet hasta 0005. Se corrigió una dependencia
local ausente de Playwright; la suite de firma repitió y aprobó 24 pruebas. El
puente corporativo aprobó 127 pruebas en 302 segundos en ejecución independiente;
el límite conjunto de 180 segundos fue insuficiente. La evidencia conserva ambos
intentos y sus resultados sustitutorios, sin sumar pruebas repetidas. El script
reproducible permite 600 segundos para ese puente. No se presenta como primer
intento íntegramente aprobado ni como validación productiva.

Evidencia única de esta integración:
`../entregas/evidencias/recuperacion-originales-20261110/verificacion.json`,
con inventario, hashes, resultados, límites y referencias a `pruebas.log`,
`fuentes-verificadas.json` y `verificar_integracion.py` en la misma carpeta.
El respaldo original anterior se conserva. Los documentos históricos no
sustituyen este seguimiento ni conceden créditos adicionales.

Los 44 ZIP/respaldos del Codespace siguen siendo un inventario distinto: la
consulta a la API de Codespaces devolvió Forbidden y no permite afirmar que se
inspeccionaron o publicaron. No se necesitan ni deben añadirse cachés/ZIP por su
contador para integrar las fuentes recuperadas. Cierre de publicación: un único
commit autorizado y push normal, verificando SHA remoto al finalizar.

**Avance sin inflación: 66,67 % (48/72), aceptación completa 0/24 y producción
no habilitada.** Permanecen la cualificación PostgreSQL/concurrencia, hardware,
identidad/proveedores, DIAN/Bold, revisión profesional y los demás criterios
externos registrados. Estos ensayos no acreditan un sistema terminado al 100 %.


## R12 · Períodos bancarios sin movimientos · 2026-11-10

Se implementaron revisión, segunda confirmación y recuperación de un período COP
que el titular declara sin movimientos, con saldos inicial/final explícitos y
huella del soporte. El lector CSV general sigue rechazando archivos sin filas:
el flujo nuevo no fabrica transacciones para eludirlo. Reutiliza la comprobación
de historia contable íntegra, apertura, cierre y cobertura; rechaza saldos
incompatibles y movimientos del libro, incluso si el neto bancario parece cero.
Los registros son metadatos de auditoría, no asientos ni pagos. Una fecha,
clasificación o fuente cambiada exige revisión; un asiento retroactivo invalida
la calificación actual conservando su confirmación histórica. La evidencia
append-only y una clave de solicitud impiden reintentos con otro contenido.

API ERP y contrato corporativo estricto conectados con un componente compartido
en los dos paneles. Controles separados para declarar/revisar/confirmar,
recuperación sin restaurar autorizaciones, edición que invalida la revisión,
descarte local, aislamiento empresarial y paleta azul/blanco conservados.
Durante el ensayo corporativo se detectó y corrigió una inserción de sintaxis
en la tabla de comandos; el recorrido completo posterior quedó aprobado.

Validación del incremento: 13 pruebas nuevas, 22 pruebas de regresión (14 de
períodos, 7 del lector CSV y 1 HTTP del puente bancario anterior), más 24
comprobaciones Chromium en ERP/Analemática. Registro añadido a
`../entregas/evidencias/recuperacion-originales-20261110/verificacion.json`
en `followups.empty_bank_period` y a su log existente. No se suman estos
conteos al corte histórico como si fueran una regresión completa nueva.

R12 continúa EN_EJECUCION: faltan cobertura de período agrupado, FX, snapshots y
volumen, fuente bancaria auténtica y revisión profesional. Los otros 19 hitos
conservan sus estados; esta entrega no los declara subsanados. Avance estable
**66,67 % (48/72), aceptación completa 0/24, producción no habilitada**.
Los cambios permanecen en el árbol de trabajo, sin commit parcial ni push nuevo.


## R12 y R03 · Períodos agrupados y devoluciones tributarias · 2026-11-10

R12: se añadió comprobación opcional de período para un lote de conciliación
agrupada. La revisión guarda saldos/fechas/soporte y cobertura del libro;
la segunda confirmación revalida esa fuente. Una asociación parcial no equivale
a cubrir toda su línea; movimientos omitidos compensados tampoco se ocultan por
un cierre neto coincidente. Se muestran por separado grupos confirmados y período
conciliado. Postear retroactivamente, cambiar clasificación o liberar la asociación
retira su calificación actual, conservando evidencia histórica. Los contratos
anteriores sin período siguen funcionando. Formularios ERP y Analemática incluyen
los términos, la calificación recuperada y bloqueo de edición tras confirmar.
No autentica al banco ni consolida períodos repartidos entre múltiples lotes.

R03: se detectó que el registro tributario enviaba los asientos proporcionales
recuperados al lector del otro protocolo de devolución y fallaba por origen
incompatible. Ahora selecciona su lector correcto y revalida prueba única,
compra nativa original, cadena de revisiones, proporción exacta sin fracciones
de centavo, líneas y recibo de posteo. Se atribuyen IVA descontable y retenciones,
con reducción de la compra original y sin sumar de nuevo el reintento. Ausencia
o alteración de pruebas/recibos exige revisión; nunca degrada a movimiento manual.
El reporte sigue siendo interno: no emite nota fiscal ni acredita DIAN.

Validación de este incremento: **21 pruebas nuevas y 93 regresiones**, 114 pruebas
en 10 suites, más **38 comprobaciones Chromium** en ambos paneles. Incluye una
consulta HTTP real corporativa de IVA/retenciones después de devolución y la API
ERP de registro tributario. No se suman al corte histórico como una regresión
completa del sistema. Evidencia añadida a la JSON/log existentes, sección
`followups.grouped_period_and_recovery_tax`, con hashes y comandos implícitos en
los nombres de suites/fuentes. No se ejecutaron acciones sobre cuentas reales.

Ambos hitos siguen EN_EJECUCION: quedan notas fiscales/DIAN, múltiples conceptos,
consolidación bancaria entre lotes, FX, grandes volúmenes/snapshots y aceptación
profesional/bancaria, además de los pendientes de los demás frentes. El porcentaje
se conserva en **66,67 % (48/72)**; aceptación completa 0/24. No se acredita
producción ni cierre de los 20 hitos por estos incrementos.

Directriz vigente del usuario: el siguiente commit consolidado ("Summit") se hará
cuando el avance verificable sea **superior al 70 %**. Con la base actual eso
requiere al menos 51/72 hitos (70,83 %). Hasta entonces se preservan cambios y
pruebas locales, sin commit ni push y sin alterar la ponderación para cruzarlo.


## R07/R08 · Confirmación BYOS incierta y acuse recuperable · 2026-11-10

Se corrigió el tratamiento del COMMIT en el almacén versionado del cliente: si
su confirmación se pierde, se descarta la conexión y se informa resultado
incierto, sin afirmar rollback ni generar otra versión. Un error de rollback o
limpieza no sustituye el error original; una limpieza fallida tampoco convierte
un COMMIT reconocido en fallo de almacenamiento. No se conectó ninguna base
productiva ni se guardaron KEK, contraseñas o documentos claros en el ERP.

La API independiente del cliente permite leer el acuse por empresa, documento,
versión y SHA-256 exactos. Revalida el grant y su permiso de lectura; devuelve
metadatos, nunca el documento ni la llave. Un 404 no autoriza a concluir que una
carga en curso fracasó; una huella distinta da conflicto. La comprobación de
bytes/huella no autentica el contenido cifrado, función reservada al cliente.

SDK y componente compartido ERP/Analemática conservan el paquete durante una
respuesta incierta y bloquean rotación, cambio del documento y recuperación de
otra versión. Permiten consultar su acuse sin volver a cargarlo y reintentar
explícitamente el mismo paquete. No hay reintento automático, token persistido
ni nueva versión implícita. La descarga cifrada existente debe conservarse para
recuperación tras recarga o cierre de sesión; el estado pendiente de pantalla
no es una autorización ni un registro persistente de custodia.

Validación del incremento: **13 pruebas nuevas y 15 de regresión**; **6 escenarios
PostgreSQL** (dos fallos de confirmación más cuatro de la regresión existente),
y **61 comprobaciones de navegador** (46 en paneles y 15 cliente HTTPS/PG).
El PostgreSQL 16 fue desechable, con rol restringido; se comprobó lectura fresca,
un único registro al reintentar, concurrencia, versiones históricas, revocación,
guardas y autenticación AEAD local. Los certificados fueron de laboratorio;
los fallos de transporte de panel fueron interceptados de prueba. No se acredita
propiedad de destino, confianza TLS ni custodia real. Durante la preparación se
corrigieron una espera prematura del servidor temporal de PostgreSQL y el alias
histórico de imports, confinado a la prueba; la ejecución final quedó aprobada.

Evidencia añadida a la JSON/log existentes, sección
`followups.byos_uncertain_commit_recovery`, con fuentes, hashes y comandos.
R07 y R08 pasan de PENDIENTE a EN_EJECUCION en la matriz de trabajo. El resumen de
estados se recalculó desde esa matriz, corrigiendo su discrepancia previa con
el texto; estos estados no equivalen a hitos ponderados aceptados.

Avance original: **66,67 % (48/72), aceptación completa 0/24**, producción no
habilitada. Continúan los pendientes de infraestructura/identidad del cliente,
TLS/grants reales, retención, custodia, hardware y los demás frentes del plan.
Se respeta el umbral de commit estrictamente superior al 70 %: no se hizo commit
ni push y no se modificaron las ponderaciones para cruzarlo.


## R04 · Borrador UBL conectado a revisión comercial · 2026-11-10

Problema: el borrador estructural permitía volver a escribir importes sin enlazarlos con la revisión comercial. Se añadió una consulta autenticada y transaccional de la última revisión de la reserva, con cotejo de huella, empresa, titular y política persistida. Cambios de importe/estado, revisión antigua, vínculo revocado y acceso ajeno bloquean la consulta. No crea eventos, facturas ni asientos.

Solución: el puente de Analemática valida contrato, huella, conceptos y totales; el formulario compartido ERP/Analemática carga conceptos revisados y vuelve a consultar la fuente antes de generar. Las tasas siguen siendo declaradas y deben reproducir exactamente el impuesto revisado; no se deducen tasas a partir de cocientes. El XML local incluye referencia a reserva/revisión/huella. Una unidad representa un concepto revisado, no habitaciones, pasajeros ni cantidades operativas. Se admiten COP y hasta 50 conceptos en este generador. Los cambios de identidad o formulario descartan artefactos; un error al regenerar no conserva un borrador anterior habilitado para cifrar. Se mantiene azul metalizado, azul claro y texto blanco.

Pruebas: 10 casos nuevos de backend/HTTP (9 ORM/API/contrato y 1 recorrido autenticado corporativo), 12 regresiones de revisión fiscal, 26 comprobaciones Chromium de SDK/formulario con fuente sintética y 38 de recorrido/cifrado en los dos paneles con servidores locales. Otras 46 comprobaciones de regresión BYOS pasaron en ambos paneles, conservando bloqueo y recuperación de cargas inciertas. Estas últimas incluyen cargar revisión por HTTP, conservar importes, insertar origen en XML y volver al modo manual. No son aceptación DIAN ni prueba con datos legítimos. Comandos, hashes y logs en la evidencia existente, clave `followups.reviewed_ubl_commercial_source`.

Pendientes: perfil y anexo DIAN vigentes, identidad/resolución/numeración legítimas, notas/anticipos, representación fiscal PDF/A-3, firma/custodia y acuses auténticos. La fuente es vigente al consultarla; no se asegura su vigencia futura ni autenticidad fiscal externa. R04 pasa de pendiente a en ejecución; no acredita alcance completo ni suma hitos a ACC-009, ya acreditada parcialmente. Avance: 48/72 = 66,67 %, aceptación completa 0/24 y producción deshabilitada. Sin commit ni push por el umbral superior al 70 %.


## R11 · Valoración inicial FX revisada y contabilizada · 2026-11-10

Problema: la contabilización extranjera existente seleccionaba una tasa global sin presentar su fuente y versión en una revisión explícita del titular. Se conservó ese comportamiento histórico para los borradores no sometidos al flujo nuevo y se añadió un camino separado de valoración inicial revisada. No se reescribieron asientos anteriores ni se alteró el catálogo global de tasas.

Implementación funcional: catálogo de borradores propios USD/EUR con base COP, veinte registros por página, selección y recuperación del estado desde los paneles ERP/Analemática. El titular declara tasa exacta con seis decimales, dirección de conversión, referencia y versión de fuente, fecha de observación con zona, vigencia y huella de soporte. La versión queda fijada por empresa/fuente/par; reutilizarla con otra tasa, vigencia o soporte exige nueva versión. No se invierte la tasa ni se consulta una tasa global como sustituto en este flujo.

La vista previa convierte cada línea con HALF_UP y exige débito/crédito COP exactamente iguales; no crea cuentas puente ni ajustes de redondeo inventados. Una reserva del borrador impide posteo genérico mientras existe revisión pendiente, incluso al cambiar su moneda o desaparecer la evidencia. La segunda confirmación usa la última revisión del mismo titular; cambios de origen, periodo cerrado, monedas/cuentas inactivas o fuente/versión alterada bloquean la operación. Tasa, importes base, asiento, auditoría, outbox y prueba de origen comparten la transacción; un fallo de evidencia revierte el posteo y conserva la reserva pendiente. Recuperar/reintentar no duplica y no restaura autorizaciones.

La contrapartida conserva moneda, tasa e importes originales y se verifica sin consultar una cotización nueva. El estado distingue un original con contrapartida de un asiento activo. Perder la evidencia del origen bloquea posteo repetido y reversión. Los permisos empresariales se revalidan en API y el puente corporativo coteja los importes y contratos antes de presentar éxito.

Verificación: 20 casos ORM del flujo y 6 API/contrato/catálogo nuevos; 26 regresiones de posteo y 26 del verificador de calidad. Chromium completó 30 comprobaciones entre ambos paneles, con HTTP/cookies/CSRF reales sobre datos desechables: catálogo, dos confirmaciones, recuperación, efecto único, inclusión de 40.000,00 COP de conversión en el balance, adaptación a 390 px y texto blanco. Capturas locales inspeccionadas en `/tmp/sgacd-reviewed-fx-erp.png` y `/tmp/sgacd-reviewed-fx-corporate.png`. Comandos, hashes y logs en la evidencia consolidada, clave `followups.reviewed_fx_initial_posting`. Las nuevas suites quedan registradas en el verificador canónico junto a la prueba de fuente UBL del incremento anterior. Otras 38 comprobaciones Chromium de regresión UBL/cifrado pasaron en ambos paneles después de incorporar FX.

Límites: es valoración inicial de borradores existentes, hasta cien líneas, no revaluación de saldos, liquidación bancaria ni cálculo completo de diferencias realizadas. Tasas y soportes son declarados y no se certifican como oficiales. Faltan PostgreSQL/concurrencia de este flujo nuevo, fuente FX autorizada, saldos/soportes legítimos, lotes históricos y aceptación profesional/productiva. No se modificaron RAT, reservas operativas ni ADR.

R11 pasa de pendiente a en ejecución. El plan restante conserva 2 verificados localmente, 10 en ejecución y 8 pendientes, sin cierre integral. ACC-006 ya tenía incremento y prueba acreditados: esta ampliación no añade un tercer hito de aceptación completa. Avance sin cambios: 48/72 = 66,67 %, aceptación completa 0/24, producción deshabilitada. Los cambios siguen locales y se conservan en el respaldo acumulado; sin commit ni push por el umbral superior al 70 %.


## R11 · Revaluación monetaria desde el libro y ajuste incremental · 2026-11-10

Problema: convertir un borrador extranjero no actualizaba el valor contable de la posición monetaria conservada. Se añadió revaluación acotada de cuentas dedicadas USD/EUR con base COP, clasificación monetaria declarada por el titular y cuentas explícitas de ganancia/pérdida. El catálogo se limita a cien cuentas por grupo y señala truncamiento. No se modifican saldos iniciales ni se deduce una moneda para un legado sin soporte.

Origen y cálculo: reconstruye hasta cincuenta movimientos contabilizados, valida hash v2, importe/base/tasa históricos y evidencia de las valoraciones iniciales revisadas. Admite ajustes COP anteriores únicamente con origen/recibo/prueba de revaluación íntegros y contrapartidas neutrales verificadas. Rechaza COP ajeno, monedas mezcladas, saldo inicial sin dimensión de divisa, saldo extranjero agotado, consumos/liquidaciones parciales sin conciliación de diferencia realizada y ajustes retroactivos después de una revaluación posterior. Es un incremento acotado, no un motor de liquidación de posiciones.

El valor objetivo es saldo extranjero por tasa declarada, redondeado HALF_UP; el asiento registra exclusivamente objetivo menos valor contable actual. Un activo que sube reconoce crédito en ganancia; un pasivo que aumenta su valor absoluto reconoce débito en pérdida. La segunda valoración incluye el ajuste anterior y evita duplicar gastos/ingresos. Un resultado cero no genera asiento. No consulta ni sustituye automáticamente la fuente de tasa revisada.

Controles: dos confirmaciones explícitas del mismo titular autenticado; huella del origen fija la revisión. Nuevos movimientos, cuenta/período inválidos o evidencia cambiada impiden contabilizar una revisión antigua. Asiento COP, recibo, auditoría, outbox y prueba se confirman o revierten en la misma transacción. La pérdida de prueba bloquea recuperación, posteo genérico repetido y contrapartida. La recuperación conserva la historia y distingue fuente actual de histórica, sin restaurar autorizaciones. La interfaz usa una clave de solicitud estable al reintentar una revisión sin cambiar sus campos.

Entrega funcional: catálogo, revisión, confirmación y recuperación por API empresarial y puente corporativo; formulario compartido disponible en Analemática y ERP turístico con azul metalizado, acentos azul claro, texto blanco y vista de 390 px. No hay pagos, movimientos bancarios ni reconocimiento fiscal automático. La clasificación monetaria, tasas y soportes siguen declarados y no certificados.

Verificación de este incremento: 22 pruebas nuevas (18 de núcleo y 4 API/contrato), 78 regresiones (20 valoración inicial, 6 API inicial, 26 posteo y 26 verificador), 30 comprobaciones Chromium con HTTP/cookies/CSRF reales en ambos paneles. Ejemplo sintético ejecutado: posición de 10 USD registrada por 40.000 COP; primera tasa 4.200 genera ajuste de 2.000 COP; tasa posterior 4.300 registra solo 1.000 COP adicionales. El balance final incluyó el efecto y permaneció cuadrado. Capturas en `/tmp/sgacd-fx-revaluation-erp.png` y `/tmp/sgacd-fx-revaluation-corporate.png`; la advertencia textual posterior sobre consumos parciales pasó comprobación sintáctica, sin otro cambio de comportamiento.

PostgreSQL16 real, creado solo para la prueba y eliminado al terminar: tres escenarios aprobados. Dos confirmaciones concurrentes de la misma revisión devuelven un asiento/recibo/prueba únicos; dos revisiones competidoras solo permiten un ajuste; un fallo de prueba revierte el posteo y permite reintento de efecto único. Se comprobó integridad del libro. Usa esquema/rol administrador de laboratorio: no acredita migración completa, roles mínimos/RLS, carga, restauración o infraestructura productiva. No se tocaron bases del proyecto ni se usaron fuentes bancarias/FX reales.

Evidencia y comandos en el JSON y log existentes, clave `followups.monetary_fx_revaluation`; suites incorporadas al verificador canónico. Pendientes R11: conciliación de consumos/liquidaciones y diferencia realizada, lotes/legados reales, fuentes y clasificación profesionales, escenarios operativos amplios y cualificación productiva. RAT/reservas/ADR permanecen fuera del cambio.

Avance acreditado: 48/72 = 66,67 %, aceptación completa 0/24, producción deshabilitada. El plan mantiene 2 hitos verificados localmente, 10 en ejecución y 8 pendientes; ninguno se presenta como cierre integral. ACC-006 ya tenía dos hitos: ampliar su código/pruebas no acredita su aceptación completa. Cambios conservados localmente y respaldados sin commit ni push, conforme al umbral superior al 70 %.


## R03/R18 · Compras de varios conceptos y recuperación fiel · 2026-11-10

Hallazgo: el motor aceptaba varias partidas, pero el formulario compartido solo permitía una. Además, recuperar la compra no reconstruía su selección de conceptos/cuentas/políticas desde la revisión persistida. Se amplió el formulario existente de Analemática y ERP, conservando navegación, azul metalizado/azul claro y texto blanco.

Implementación: hasta veinte conceptos, con importe neto, cuenta de gasto/activo, categoría y versión de política por concepto; cuenta por pagar compartida. Admite códigos/cuentas tributarios adicionales, hasta veinte códigos por concepto según los límites del contrato. No se deducen tasas ni deducibilidad. Una suma distinta al subtotal, códigos duplicados o fracciones de centavo impiden revisar. Se conserva el límite existente de 8192 bytes: un desglose demasiado extenso se bloquea antes de enviarse y requiere lotes todavía pendientes; no se presenta el producto veinte por veinte como una capacidad garantizada ni se envían partes de una revisión.

Recuperación: la API entrega selección, cuentas y revisión tomadas de la evidencia persistida, sin archivos ni autorizaciones. Se preservan UUID de conceptos, políticas y todos los mapas tributarios; la comparación del cliente no depende del orden de claves JSON. Una cuenta histórica fuera de la página cargada se muestra por referencia para consulta, no se inventa su nombre ni se acredita vigencia. Tras contabilizar los conceptos quedan de consulta. Cambiar, añadir o quitar datos descarta las confirmaciones locales. La vista previa muestra categorías en español, porcentajes y detalle de cada tributo.

Frontera corporativa: el contrato coteja empresa, entradas solicitadas/restituidas, identidades, políticas, bases, redondeo de componentes, cuentas, lados contables y totales. Rechaza un resultado que cambie partidas, atributos o valores. La fuente institucional y fiscal sigue sin aceptación independiente. El posteo y la contrapartida usan el motor existente; no hubo reescritura contable ni cambio de migraciones.

Verificado en ambos paneles mediante HTTP/cookies/CSRF y SQLite desechable: compra sintética de 60,00 COP gravados y 40,00 excluidos produce IVA 11,40, retención 1,50 y cuenta por pagar 109,90. Recuperar antes/después del posteo y recargar conserva ambos conceptos sin restaurar permisos. La contrapartida completa conserva el original y compensa ambos tributos. Una segunda variante incorpora un tributo positivo adicional de 3,00 COP, conservando los tres códigos/cuentas al recuperar. El registro integral atribuye cada valor a su cuenta sin movimientos tributarios sin atribuir en esos casos.

Las devoluciones parciales por concepto de una compra múltiple siguen pendientes: la interfaz lo indica y bloquea esos controles, y el backend conserva el rechazo del protocolo no soportado. No se fuerza una devolución proporcional global ni se emite una nota DIAN. La devolución previa de un concepto y su recuperación continúan verificadas.

Pruebas: 11 nuevas de núcleo/API/contrato; 94 regresiones (35 compras nativas, 18 devoluciones, 26 verificador y 15 contratos/HTTP corporativo). Navegador: 62 comprobaciones del escenario mixto y 70 del escenario con tributo adicional/orden de claves, entre ambos paneles; 12 comprobaciones solo DOM de límites/limpieza, que no acreditan autenticación o posteo; 38 y 28 comprobaciones de regresión de compra/devolución de un concepto. Son recorridos parcialmente comunes: no se suman como hitos distintos ni como porcentaje de cobertura. Azul/blanco y vista móvil de 390 px comprobados. Capturas locales `/tmp/sgacd-purchase-concepts-erp.png` y `/tmp/sgacd-purchase-concepts-corporate.png`; un ajuste posterior solo de etiquetas en español/porcentajes pasó comprobación sintáctica.

Evidencia, comandos y hashes en el JSON/log existentes, clave `followups.native_purchase_multiconcepts`. Nueva suite incorporada al verificador canónico. Pendientes: devolución por concepto, notas fiscales, atribución integral de ajustes, lotes extensos, datos/reglas revisados profesionalmente, migraciones/concurrencia/carga y aceptación productiva. No se modificaron RAT, reservas operativas ni ADR.

Avance acreditado sin cambios: 48/72 = 66,67 %, aceptación completa 0/24, producción deshabilitada. R03/R18 permanecen en ejecución; ampliar ACC-014, ya acreditada parcialmente, no concede el hito de aceptación completa. El plan conserva 2 verificados localmente, 10 en ejecución y 8 pendientes, sin cierre integral. Cambios preservados localmente y respaldados, sin commit ni push antes de superar el 70 %.


## R03/R18 · Devoluciones por concepto y corrección trazable · 2026-11-10

Se resolvió el pendiente de devoluciones parciales para compras nativas de dos a veinte conceptos. Cada devolución selecciona netos explícitos y limita su capacidad por partida. IVA y retenciones se prorratean acumulativamente desde cada componente del asiento original, conservando cuentas y redondeo al centavo; no se infieren tasas actuales ni se distribuyen impuestos del concepto gravado al excluido. Se bloquean fracciones, conceptos repetidos/desconocidos, exceso de neto y exceso de cuenta por pagar por redondeo. Se conserva el flujo anterior de un concepto.

Revisión y posteo requieren dos confirmaciones separadas. El asiento, la prueba y la reserva de soporte se guardan atómicamente; un fallo revierte todo y el reintento no duplica asientos. La recuperación revalida historial, fuente, recibos, componentes y huellas; nunca devuelve autorizaciones. Fuentes pagadas o cambiadas bloquean nuevos posteos. Las correcciones se hacen sobre la última devolución activa, con motivo, soporte, revisión y segunda confirmación; conservan ambos asientos y restituyen solo las partidas afectadas. La huella del soporte consumido no se libera. No se permite contrapartida global con devoluciones activas ni elusión por reversión genérica. Límites explícitos: treinta devoluciones y treinta correcciones por compra; ampliación y lotes siguen pendientes.

El registro tributario integral atribuye devolución y corrección a sus componentes originales. En ambos paneles se verificó por HTTP/cookies/CSRF una compra de 60 COP gravados y40 excluidos: devolver30 del primero reduce IVA5,70 y retención0,75, deja40 disponibles del excluido y30 del gravado; corregir restituye IVA11,40 y retención1,50. La contrapartida completa posterior compensa los tributos sin borrar originales. Interfaz azul/blanco, control de capacidad, soporte solo hash local, recuperación sin autorizaciones y vista móvil390px comprobados.

Pruebas y hashes están en los JSON/log existentes, clave followups.purchase_item_returns:20 pruebas nuevas (16 núcleo y4 API/contrato), regresiones de compras/devoluciones/contrapartidas/registro tributario y recorrido Chromium de ambos sistemas. Los conteos exactos constan en la evidencia automática; los recorridos comparten comprobaciones y no se suman como cobertura ni hitos adicionales. No se ejecutó dinero ni se emitió nota fiscal.

Este corte sustituye el pendiente de devolución por concepto de los apartados anteriores para compras múltiples nativas. Permanecen notas fiscales/DIAN, aceptación profesional de políticas y soportes, conciliación con documentos externos, PostgreSQL/concurrencia/carga y producción. R03/R18 continúan en ejecución. Avance48/72=66,67%, aceptación completa0/24. Sin commit ni push mientras no se supere70%; sin modificaciones a RAT/ADR.


## R03/R18/R19 · Concurrencia PostgreSQL y descarga de historial · 2026-11-10

Bloqueo abordado: las devoluciones por concepto solo estaban verificadas con SQLite y recorridos HTTP secuenciales. Se añadió un ejecutor explícito y reproducible para PostgreSQL16 desechable, restringido a127.0.0.1 y un nombre de base de laboratorio, sin utilizar DATABASE_URL del proyecto ni descargar imágenes durante la prueba. Arranca el contenedor con almacenamiento temporal, genera una contraseña efímera en archivo privado, crea el esquema acotado y elimina el contenedor al terminar, incluso ante un error. Los fallos guardan diagnóstico privado sin imprimir credenciales.

Las conexiones de ejecución, incluidas las de hilos competidores, usan un rol de laboratorio sin superusuario, BYPASSRLS, creación de roles/bases ni DDL. Se concede solo uso de esquema/secuencias y SELECT/INSERT/UPDATE; no DELETE. Se comprueba que CREATE TABLE sea rechazado. La creación inicial del esquema sí usa su propietario desechable. Esto no acredita RLS instalada ni cualificación de roles productivos.

Seis escenarios aprobados: misma revisión simultánea produce un único asiento con un reintento reconocido; dos devoluciones competidoras solo permiten una; misma corrección simultánea produce una contrapartida; dos revisiones de corrección solo permiten una; devolución y contrapartida total competidoras no dejan ambos efectos activos; fallo de escritura de prueba revierte asiento y reserva y permite un reintento único. Se revalida estado y cadena contable tras cada carrera. No se afirma cobertura de todos los aislamientos, carga, fallos de red, migraciones históricas ni infraestructura productiva.

Función nueva compartida en Analemática y ERP: «Descargar historial de devoluciones por concepto». Exporta el último estado observado, con partidas, saldos, devoluciones, correcciones, referencias de asientos y huellas de evidencia. Incluye fecha de captura, SHA-256 calculado sobre UTF-8 de JSON.stringify(snapshot), codificación explícita y límites de autenticidad. No contiene soportes, credenciales, firmas de autorización ni una nota fiscal. Cambiar de fuente, limpiar sesión o perder visibilidad invalida la descarga pendiente. El archivo puede quedarse obsoleto después del corte y se declara expresamente.

Verificación Chromium:82 comprobaciones entre ambos paneles, incluida descarga real, reconstrucción independiente del SHA-256, historial con corrección, ausencia de contenido del soporte y banderas sin autorización/documento fiscal. Incluye regresión del recorrido de compra/devolución/corrección/contrapartida y azul/blanco a390px; son escenarios compartidos, no82 funciones nuevas. Evidencia y comandos en los JSON/log existentes, clave followups.purchase_returns_postgres_and_export.

Estado: se reduce la incertidumbre de concurrencia de este flujo concreto. R03/R18/R19 siguen en ejecución; continúan pendientes notas DIAN, autenticidad/revisión profesional, cualificación integral de bases y producción. Avance48/72=66,67%, aceptación completa0/24. Sin commit/push antes de superar70%. No se modificaron RAT/ADR ni se ejecutaron pagos.


## R12/R19 · Historia bancaria por lotes con integridad · 2026-11-10

Hallazgo subsanado: la evaluación de períodos cargaba todas las líneas de caja y rechazaba más de2000 históricas. Verificaba cada asiento mediante una consulta individual de sus contrapartidas. Se sustituyó esa lectura por paginación keyset de128 líneas y grupos de16 asientos, bajo transacción/bloqueo de empresa, sin caché persistente de confianza. La consulta de contrapartidas conserva un máximo de16384 filas por grupo; cada asiento conserva el contrato de2 a1000 líneas. El límite histórico ahora es20000 líneas; la20001 se rechaza antes de devolver un resultado parcial. Se mantiene el límite de200 movimientos dentro del período y los límites de CSV/importación existentes.

Se reconstruye el hash de cada asiento completo, incluidas las líneas ajenas a caja; se comprueba pertenencia de línea, cuenta y catálogo contable a la empresa. La aritmética y el orden UUID del digestv1 permanecen iguales: revisiones previas conservan su formato, sin migración ni reconstrucción de aprobaciones. Cambiar importes, metadatos de cuentas, contrapartidas o pertenencia del catálogo invalida la evaluación. Un tamaño de lote distinto produce el mismo resultado; los límites no silencian omisiones. No se borran saldos ni se crean ajustes para cuadrar.

El contrato corporativo también limitaba historia a2000: se actualizó a20000 y se añadió el rechazo de conteos de período superiores a la historia verificada. No se amplía la declaración de autenticidad: el banco y sus fuentes siguen sin verificación independiente.

Verificación:14 pruebas nuevas del núcleo y2 del contrato corporativo; regresiones de período, período vacío, agrupación, asignación parcial, recuperación, contratos y verificador canónico. Se comprobó exactamente20000 líneas y rechazo de20001. Medición sintética SQLite:20000 líneas en10,611 segundos en la última ejecución; corresponde a auditoría histórica, no al objetivo de250ms del posteo transaccional ni a una cualificación de producción. El caso de129 líneas del iterador requiere como máximo12 consultas, conservando la verificación completa. El costo total sigue siendo lineal y requiere snapshots cualificados para mayor escala.

En ambos paneles,40 comprobaciones Chromium sobre HTTP/cookies/CSRF y ORM reales verifican un período con2003 líneas históricas, apertura2001,00 y cierre2016,00, agrupación de15,00, recuperación sin autorizaciones, liberación y conservación del libro. Identidad azul/blanco y móvil390px conservados. Los históricos masivos son fixtures sintéticos insertados para comprobar lectura: no acreditan origen de asientos, migraciones históricas, autenticidad bancaria ni aceptación global de cadena. Evidencia, comandos y hashes en los JSON/log existentes, clave followups.bank_history_streaming. Nueva suite incorporada al verificador canónico.

Pendientes: snapshots históricos cualificados, volúmenes/concurrencia en PostgreSQL objetivo, FX bancario, aceptación de extractos y revisión profesional, además de los pendientes fiscales y otros frentes del plan. R12/R19 continúan en ejecución. Avance48/72=66,67%, aceptación completa0/24. Sin commit/push antes de superar70%; sin cambios en RAT/ADR, pagos ni billetera.


## R10/R18 · Deducciones fijas por trabajador, asiento y formulario · 2026-11-10

Función nueva: la nómina revisada de Analemática y ERP permite habilitar «Incluir deducciones fijas por pagar». Cada trabajador declara el importe en COP y las huellas de soporte y autorización. El formulario ofrece una deducción de importe fijo por trabajador; el contrato del núcleo admite hasta ocho códigos explícitos por política/trabajador. Las reglas se versionan sin redefinir una versión registrada. No se afirma que una huella pruebe legalidad, consentimiento legítimo o aplicabilidad; se conserva authorization_independently_verified=false.

El motor conserva salario y bases de aportes/provisiones. Suma la deducción fija a las porcentuales, reduce únicamente el neto y acredita su importe en la cuenta de deducciones por pagar existente. Exige importe positivo al incluir un concepto, dos decimales exactos, código único conocido y ambas huellas; rechaza flotantes, fracciones de centavo, duplicados y neto negativo. Una lista vacía declara que el trabajador no tiene deducciones fijas en esa política. No infiere topes legales ni cancela anticipos/deudas históricas: es una obligación por pagar declarada que requiere revisión laboral profesional.

La revisión persiste por trabajador el desglose fijo, el porcentaje calculado y las referencias, además de totales agregados. El posteo reconstruye esos insumos antes de causar, mantiene las dos confirmaciones, guarda detalle/cabecera/asiento/evidencia atómicamente y conserva el mismo asiento al reintentar. Una falla de escritura del detalle revierte la causación. La recuperación coteja importes proyectados y no restaura autorizaciones. Los bloqueos existentes ante novedades, ausencias e incapacidades siguen vigentes; no se omiten esos registros para activar esta función.

El puente corporativo coteja por separado códigos, trabajador/contrato/días, importes y huellas solicitados, falsa declaración de autorización independiente, componentes porcentuales, neto por persona y totales. Una respuesta que cambie estos elementos se rechaza. El formulario muestra el desglose y sus referencias en ambas plataformas; editar descarta las confirmaciones, y la pérdida de sesión limpia datos privados. Azul/blanco y móvil390px conservados.

Ejemplo sintético completo ejecutado en ambos paneles por HTTP: salario base500,00 + horas extra12,50 + recargo1,75 = devengado514,25 COP. Deducción porcentual20,57 + fija25,00 =45,57; neto468,68. Aportes61,71 y provisiones41,14 permanecen iguales; el costo laboral617,10 sigue disponible para distribución operativa sin crear otro gasto ni un pago. La prueba base sin suplementos verifica directamente el crédito45,00 en deducciones por pagar y neto455,00. No se usaron trabajadores, autorizaciones o cuentas bancarias reales.

Validación:11 nuevas pruebas del núcleo/API/contrato,109 regresiones de nómina, suplementos, costos, frontera y verificador;44 comprobaciones Chromium entre los dos paneles, incluyendo causación, reintento/recuperación, deducción con soporte/autorización, costos sin reducción indebida y limpieza de sesión. Capturas locales de la interfaz final: /tmp/sgacd-fixed-deductions-erp.png y /tmp/sgacd-fixed-deductions-corporate.png. Comandos, hashes y resultados en el JSON/log existentes, clave followups.declared_fixed_payroll_deductions. Suite incorporada al verificador canónico.

Pendientes concretos: catálogo ampliado de deducciones en interfaz, habilitación/consentimiento y topes legales revisados profesionalmente, integración de novedades/ausencias/incapacidades/viáticos, nómina electrónica DIAN, migraciones/concurrencia PostgreSQL y aceptación productiva. No se ejecutaron pagos, descuentos bancarios, retiros ni transferencias de billetera. R10/R18 siguen en ejecución. Avance acreditado48/72=66,67%, aceptación completa0/24, sin publicación Git antes de superar70%. RAT/ADR permanecen fuera del cambio.


## R10/R18 · Novedad registrada → nómina → asiento → consumo único · 2026-11-10

Bloqueo resuelto para un subtipo concreto: antes cualquier NovedadNomina existente impedía la causación. Ahora se pueden seleccionar en ambos paneles las deducciones fijas registradas, sin volver a escribir su importe. La política debe declarar expresamente FIXED_LIABILITY_FROM_SOURCE; no se mezcla con deducciones manuales. Se admiten hasta ocho por trabajador, únicamente concepto DEduccion, cantidad1, valor positivo, fecha dentro del período, perteneciente al trabajador de la empresa y sin procesar. Las asignadas a otra planilla, fuentes desconocidas/repetidas, otras cantidades/tipos y fechas incompletas o ajenas al período se rechazan. No se infiere la naturaleza legal de un concepto por su descripción.

La selección debe cubrir todas las novedades pendientes del trabajador para esta planilla o aún sin asignar; no se omiten filas silenciosamente. También se impide omitir novedades asignadas a la planilla al seleccionar sus trabajadores. Cada fuente se fija por ID, trabajador, planilla de origen, fecha, concepto, cantidad, importe y hash de descripción; el texto privado no se devuelve al navegador. Se declaran huellas de soporte y autorización con verificación independiente=false. El catálogo se limita a100 novedades de la empresa y declara truncamiento.

El importe de origen se incorpora a deducciones por pagar y al neto, conservando devengados, aportes y provisiones. La revisión no consume la fuente. Tras la segunda confirmación, planilla, detalle, asiento, marca procesada, asignación de la fuente y prueba de consumo se guardan en la misma transacción. El reintento reconoce el asiento existente; no causa de nuevo. Si la escritura de la prueba falla, fuente y asiento vuelven al estado anterior y se permite reintentar. La recuperación comprueba fuente y prueba; un cambio, borrado, reinicio artificial de procesada o prueba ausente exige conciliación, sin reconstrucción automática de aprobaciones ni orígenes.

El formulario añade «Incluir deducciones desde novedades registradas» y selección múltiple por trabajador, con soporte/autorización. Muestra los importes de la fuente, no los solicita de nuevo. La frontera corporativa coteja selección solicitada, identidades, fechas, cantidad, fuente/huella, clasificación declarada, deducciones y netos. Al cambiar datos se descartan confirmaciones; sesión y fuentes siguen acotadas a la empresa. Se preservan las dos confirmaciones, identidad azul/blanco y móvil390px.

Recorrido completo ejecutado con datos sintéticos en Analemática y ERP: novedad registrada25,00, base500,00 y suplementos14,25; deducciones porcentuales20,57 más novedad25,00 producen neto468,68. La fuente queda procesada y vinculada a la planilla, desaparece del catálogo pendiente y se recupera el mismo asiento. El costo laboral617,10 sigue disponible para distribución, sin gasto adicional ni pago. No se usaron autorizaciones, empleados o movimientos bancarios reales.

Pruebas:18 nuevas de núcleo/API/contrato,120 regresiones;50 comprobaciones del recorrido nuevo entre ambos paneles y72 de regresión de interfaz base/manual. PostgreSQL16 desechable con rol restringido: misma revisión concurrente produce un solo asiento, planillas competidoras no consumen dos veces la fuente y un fallo de la prueba de consumo revierte fuente/asiento antes del reintento. Permisos DDL denegados en runtime; el esquema inicial usa propietario de laboratorio. No acredita migraciones históricas, RLS/permisos/carga productivos ni aceptación profesional. Resultados, comandos, hashes y capturas canónicas panel-erp.png/panel-analematica.png en la carpeta de evidencia existente, clave followups.reviewed_payroll_novelties. No se abrió otro informe narrativo.

Pendientes: devengados/otros tipos de novedad, ausencias, incapacidades, viáticos, topes/aplicabilidad y consentimiento legítimo revisados profesionalmente; corrección controlada de fuentes consumidas; nómina DIAN y cualificación productiva. Las fuentes consumidas que se alteren requieren conciliación y se rechazan, no se declaran reparadas. R10/R18 continúan en ejecución.

Avance acreditado48/72=66,67%, aceptación completa0/24. La matriz ya otorga incremento y prueba a las24 tareas; ampliar esos incrementos no da crédito adicional. El tercio restante requiere aceptación completa, con funcionalidades y validaciones externas aún pendientes. No se cambió el denominador para aumentar el porcentaje ni se realizó commit/push antes de superar70%. RAT/ADR y pagos permanecen fuera del cambio.


## R10/R18 · Bonificación y comisión registradas → devengado → asiento → costo · 2026-11-10

Bloqueo subsanado para dos tipos de devengado: el modo anterior solo admitía deducciones y rechazaba cualquier DEVENGADO existente. Se añadió COMPENSATION_FROM_SOURCE conservando el modo previo y sus revisiones. El administrador debe clasificar cada concepto explícitamente como bonificación o comisión; no se infiere de su código o descripción. Fuentes con cantidad diferente de1, importes no positivos, fechas ajenas al período, duplicados, omisiones y conceptos no clasificados siguen bloqueadas.

Cada regla porcentual exige base BASE o GROSS incluso cuando no hay horas extra. Los importes registrados se suman al devengado y se proyectan a DetalleLiquidacion.bonificaciones/comisiones. El total actualizado alimenta aportes/provisiones solo conforme a la base declarada, la deducción porcentual, el neto, las líneas contables y la fuente de costo operativo. Horas extra y recargos conservan sus cálculos y campos propios, sin sumarlos dos veces. Se mantienen las dos confirmaciones y la transacción común de fuente/planilla/detalle/asiento/prueba. Un fallo durante el segundo consumo revierte las tres fuentes y el asiento completo. No hubo migración ni reescritura de revisiones históricas.

En ambos paneles se añadió «Incluir bonificaciones y comisiones registradas», selección de fuentes y clasificación por concepto. Una clasificación ausente o contradictoria entre trabajadores bloquea la revisión. Cambiarla elimina confirmaciones. Los importes se toman del registro; el formulario no solicita reintroducirlos. Se conservan empresa/contrato/período, la privacidad de la descripción de origen, azul/blanco y móvil390px. La revisión muestra bonificación, comisión y deducción con sus referencias; horas extra/recargo se presentan en español. El catálogo expone el ID de concepto necesario para declarar su clasificación.

La frontera corporativa coteja política normalizada solicitada, conceptos/campos elegidos, fuentes y huellas, proyección de bonificaciones/comisiones, devengado, cada componente porcentual con su base/tasa/redondeo, pasivos y neto. Rechaza cambios en clasificación, bases, importes o fuentes. Los límites siguen acotados:8 fuentes por trabajador,8 clasificaciones por política y10 trabajadores, sujetos a8192 bytes por solicitud y32768 por evento canónico; no se garantiza el producto10x8 ni se envían fragmentos de una causación.

Ejemplos reales del laboratorio: base500 + bonificación50 + comisión30 = devengado580 COP; con deducción porcentual23,20 y fuente de deducción25, neto531,80, aportes69,60 y provisiones46,40. El detalle conserva bonificación50/comisión30 y el gasto salarial contabiliza580. Con las mismas fuentes más horas extra12,50/recargo1,75, ambos paneles produjeron devengado594,25, deducciones48,77, neto545,48, aportes71,31 y provisiones47,54. El costo laboral713,10 se distribuyó dejando356,55 sin asignar en el caso de capacidad parcial, sin nuevo gasto ni pago. Con base de aportes BASE explícita, el ejemplo sin suplementos mantiene aportes60 y neto535: es una declaración aritmética, no aceptación legal de esa base.

Validación:11 pruebas nuevas núcleo/API/contrato y138 regresiones;56 comprobaciones del escenario mixto en ambos paneles y94 de regresión de interfaces de deducción registrada/manual. PostgreSQL16 desechable y rol restringido: misma revisión y planillas competidoras conservan un solo asiento y tres consumos; fallo del segundo claim revierte todo antes de reintentar. Esquema de laboratorio, sin aceptación de migraciones históricas, permisos/RLS/carga productivos ni guardas operativas PostgreSQL. Capturas panel-devengados-erp.png y panel-devengados-analematica.png en la carpeta de evidencias existente; se conservan las capturas previas. Comandos, resultados y hashes en los JSON/log existentes, clave followups.registered_source_earnings. Nueva suite en el verificador canónico.

Pendientes: otros devengados y novedades, ausencias/incapacidades/viáticos, creación/corrección controlada de fuentes en el panel revisado, topes y clasificación/bases legales con revisión profesional, nómina electrónica DIAN y cualificación productiva. Consentimiento y soportes siguen declarados, no autenticados por estos fixtures. R10/R18 permanecen en ejecución. Avance48/72=66,67%, aceptación completa0/24. No se concede crédito adicional por ampliar una tarea parcialmente acreditada; sin commit/push antes de superar70%. Sin cambios en RAT/ADR, billetera, cuentas reales o pagos.


## R10/R18 · Captura desde panel y recuperación del registro · 2026-11-10

Bloqueo resuelto: los recorridos previos necesitaban NovedadNomina precargadas. Ahora ambos paneles incluyen «Registrar novedad de nómina»: trabajador, concepto existente, fecha, importe fijo, referencia única, soporte, autorización y confirmación de captura. Requiere trabajador activo de la empresa seleccionada y planilla BORRADOR; no crea empleados/contratos/planillas/conceptos globales ni contabiliza al capturar. Emplea cantidad1. El catálogo existente de conceptos se consulta con límite100 y truncamiento explícito.

Los dos archivos se leen y se resumen localmente, con máximo2MiB cada uno; el contenido y el nombre no se envían. El ERP conserva huellas, dato de origen y autor, no certifica autenticidad/consentimiento ni deposita automáticamente originales en BYOS. El cliente debe conservarlos en su custodia documental. La referencia exacta, sensible a mayúsculas/minúsculas, se persiste resumida y es única por empresa. El mismo request devuelve el registro original; el mismo identificador con datos distintos o la misma referencia con otro request se rechazan. Fuente, captura, vínculo e índice se guardan atómicamente: una falla revierte también la novedad, sin registros huérfanos.

«Consultar novedad por referencia» recupera un resultado incierto sin volver a crear ni restaurar autorizaciones. Mientras la respuesta de registro sea incierta, se bloquean edición, cambio/carga de planilla y nuevas revisiones/posteos de esa nómina; se habilita la consulta. Si se acredita referencia inexistente, el usuario puede revisar y confirmar de nuevo. Si faltan pruebas o el índice, se exige conciliación y no se reconstruye historia. Al cambiar de planilla se descarta la confirmación de captura; sesión/visibilidad descartan datos locales. Controles nuevos con altura mínima44px y estilo azul/blanco; móvil390px verificado.

Las nuevas fuentes se enlazan al formulario de cálculo con sus huellas de soporte por registro. Reutilizar una referencia documental no restaura una autorización: revisión y posteo conservan sus dos confirmaciones. El motor coteja la fuente con su captura nativa antes de calcular y al recuperar el asiento. Cambios por otras rutas, referencias alteradas o pruebas eliminadas bloquean, sin adoptar la fuente como legado. Los registros anteriores sin captura nativa conservan su protocolo. No se introdujeron migraciones ni sustituciones destructivas de datos.

La frontera corporativa valida empresa/planilla, referencia resumida solicitada, fuente/huella, solicitud/empleado/concepto/importe/fecha y cualificación de lectura, replay y escritura de metadatos. Nunca presenta la captura como un asiento, envío documental o movimiento de dinero. API estricta rechaza campos de proceso o empresa inyectados. Se amplió el ejecutor PostgreSQL existente mediante --native-intake; esquema desechable, rol restringido sin DDL y sin acceso a bases del proyecto.

Verificado desde cero novedades precargadas en ambos paneles: crear deducción25, bonificación50 y comisión30 mediante archivos locales; perder deliberadamente la primera respuesta después del commit del servidor; consultar la referencia y recuperar un único registro; clasificar fuentes, revisar/contabilizar y distribuir costos. Devengado594,25, deducciones48,77, neto545,48 y costo713,10 en el ejemplo combinado con suplementos. Los registros se procesan una vez y se conserva el mismo asiento. Los cuerpos POST no contienen los bytes de los archivos. Son datos sintéticos, no autorizaciones o pagos reales.

Pruebas:15 nuevas núcleo/API/contrato,149 regresiones;68 comprobaciones del recorrido completo entre ambos paneles y100 de regresión de interfaces anteriores. PostgreSQL16: misma solicitud concurrente crea una sola fuente, distinta solicitud con referencia repetida permite una sola captura, falla del índice revierte y permite reintentar. No cualifica migración histórica, permisos/RLS/carga de producción ni aceptación fiscal/profesional. Capturas panel-captura-nomina-{erp,analematica}.png y sus cierres en la carpeta existente; se conservan imágenes anteriores. Comandos, hashes y resultados en el JSON/log existentes, clave followups.native_payroll_source_intake. Suite nueva en verificador canónico; AST, sintaxis JS y coherencia de progreso comprobados.

Pendientes concretos: corrección/retiro controlado de fuentes pendientes o consumidas; custodia automatizada de originales; duplicados semánticos y gobierno/versionamiento del catálogo compartido de conceptos; otras novedades, ausencias/incapacidades/viáticos, DIAN y aceptación profesional/productiva. El catálogo heredado permite cambios fuera de este flujo y debe auditarse; aquí no se agregan permisos globales de escritura y los cambios incompatibles en fuentes capturadas se detectan. Este corte sustituye únicamente el pendiente de captura de fuentes fijas ya soportadas, no el de corrección integral.

Avance acreditado48/72=66,67%, aceptación completa0/24. R10/R18 siguen en ejecución. Código conservado y respaldado localmente; sin commit/push antes de superar70%. No se modificaron RAT/ADR, billetera ni cuentas bancarias ni se ejecutaron pagos.


## R10/R18 · Corrección de novedades pendientes con historia y nuevo cálculo · 2026-11-10

Problema subsanado: después de capturar una fuente fija, un error de importe o fecha obligaba a detenerse; una edición directa rompía la evidencia. Se añadió «Preparar corrección de novedad» y «Guardar corrección de novedad» en los dos paneles existentes. Permite modificar fecha, importe y referencias documentales con motivo explícito, archivos locales y nueva confirmación. Conserva trabajador, concepto, planilla, referencia única y captura original. Solo admite fuente nativa no procesada en planilla BORRADOR sin asiento/orden de pago. No elimina registros, crea contrapartidas para fuentes contabilizadas ni introduce migraciones.

Cada corrección agrega autor, versión, motivo, antes/después, referencias y hash previo; se conserva la captura inicial. La consulta reconstruye la versión efectiva, coteja la fuente actual y verifica la proyección de cabecera. Revisiones ausentes, truncadas o incompatibles bloquean. Límite20 correcciones por fuente. La cabecera es una proyección actualizable; la cadena detecta incoherencias, no acredita almacenamiento externo inmutable, blockchain ni inmunidad frente a un administrador de base que reescriba coherentemente todos los datos y pruebas.

El bloqueo de empresa/planilla y la versión esperada impiden aceptar dos correcciones competidoras. La misma solicitud puede repetirse con los mismos datos sin agregar otra revisión; un reintento antiguo después de otra corrección exige consultar. Fuente, evento y cabecera comparten transacción: una falla en cualquier prueba revierte importe/fecha e historia. La API rechaza cambio de empleado/concepto/empresa o campos ajenos al contrato. El puente corporativo verifica identidad, alcance, historia, huella efectiva, versión y datos solicitados.

Cambiar importe, fecha o solo soportes invalida la revisión financiera previa en el servidor. El panel descarta revisión y confirmaciones, actualiza el catálogo y exige volver a revisar/autorizar el posteo. La consulta recupera la última versión sin restaurar aprobaciones. Durante resultado incierto se bloquean cambios y acciones financieras; se conserva consulta por referencia. El recorrido de navegador pierde deliberadamente la respuesta después de guardar una corrección, recupera la misma versión y no duplica. Las fuentes ya procesadas quedan protegidas en interfaz y servidor.

Recorrido comprobado en ERP y Analemática: capturar deducción25, bonificación50 y comisión30; corregir bonificación a60 manteniendo visible50 en historia; revisar/contabilizar con suplementos14,25. Resultado: devengado604,25; deducción porcentual24,17 más fuente25 =49,17; neto555,08; aportes72,51; provisiones48,34; costo725,10. Distribución parcial deja362,55 sin asignar. Recuperación conserva un solo asiento y las fuentes procesadas. Datos y archivos sintéticos; no se realizaron pagos ni transmisión DIAN. Se mantuvo azul/blanco y móvil390px sin desbordamiento.

Verificación:16 pruebas nuevas núcleo/API/contrato;164 regresiones (fuentes nativas, nómina, suplementos, deducciones, novedades, devengados, costos, frontera, runner y puente corporativo). Navegador:82 comprobaciones del nuevo recorrido entre ambos paneles y68 de regresión de captura. PostgreSQL16 desechable con rol restringido: repetición concurrente produce una sola revisión; solicitudes competidoras sobre versión0 aceptan una; falla de cabecera revierte fuente/historia antes de reintentar. No acredita migraciones históricas, permisos/RLS/carga productivos ni aceptación profesional. Capturas panel-correccion-nomina-{erp,analematica}.png y comandos/hashes en los JSON/log existentes, clave followups.native_payroll_source_correction. Se amplió el verificador canónico y el ejecutor PostgreSQL existente.

Pendientes sustituidos: corrección de importe/fecha/soportes de fuente nativa pendiente en borrador. Permanecen retiro, ajustes de fuentes consumidas o heredadas, gobierno/versionado del catálogo, custodia automatizada/autenticidad de originales, otras novedades, reglas laborales completas, DIAN y aceptación profesional/productiva. Los hashes de soporte y autorización siguen siendo referencias declaradas, nunca prueba independiente de legitimidad.

Avance acreditado48/72=66,67%, aceptación completa0/24. R10/R18 siguen en ejecución: esta ampliación mejora tareas ya acreditadas parcialmente y no concede otro hito. Código y pruebas locales en codex/conectado-20261110, pendientes de entrega consolidada conforme al umbral vigente superior70%; no se realizó commit/push. No se modificaron RAT/ADR, billetera ni cuentas reales.


## R12/R18 · Período bancario consolidado entre lotes y reporte descargable · 2026-11-10

Bloqueo subsanado: las asociaciones parciales ya conservaban capacidad entre lotes, pero la calificación del período seguía limitada a un solo lote. Se implementó bank_period_rollup sobre los servicios existentes, con catálogo, revisión, confirmación y recuperación. Reúne lotes agrupados v1 confirmados y activos de una misma cuenta COP; coteja cada prueba/claim, referencia bancaria única, identidad/hash del movimiento y asignación acumulada. Los importes originales, el libro y sus claims se conservan; no se crean ajustes, pagos ni liquidaciones de facturas.

Para revisar exige declaración explícita de extracto completo, fechas, saldo inicial/final y huella del soporte. La suma de asignaciones debe cubrir exactamente cada movimiento seleccionado; el conjunto debe cubrir todos los movimientos del libro en el período. Se cotejan entradas y salidas separadamente, apertura histórica y cierre. Movimientos omitidos que se compensan en neto tampoco califican. La apertura no se presume cero. El corte y la historia se validan con el servicio de período existente, incluyendo sus límites e integridad de contrapartidas. Fechas originales ajenas al período no se presentan como un ajuste de tránsito implícito.

La revisión guarda actor, versión, selección ordenada, huellas de origen y comparación. La segunda confirmación exige la revisión vigente del mismo titular y revalida fuentes, política, capacidad y libro bajo bloqueo de empresa. Repetir confirmación conserva una sola prueba. Cambiar o liberar un lote, revertir su asiento, alterar la política, perder un claim o agregar movimientos retroactivos invalida la calificación, conservando la confirmación histórica. Una falla de escritura revierte la prueba; no toca los lotes previos. Catálogo y estado son de lectura; no restauran autorizaciones. API estricta y contexto corporativo verifican empresa/cuenta, comparación y flags de no escritura/no autenticación.

Formulario compartido en los dos paneles, dentro de la agrupación bancaria existente: catálogo seleccionable, fechas/saldos/huella, declaración de integridad del extracto, dos confirmaciones y comparación visible entre banco/libro/asignaciones antes de confirmar. Cambiar datos invalida revisión y confirmaciones. Una respuesta de confirmación perdida se recupera por cuenta/período sin duplicar; mientras sea incierta se bloquea cambio de alcance. Un fallo de consulta retira la indicación de calificación vigente y exige recuperar; no deja visible una conciliación positiva obsoleta. Se conserva azul/blanco, controles nuevos44px y móvil390px sin desbordamiento.

«Descargar consolidación JSON» vuelve a consultar el estado y genera el archivo local con fecha de exportación, revisión, fuentes, comparación y calificación. Muestra SHA-256 de los bytes descargados. Incluye banco no autenticado y aprobaciones no restauradas. La huella comprueba consistencia del archivo, no legitimidad del banco. Cambio de sesión/descartar limpia datos y catálogo locales; no se envían archivos a un tercero. No se añadió otro informe narrativo.

Recorrido ejecutado en ERP y Analemática: tres lotes independientes6,4 y5; los dos primeros consumen el mismo movimiento original10 y el tercero otro movimiento5. El período pasa por apertura0, entradas15, salidas0 y cierre15, con3 filas bancarias y2 movimientos contables cubiertos. Se pierde intencionalmente la respuesta de confirmación después del commit de laboratorio y se recupera el mismo período, sin aprobaciones. El archivo descargado coincide con su SHA-256 mostrado. Al liberar el lote5, la recuperación muestra período no conciliado y fuente no vigente. Son fixtures sintéticos; no hubo fuente bancaria auténtica, pagos ni aceptación profesional.

Pruebas:19 nuevas núcleo/API/contrato,178 regresiones (123 bancarias,29 corporativas,26 del runner);44 comprobaciones nuevas en navegador y60 de regresión entre ambos paneles. Cubren saldos iniciales reales del libro de laboratorio, entradas/salidas, omisiones compensadas, alcance de otro usuario, falsos flags y preservación del ledger/claims. PostgreSQL16 desechable, rol sin superusuario/bypass RLS/DDL: confirmación concurrente idempotente, carrera confirmación/liberación con calificación final inválida y falla de prueba con recuperación. No cualifica producción. Capturas panel-consolidacion-bancaria-{erp,analematica}.png, comandos, hashes y logs en la carpeta existente y followups.consolidated_bank_period del JSON canónico. Se amplió el verificador existente; nuevo ejecutor PostgreSQL es una prueba técnica, no un análisis adicional.

Límites/pending: de1 a20 lotes,200 filas bancarias y200 movimientos por período; catálogo50 tras escanear como máximo1000 pruebas de empresa. Continúan el límite histórico20k y32KiB por cuerpo canónico: no se promete el producto de todos los máximos. Solo lotes agrupados v1 confirmados, una cuenta COP y períodos acotados; no convierte automáticamente conciliaciones antiguas/otros formatos. Siguen autenticidad/consentimiento de fuente, revisión profesional, FX/instrumentos y diferencias de tránsito, snapshots/archivo, migración histórica, roles/RLS/carga/latencia y conectores bancarios reales. No se habilitó producción ni se cambiaron RAT/ADR, nómina, billetera o cuentas reales.

Este corte sustituye el pendiente de consolidación interna entre lotes agrupados dentro de ese alcance; R12/R18 permanecen en ejecución. Avance48/72=66,67%, aceptación completa0/24. El incremento amplía una tarea ya acreditada parcialmente y no otorga otro hito; la autenticidad bancaria/profesional no se demuestra con laboratorio. Código y evidencias conservados en codex/conectado-20261110; sin commit/push antes del umbral vigente superior70%.


## R11/R18 · Liquidación parcial/total en divisa y diferencia realizada · 2026-11-11

Bloqueo resuelto dentro de un alcance explícito: la revaluación detectaba consumos pero los rechazaba porque no existía baja con diferencia realizada. El nuevo fx_settlement toma una cuenta monetaria dedicada USD/EUR y un abono/cargo COP ya contabilizado, con dos líneas de caja/cuenta puente. No ejecuta transferencias, vuelve a contabilizar caja, edita el asiento extranjero original ni modifica su tasa histórica. El movimiento debe ser íntegro, vigente, de la misma empresa/fecha y corresponder a una cuenta de caja previamente clasificada. Un activo recibe abono contra puente pasivo; un pasivo usa cargo contra puente activo. Cuentas, cantidad, clasificación, tasa y soportes son explícitos.

La baja proporcional usa el valor contable efectivo de la posición, incluidas revaluaciones previas, con Decimal/HALF_UP. El último consumo libera exactamente el resto para no dejar centavos ni cantidad residual. Caja registrada debe coincidir con cantidad por tasa declarada; no se infieren comisiones, diferencias de tránsito ni ajustes de redondeo. La ganancia se abona a ingreso y la pérdida se carga a gasto según activo/pasivo. Sin diferencia se generan solo las dos líneas necesarias; se normaliza cero y se rechaza -0,00. Las cantidades restantes se reconstruyen con registros extranjeros originales y deltas de liquidación/contrapartida verificados, sin reescribir el libro histórico.

Revisión y contabilización requieren dos confirmaciones del mismo titular personal. Se vinculan empresa, solicitud, posición, recibo previo, cuentas, fecha, tasa/versionado, soporte y período abierto. Fuente, asiento, receipt idempotente, prueba y claim de caja comparten transacción. Fallar el claim revierte todo el posteo. Una caja ya usada o un saldo cambiado requieren nueva revisión; solicitudes concurrentes no consumen dos veces. Faltantes o alteraciones de prueba/origen/claim bloquean sin reconstruir. El prefijo de liquidación queda reservado a su comando explícito; una ruta genérica no puede crear un asiento que simule ese origen.

La contrapartida conserva el original y restaura cantidad/valor. La caja solo queda disponible en un corte que ya incluya la contrapartida; no se libera retrospectivamente. Se rechaza un ajuste retroactivo anterior a otra liquidación, revaluación o contrapartida monetaria. No se permite revertir el abono/cargo mientras haya una liquidación FX activa. La revisión del efectivo también rechaza un recibo ya vinculado a reconocimiento de anticipo. En el validador de anticipo existente se añadió únicamente el bloqueo inverso de doble aplicación a FX, incluso si la cuenta puente contiene otros recibos; no se optimizaron reservas/RAT/ADR ni sus operaciones comerciales.

Ambos paneles tienen catálogo de fuentes, selección de cuenta monetaria y movimiento COP existente, puente, cantidad, tasa con soporte/vigencia/versionado, hash local del documento y dos confirmaciones. Los archivos (máximo2MiB) se leen/resumen localmente y no se envían; el cliente conserva sus originales. Editar datos invalida la revisión. Respuesta inicial perdida se recupera por el request estable; posteo incierto se recupera por revisión sin otro asiento ni autorizaciones restauradas. Mientras hay incertidumbre se bloquean ediciones de alcance. Recuperar una revisión exige volver a declarar clasificación y segunda autorización. Sesión/empresa/logout descartan el estado local; se preservan azul/blanco, foco nativo, botones44px y móvil390px. La consulta del libro se refresca tras confirmar. La tasa y el banco siguen no autenticados y fiscal_accepted=False.

Ejemplo ejecutado de activo:10USD a4000=40000COP; abono ya registrado17200COP por4USD a4300. Se debita puente17200, acredita monetaria16000 y gana1200; quedan6USD/24000COP. El balance de prueba refleja24000 en monetaria,17200 de caja original y puente0, con débitos/créditos iguales. Si hubo revaluación a4200, se libera16800 y la diferencia desde ese valor es400; el resto6USD/25200 puede revaluarse después a4250 con ajuste300. El pasivo probado da baja4 de10USD con cargo17200, pérdida1200 y saldo-6USD/-24000COP; una segunda liquidación sin diferencia no crea ingreso/gasto ficticio. Otra prueba liquida3,33+3,33+3,34 de una posición de40001,23COP y libera exactamente40001,23, cerrando cantidad y valor en cero. Son datos sintéticos y asientos reales de laboratorio, nunca pagos o soportes bancarios auténticos.

Verificación:30 pruebas nuevas (25 núcleo,5 API/contrato),203 regresiones (177 contables y26 del runner);36 comprobaciones nuevas del recorrido HTTP en ambos paneles y30 de regresión de revaluación. Incluye pérdida deliberada de ambas respuestas tras el commit del servidor, saldo restante, hash del asiento de caja original intacto, ausencia de bytes documentales en POST y borrado de sesión. PostgreSQL16 desechable con rol sin superusuario/bypass RLS/DDL: misma revisión concurrente produce un asiento; revisiones competidoras de la misma caja aceptan una; dos recibos que intentarían consumir14 de10USD no sobreconsumen; falla de claim revierte asiento/receipt/prueba antes de reintentar. No acredita permisos/RLS/carga, migraciones históricas ni infraestructura productiva. AST/sintaxis y coherencia de progreso verificados. Capturas panel-liquidacion-divisas-{erp,analematica}.png, comandos/hashes/logs en la carpeta existente y followups.reviewed_fx_settlement del JSON canónico.

Límites/pending: USD/EUR/COP, cuentas monetarias dedicadas, cantidad de dos decimales, un movimiento COP completo por liquidación y dos líneas simples en su origen, misma fecha de caja/liquidación, hasta50 líneas monetarias y1000 asientos de liquidación por empresa. Catálogo100 candidatos de caja/50 resultados elegibles y100 cuentas por grupo, sujeto al límite32KiB del evento; no se promete el producto de los máximos. Sin migración de esquema. Quedan cargos/comisiones, división de un movimiento entre posiciones, diferencias de tránsito y otros consumos, legados/lotes/snapshots, formatos bancarios adicionales, fuentes auténticas/tasas y clasificación profesionales, gobernanza tributaria, rendimiento250ms/carga/roles y aceptación productiva. No se acreditan Next.js completo ni dispositivos nativos por estos recorridos. No se tocaron billetera ni cuentas reales ni se transmitió a DIAN.

Este incremento sustituye el pendiente de liquidación parcial/total y diferencia realizada solo en ese alcance. R11/R18 continúan en ejecución; avance48/72=66,67%, aceptación completa0/24. Ampliar una tarea parcialmente acreditada no otorga otro hito. Código y evidencias siguen locales en codex/conectado-20261110 y respaldados; no se hizo commit/push antes del umbral acordado superior70%.


## R11/R18 · Apertura ampliada preservada y fecha comercial · 2026-11-11

Problema subsanado: la apertura anterior quedaba limitada a100 cuentas. Se implementó apertura de primer libro COP de2 a250 cuentas de balance activas, preservando saldos originales y sin inventar una cuenta de cuadre. Cinco páginas de50 vinculan manifiesto, revisiones y hashes; el navegador consulta y verifica todas antes de habilitar revisión. Un único asiento equilibrado conserva todas las líneas. Dos confirmaciones separadas, mismo titular/empresa/período abierto, control de revisión vigente y reserva de namespace. Fuente cambiada, chunk faltante, prueba alterada, libro ya iniciado o251 cuentas bloquean sin reconstruir evidencias ni modificar saldos originales. La apertura anterior sigue operativa; un candidato antiguo no elude una revisión ampliada más reciente.

Ambos paneles incorporan formulario, tabla paginada desplegable, fecha contable del servidor, hash local del soporte (no se envían bytes), recuperación tras respuesta perdida y limpieza por sesión/empresa. Recuperar no restaura autorizaciones. Se conserva azul/blanco y navegación a390px. Recorrido real de laboratorio:250 cuentas y un asiento de250 líneas por224COP en cada lado; reportes conciliados y fuente preservada. No son saldos auténticos ni aceptación productiva.

Verificación actual: 252 pruebas automatizadas aprobadas en los logs de esta entrega (20 de apertura y regresiones, incluida política de cancelación),38 comprobaciones nuevas de navegador y52 de regresión;4 escenarios PostgreSQL16 desechable con rol restringido. PostgreSQL comprueba replay concurrente, revisiones competidoras, rollback completo de asiento/receipt/auditoría si falla prueba y rollback de manifiesto/chunks si falla fuente. Se corrigió una consulta adicional que rompía el presupuesto de rendimiento existente y se volvió a aprobar la regresión. Además, las23 pruebas de reembolso detectaron comparación errónea del día UTC contra vigencia comercial local: se usa ahora timezone.localdate del consentimiento; prueba específica de00:30UTC=19:30Colombia del día anterior y regresión de reembolsos aprobadas. No se alteran porcentajes comerciales ni se ejecutan pagos.

Se actualizaron únicamente las descripciones límite obsoletas de ACC-001/004/006/015 y los pendientes descriptivos del registro, reflejando pruebas PostgreSQL, FX y banco ya disponibles; permanecen iguales IDs, alcance, ponderaciones y créditos. Avance48/72=66,67%, aceptación completa0/24. R11/R18 siguen en ejecución: falta migración de libros existentes/descuadrados, lotes mayores, soportes legítimos, cualificación de carga/roles, revisión profesional y producción. No se acredita Next.js completo, Flet físico ni integración DIAN/bancaria auténtica.

Evidencia/capturas/logs/hashes en la carpeta existente, followups.chunked_preserved_opening de verificacion.json. Consulta remota de solo lectura confirma main9ada277ab4224ea7205cef0230e782385b149d93; esta entrega sigue local y respaldada, sin commit/push/merge. No se inventa porcentaje para superar el umbral de publicación superior70% indicado por el usuario.


## Entrega Git consolidada autorizada · 2026-11-11

El usuario autorizó expresamente integrar el acumulado actual mediante un único commit y actualizar main, como excepción al umbral superior70%. Se conserva48/72=66,67%, aceptación completa0/24 y producción deshabilitada. Se verifican respaldo, diferencias, coherencia y avance normal del remoto antes de publicar; no se usa force ni se descarta trabajo externo. El SHA definitivo se confirma contra refs/heads/main después del push.


## R14/R18 · Exportación ESG comprobada y mapeos múltiples · 2026-11-11

Problema: el formulario existente solo declaraba un límite por consulta y exportabaJSON sin comprobar en el navegador la huella completa, la correspondencia del ámbito ni el producto y total decimal. Se amplió el mismo componente compartido, conservando estructura/colores azul metalizado, claro y blanco. Ahora permite agregar hasta los tres límites existentes sin sobrescribir una declaración previa; mantiene los límites sin observaciones separados de los valores medidos. El soporte de cada mapeo se resume localmente conSHA256 (1byte..2MiB); sus bytes nunca forman parte delPOST. Cambiar datos invalida resultados y descargas; descarte, pérdida de sesión y ocultamiento limpian el estado privado. Botones mínimos44px y390px sin desborde comprobados.

Antes de mostrar o descargar, se verifican período/corte/mapeos solicitados, empresa/proveedor, flags de no certificación/no pago/no obligación, UUIDs y fuentes, hash canónico completo, límites de200 actividades/512KiB, duplicados por identificador, producto cantidad por factor y totales por frontera usandoBigInt con decimales exactos y redondeo a seis lugares. Un hash recalculado no convierte un importe o ámbito alterado en aceptable. Esto comprueba consistencia; no autentica las fuentes ambientales ni equivale aZKP o certificación.

CSV descargable conUTF-8, campos entrecomillados y protección frente a fórmulas; cada actividad conserva empresa/prestador, período/corte, hash del reporte, observación, revisión efectiva, cantidad/unidad/factor, kgCO2e, fuentes/prueba y marco/soporte declarado. Incluye explícitamente estadoBORRADOR_NO_CERTIFICADO y flagsFalse. Un período vacío exporta una filaSIN_MEDICIONES con ámbito y digest, sin inventar actividad, medición cero ni cobertura. JSON sigue disponible.

Verificación:44 comprobaciones de navegador en las pantallas reales ERP y Analemática, sobreHTTP/CSRF/cookies/ORM desechables; incluye corrección12.345600->24.691200 sin doble cómputo, dos fronteras mapeadas sin inventar mediciones, soporte local no transmitido, CSV y JSON trazables, vacío explícito y rechazo de tres respuestas alteradas (digest inválido; importe con digest recalculado; fechas con digest recalculado).25 regresiones aprobadas:12 reporte,7 recuperación/correcciones/API y6 contrato corporativo. Capturas panel-exportacion-esg-{erp,analematica}.png y logs/comandos/hashes en la evidencia existente, followups.esg_multi_boundary_verified_csv.

Pendientes: duplicados semánticos que requieren criterio de dominio; soporte/factor legítimo, marco y aplicabilidad revisados profesionalmente; snapshots para superar200 observaciones/actividades, carga, compilación Next.js completa y aceptación nativa/productiva. No se crearon pasivos, créditos, pagos ni integraciones nuevas con proveedores. Sin cambios de esquema niRAT/ADR/reservas. Avance48/72=66,67%, aceptación integral0/24: no se añade crédito a una tarea ya parcialmente acreditada. Este incremento está local sobre el commit publicadoee5280429; no se ha creado otro commit/push. La excepción de publicación anterior fue para una sola entrega.


## R12/R18 · Lotes bancarios posteriores al50 accesibles · 2026-11-11

**Implementado y probado.** El catálogo anterior devolvía solo50 lotes y los demás no podían seleccionarse en los paneles. Ahora consulta páginas de50, con cursor ligado a empresa/cuenta y huella del catálogo completo; conserva el límite existente de1000 confirmaciones por empresa. El servidor rechaza cursor incompleto, desconocido, que no termine una página completa o que intente continuar tras el final. Una liberación que cambie el catálogo invalida la continuación: exige recargar desde el principio. El contrato corporativo valida ámbito, continuación, orden, duplicados, límites y huella si la respuesta ya es completa.

El mismo formulario de ambos sistemas ofrece cargar la siguiente página, conserva selecciones y muestra cantidad cargada/total e integridad pendiente/completa. Solo habilita la revisión cuando se consultaron todas las páginas y elSHA256 canónico acumulado coincide. No conserva autorizaciones al ampliar la consulta. Un error de página borra todas las elecciones antiguas e impide usar un catálogo parcial como si fuera completo. No se modifica el libro ni se mueven saldos/dinero. Código compatible con las rutas existentes, sin migraciones.

Pruebas:20 de núcleo/API/contrato (incluida una nueva prueba integral de53 lotes),12 de período agrupado,17 de agrupación y29 bancarias corporativas:78 aprobadas;26 del runner aparte.24 comprobaciones nuevas de navegador (55 lotes sintéticos confirmados en cada base desechable, páginas50+5, últimos lotes seleccionables, selección preservada, huella completa, datos antiguos eliminados ante respuesta alterada y descarte) y44 de regresión del flujo de consolidación completo en ambas pantallas. La regresión confirma que tres lotes6+4+5 siguen conciliando dos movimientos por15COP, con dos autorizaciones, recuperación, exportación y posterior pérdida de vigencia por liberación. Se verificaron azul/blanco y390px sin desborde. Capturas panel-catalogo-bancario-paginado-{erp,analematica}.png, comandos/logs/hashes en la evidencia existente, followups.paged_bank_rollup_catalog.

**Alcance pendiente de desarrollo.** No se ampliaron los máximos de20 lotes seleccionados/200 filas bancarias/200 movimientos por consolidación ni el alcanceCOP. Falta snapshots/escalado y medición de carga; no se acredita rendimiento250ms. Preparar55 lotes mediante110 escrituras HTTP corporativas alcanzó el límite de solicitudes del backend (429); no se deshabilitó. La prueba final prepara sus55 confirmaciones mediante el motor real en ORM desechable antes de abrirHTTP, y prueba la navegación HTTP con cuotas vigentes. Hallazgo adicional pendiente: el puente transforma el429 de consulta previa en503 genérico; mejorar su presentación y espera segura sin aumentar cuotas ni reintentar pagos automáticamente.

**Requisitos externos.** Extractos y soportes bancarios auténticos, consentimiento/permisos si se conectaAPI, revisión contable profesional e infraestructura objetivo para cualificación. Los55 lotes de prueba no acreditan autenticidad bancaria ni aceptación productiva. R12/R18 siguen en ejecución. Avance histórico48/72=66,67%, aceptación integral0/24, sin crédito adicional por esta ampliación. Desde esta entrega las novedades se presentan con estas tres categorías explícitas; no se equipara código probado parcialmente a sistema completado. Base publicadaee5280429; este incremento y el anteriorESG permanecen locales, documentados y respaldados, sin otro commit/push.


## Directriz vigente · Cierre secuencialACC-001 aACC-024

El usuario exige cerrar cada tarea al100% antes de pasar a la siguiente. Esta regla sustituye la ejecución alternada de frentes; no cambia el alcance original ni convierte incrementos parciales en aceptación completa. Conservar el trabajo previo de todas las tareas. Los20 hitos remanentes son acciones dependientes dentro de las24 tareas originales, no un segundo denominador de avance.

Única tarea activa: **ACC-001 · Validación monetaria exacta y aislamiento de cuentas**. Estado: abierta, aceptación integral pendiente. No iniciarACC-002 hasta documentar evidencia de todos sus criterios y acreditar full_acceptance deACC-001. Una dependencia compartida puede modificarse exclusivamente si es necesaria para cerrar la tarea activa, con regresión del comportamiento afectado; eso no inicia ni cierra otra tarea.

| Orden | ID | Tarea | Estado secuencial |
|---|---|---|---|
| 1 | ACC-001 | Validación monetaria exacta y aislamiento de cuentas | CERRADA · 100% de sus criterios originales |
| 2 | ACC-002 | UUID de alta y guardas de asientos/líneas | CERRADA · 100% de sus criterios originales |
| 3 | ACC-003 | Idempotencia y outbox en una transacción | CERRADA · 100% de sus criterios originales |
| 4 | ACC-004 | Periodos, concurrencia y contrapartidas | CERRADA · 100% de sus criterios originales |
| 5 | ACC-005 | Puente TourismProvider a Tenant y actor verificables | CERRADA · 100% de sus criterios originales |
| 6 | ACC-006 | Monedas, FX y valoración | CERRADA · 100% de sus criterios originales |
| 7 | ACC-007 | Hash canónico versionado y controles SQL | CERRADA · 100% de sus criterios originales |
| 8 | ACC-008 | Contrato CRM y reserva hacia facturación | CERRADA · 100% de sus criterios originales |
| 9 | ACC-009 | XML, representación y firma fiscal | EN EJECUCIÓN · requiere habilitación/custodia/acuses reales |
| 10 | ACC-010 | Envelope encryption cliente y recuperación | CERRADA · 100% de sus criterios originales |
| 11 | ACC-011 | Conectores BYOS y OAuth mínimos | EN EJECUCIÓN · conectores locales; permisos cloud reales pendientes |
| 12 | ACC-012 | Órdenes, novedades y controles SG-SST | EN EJECUCIÓN · riesgo específico añadido; aceptación integral pendiente |
| 13 | ACC-013 | Reglas de nómina, costos y provisiones | EN ESPERA · conservar implementación previa |
| 14 | ACC-014 | Impuestos y conciliación continua | EN ESPERA · conservar implementación previa |
| 15 | ACC-015 | Legacy bridge y open banking | EN ESPERA · conservar implementación previa |
| 16 | ACC-016 | Proyecciones y ratios turísticos | EN ESPERA · conservar implementación previa |
| 17 | ACC-017 | Monte Carlo y recomendaciones | EN ESPERA · conservar implementación previa |
| 18 | ACC-018 | Factores de carbono y ledger ambiental | EN ESPERA · conservar implementación previa |
| 19 | ACC-019 | Reportes ESG y marcos aplicables | EN ESPERA · conservar implementación previa |
| 20 | ACC-020 | Consultas NLP de solo lectura | EN ESPERA · conservar implementación previa |
| 21 | ACC-021 | RPA financiera con autorizaciones | EN ESPERA · conservar implementación previa |
| 22 | ACC-022 | Offline cifrado y conflictos | EN ESPERA · conservar implementación previa |
| 23 | ACC-023 | Benchmark250ms y precisión IA | EN ESPERA · conservar implementación previa |
| 24 | ACC-024 | Recuperación, seguridad y despliegue | EN ESPERA · conservar implementación previa |

Criterios de cierre deACC-001 conservados de la matriz: importes finitos sin float ni redondeo silencioso; balance exacto; rechazo de cuentas ajenas o inactivas; rechazo de períodos ambiguos. Se debe comprobar su cumplimiento en los puntos de entrada de ambos sistemas, documentar las rutas y pruebas reproducibles, y resolver cualquier fallo encontrado. No exigir certificadosDIAN ni bancos para estos criterios si no son necesarios; no añadir requisitos artificiales ni eliminar criterios para cerrar. El estado actual de código y pruebas históricas no sustituye esta revisión integral del alcance.

Cada cierre tendrá tres apartados:1)funcionalidad implementada y probada con evidencia;2)alcance de desarrollo pendiente (debe quedar vacío para cerrar);3)requisitos externos del criterio original (resueltos o justificados como no aplicables, nunca asumidos). Si hay bloqueo externo, la tarea sigue activa y no se salta a la siguiente. El porcentaje histórico permanece48/72=66,67%, aceptación integral0/24; esta decisión de organización no otorga crédito ni implica un nuevo commit/push.


## Cierre secuencial · ACC-001 al100% · 2026-11-11

**Funcionalidad implementada y probada.** Se revisaron los criterios originales de la filaACC-001 sin reducir alcance ni añadir requisitos de otras tareas. Se corrigieron dos fallos: la precisión/redondeo/trampas Decimal del llamante podía afectar operaciones y sumas; un período abierto superpuesto creado después del borrador no se rechazaba al contabilizar. Se fija un contexto decimal interno de50 dígitos, suficiente para importes y agregados acotados del motor, restaurando el contexto del llamante. La unicidad del período abierto y su identidad se revalidan al postear. El replay de un asiento ya contabilizado conserva su efecto histórico aunque el período haya cerrado; no es un nuevo posteo. Además, se rechazan aliases monetarios contradictorios y amount_transaction fraccionario/float antes de que DecimalField pueda redondearlo.

Aceptación por criterio:1)finite/no float/no silent rounding: casosNaN/Infinity/bool/float/negativos/subcentavo/desbordamiento y contexto hostil;2)balance exacto: diferencia de un centavo no desaparece al bajar precisión, eventos/manuales conservan1000000.01 por lado;3)cuenta ajena: cuenta y plan extranjeros rechazados antes de crear efectos;4)inactiva: se reconsulta al crear y al postear un borrador;5)período ambiguo: rechazo tanto al crear como al contabilizar después de introducir superposición. Pruebas de fallo comparan cabeceras/líneas/receipts/auditoría/outbox y preservan ausencia de efectos. Ambos backendsHTTP autenticados rechazan importes inválidos sin persistir factura; el flujo válido de compra produce balances idénticos134.00/134.00. Las rutas financieras activas de ambos sistemas convergen en este motor; no se declara operativo código de presentación antiguo desconectado.

Verificación:10 pruebas específicas nuevas de aceptación y3HTTP nuevas; regresiones26 de posteo,46 adaptador,20 apertura,25 liquidaciónFX,23 reembolso y35 compras, todas aprobadas. Son188 ejecuciones de pruebas entre ocho suites, no188 criterios nuevos ni cobertura100%. Además26 del runner;38 comprobaciones de navegador preservan los recorridos de apertura250 cuentas en ambos paneles. PostgreSQL16 desechable con rol sin superusuario/bypassRLS/DDL comprueba seis escenarios del criterio monetario/aislamiento/período, incluida reversión transaccional de intentos inválidos y replay histórico. No se certifican grants/RLS/migraciones/carga de producción por estos tests. Comandos/tests/logs/hashes y matriz explícita de los cinco criterios en followups.ACC001_full_acceptance del JSON canónico existente.

**Alcance pendiente deACC-001:** ninguno de sus criterios originales. **Requisitos externos deACC-001:** ninguno: estos criterios no requieren un banco, certificadoDIAN ni dictamen tributario. No se usa esta conclusión para cerrarFX, impuestos, concurrencia, inmutabilidadSQL o producción, que tienen tareas propias. Los datos financieros de laboratorio son sintéticos; los motores, bases yHTTP son ejecutables reales.

**Estado:ACC-001 CERRADA al100%.** Se acredita exclusivamente el tercer hito deACC-001. La base48/72=66,67%,0/24 aceptadas se conserva como corte anterior en la evidencia y las pruebas del generador. Resultado nuevo49/72=68,06%,1/24 tareas cerradas (4,17% de cierres integrales), producción deshabilitada. El generador deja de afirmar que ninguna tarea está aceptada y sus pruebas conservan el corte histórico sin alterar el denominador72. ACC-002 es la siguiente en la secuencia; no se ha iniciado su desarrollo en esta entrega. Cambios locales y respaldados, sin commit/push nuevo.


## Cierre secuencial · ACC-002 al100% · 2026-11-11

**Funcionalidad implementada y probada.** Se conservaron exactamente los criterios originales: crearUUID nuevo sinDoesNotExist y rechazar cambiosORM sobre contabilizados incluso con padre cacheado. Se sustituyó el atributo reutilizable_validated_post por un permiso temporalContextVar ligado a empresa yUUID, abierto solo durante elsave validado del motor y retirado al finalizar o fallar. Un atributo colocado en un objeto ya no autoriza una cabecera nueva contabilizada. No es una frontera de seguridad contra códigoPython privilegiado: sigue siendo un invariante interno, con permisos y guardasSQL separados.

Las instancias cargadas o ya guardadas recuerdan suUUID y rechazan reasignarlo; altas de instancias nuevas y cargas con campos diferidos siguen funcionando. Las guardas vuelven a leer el padre del libro en la base: guardar/borrar líneas o agregar otra línea bajo un padre cacheado como borrador se rechaza si ya fue contabilizado. Cabeceras contabilizadas rechazan save normal, update_fields, force_update, force_insert, desmarcado ydelete. OperacionesQuerySet/bulk que omiten elsave se comprueban contra los triggers existentes del esquema migrado (0005/0006); no se reconstruyen ni eliminan registros históricos.

Verificación:8 pruebas nuevas de aceptación; regresiones26 posteo,14 guardasSQL,10ACC-001,46 adaptador,20 apertura,4HTTP de compras/recuperación/devoluciones/contrapartidas en ambos sistemas,25FX y23 reembolsos:176 ejecuciones de pruebas funcionales/regresión aprobadas.26 del runner aparte. PostgreSQL16 desechable con rol sin superusuario/bypassRLS/DDL y con permisosDML comprueba cinco escenarios: altaUUID, cabecera/padre cacheados, atributo falsificado, operaciones masivas/delete bloqueadas por triggers y posteo/replay/contrapartida normal con hash original intacto. SQLite también verifica las operaciones masivas. Las pruebas del permiso temporal incluyen retirada al fallar y aislamiento en otro hilo. No se modificó interfaz ni se presenta un nuevo recorrido visual; la aceptaciónHTTP ejecuta los flujos existentes. Logs/comandos ejecutables/tests/hashes y criterios explícitos en followups.ACC002_full_acceptance del JSON canónico existente.

**Alcance pendiente deACC-002:** ninguno de sus criterios originales. **Requisitos externos deACC-002:** ninguno para la implementación y aceptación funcional. Precondición de operación: esquema migrado con guardasSQL instalado; lo verifican estas pruebas y las herramientas de salud existentes. No se afirma haber inspeccionado o cualificado una base productiva. PropietariosSQL capaces de desactivar triggers, roles/RLS/otras tablas y despliegue completo mantienen sus tareasACC-007/024; no se cierran como efecto secundario deACC-002. Sin migraciones nuevas ni cambio de datos.

**Estado:ACC-002 CERRADA al100%.** ACC-001 conserva su aceptación y pasó nuevamente sus diez pruebas. Solo se añade el tercer hito deACC-002:50/72=69,44%,2/24 tareas cerradas (8,33% de cierres integrales), producción deshabilitada. El corte49/72=68,06%,1/24 se preserva en evidencia y en pruebas del generador junto al corte anterior48/72. ACC-003 es la siguiente; no se desarrolló en esta entrega. Cambios locales respaldados, sin otro commit/push.


## Cierre secuencial · ACC-003 al100% · 2026-11-11

**Funcionalidad implementada y probada.** Se mantienen los criterios originales: duplicado sin duplicar asiento, contenido distinto rechazado y caída/reintento con efecto único. Se corrigió el replay de un asiento ya contabilizado para que también compruebe que existe el eventooutboxv2 original y que tipo/dominio/agregado/versión/payload coinciden exactamente con el asiento. Un evento ausente o alterado bloquea sin crear otro ni reconstruir evidencia. El estado de transportePROCESSED no altera la identidad del evento ni acredita aceptación fiscal o de red. La proyección local usa contextoDecimal independiente del llamante, conservando importes exactos.

Pruebas:8 nuevas de aceptación y regresiones16 entrega local,26 posteo,10ACC-001,8ACC-002,20 apertura,4HTTP de compras/posteo/retry/recuperación/devoluciones/contrapartidas en ambos sistemas,25FX y23 reembolsos:140 ejecuciones aprobadas.26 del runner aparte. PostgreSQL16 desechable con rol restringido: dos llamadas concurrentes iguales regresan el mismo asiento (un receipt/un outbox); mismo identificador con importes distintos acepta una y rechaza otra; fallo al crear receipt o outbox revierte cabecera/líneas/auditoría/receipt/outbox y permite un retry único; fallo del consumidor revierte balance/receipt/acuse, y un acuse perdido no vuelve a incrementar el balance. SQLite comprueba además interrupción de auditoría, ausencia/alteración del outbox y proyección1000000.01 bajo precisiónDecimal hostil. No se usa bus externo ni cuentas reales. Evidencias/comandos reproducibles/tests/hashes y criterios en followups.ACC003_full_acceptance del JSON existente.

**Alcance pendiente deACC-003:** ninguno en sus criterios transaccionales locales originales. **Requisitos externos de esos criterios:** ninguno. Kafka, publicación externa y deduplicación/acuse de un consumidor externo siguen sin acreditarse: no se declara exactly-once de red ni se usa el estado local como sustituto de un acuse auténtico. Tampoco se habilitan producción ni integraciones fiscales/bancarias. La transacciónACID comprobada es la del motor compartido; los dos backendsHTTP no se convierten en una transacción distribuida.

**Estado:ACC-003 CERRADA al100% de sus criterios originales.** ACC-001/002 conservan aceptación y pasan regresión. Solo se añade el tercer hito deACC-003:51/72=70,83%,3/24 tareas cerradas (12,50% de cierres integrales), producción deshabilitada. El corte50/72=69,44%,2/24 y los anteriores se conservan en evidencia y pruebas del generador. ACC-004 es la siguiente; no se inició su desarrollo.

El cierre supera el umbral estricto70% establecido por el usuario para el siguienteSummit consolidado. Se prepara una sola entrega del acumulado local, con respaldo y comprobación del remoto, sin force ni descarte de trabajo ajeno. La publicación solo se da por confirmada al comparar elSHA local conrefs/heads/main después delpush; no se confunde publicación del código con despliegue productivo.


## Cierre secuencial · ACC-004 al100% · 2026-11-11

**Funcionalidad implementada y probada.** Los criterios originales se mantienen: carrerasPostgreSQL de cierre/posteo/reversión y cuentas con orden de bloqueo consistente. Se corrigió la configuración de períodos/cuentas, que no tomaba el bloqueo de empresa utilizado por el motor. save/delete de instancias y operaciones de sus managers ahora adquieren empresa antes de sus filas; conjuntos de empresas se bloquean porUUID ascendente, y el motor conserva cuentas porUUID ascendente. update/delete/bulk_update/bulk_create/update_or_create quedan serializados. Se rechazan reasignaciones de empresa y upserts masivos de estado para no mutar registros existentes sin revisión; el alta normal y la configuración durante provisión se conservan. El parámetro select_for_update en una actualización masiva no adelanta el bloqueo de filas a la consulta de propietarios. No son guardas contraSQL arbitrario o código privilegiado que adquiera deliberadamente bloqueos inversos.

Un objeto cargado antes de un cierre/desactivación no puede guardar su estado antiguo para reabrir/reactivar silenciosamente. Se admite escribir de nuevo el mismo estado y, tras refresh_from_db, una modificación explícita del estado; no se añade una política jurídica de reapertura. UUID de empresa como texto oUUID son equivalentes. No cambia el esquema, los saldos ni el hash histórico. No se añadieron pantallas o rutas nuevas de cierre.

PostgreSQL16 desechable con rol restringido verificó diez escenarios: cierre/posteo y cierre/contrapartida, cada uno simultáneo, cierre primero y operación primero; contrapartidas simultáneas con una sola aceptada; asientos con cuentas disjuntas y ordenSQL de bloqueos comprobado; desactivación/posteo y rollback de contrapartida antes del reintento. Si cierre obtiene el bloqueo primero, la operación queda rechazada sin borrador huérfano; si el asiento obtiene primero el bloqueo, termina antes de la marca temporal del cierre. Se comprobaron caminos de cierre/desactivación masivosORM además de save. Todos terminaron sin deadlock en esas ejecuciones; no es una promesa universal de ausencia de deadlocks bajo código o carga arbitrarios.

Pruebas:11 específicas nuevas,26 posteo,46 adaptador,10ACC-001,8ACC-002,8ACC-003,20 apertura,4HTTP de ambos sistemas (compras/recuperación/devoluciones/contrapartidas),25FX y23 reembolsos:181 ejecuciones funcionales/regresión aprobadas.26 del runner aparte. Las específicas incluyen contrapartida de original histórico cerrado dentro del período actual abierto, original intacto, rechazo de una segunda contrapartida y rollback al fallar auditoría. No se acredita cobertura100% ni rendimiento productivo por estos conteos. Evidencias/comandos reproducibles/tests/hashes y criterios explícitos en followups.ACC004_full_acceptance del JSON existente.

**Alcance pendiente deACC-004:** ninguno de sus criterios originales. **Requisitos externos de esos criterios:** ninguno; se ejecutaron sobre PostgreSQL real desechable. Política normativa/legal de cierre, roles/RLS/carga y despliegue productivos permanecen en sus frentes. Los pendientes históricos de reconstrucción de legados, lotes mayores y snapshots se conservan enR11/backlog global y no se dan por resueltos con este cierre.

**Estado:ACC-004 CERRADA al100% de sus criterios originales.** ACC-001/002/003 conservan aceptación y aprobaron nuevamente sus pruebas. Solo se acredita el tercer hito deACC-004:52/72=72,22%,4/24 tareas cerradas (16,67% de cierres integrales), producción deshabilitada. El corte51/72=70,83%,3/24 y los anteriores se conservan en evidencia y en pruebas del generador. ACC-005 es la siguiente; no se desarrolló en esta entrega. Cambios locales y respaldados sobre main publicadoc745d0a58, sin nuevo commit/push: la entrega consolidada por superar70% ya se realizó y no autoriza commits parciales posteriores.


## Cierre secuencial · ACC-005 al100% · 2026-11-11

**Funcionalidad implementada y probada.** Criterios originales conservados: VerifiedCompanyLink vigente, sin equivalencia automática deUUID y actor/período coherentes. Se corrige el uso de credencialesORM cacheadas: usuario y revisor se consultan en la base al resolver o revisar, y la revisión importada por el propio administrador se rechaza. Se validan tipos/conciencia de zona horaria en la vigencia antes de compararla. La creación del vínculo tomaTenant antes deTourismProvider y vuelve a comprobar privilegios del operador, alineándose con las operaciones financieras. El puenteSQLAlchemy refresca titular y roles del revisor, conservando el dueño corporativo fijado y la sesión ERP coincidente.

Ambos despachadores corporativos revalidan el vínculo después de recibir una respuesta del ERP. Si fue revocado durante la operación, no devuelven datos y explican que el resultado puede estar registrado y debe recuperarse con la solicitud/revisión original y acceso autorizado. No se afirma ni intenta rollback distribuido. La pruebaHTTP acredita que una revocación previa impide despacho y que una posterior a unPOST real de proveedor sintético retiene la respuesta, dejando exactamente un registro enERP, comprobado por suAPI autorizada. La variante de recuperación también descarta un reporte ante revocación posterior. No se envía un segundoPOST ni se inventa una contrapartida para ocultar el resultado.

Verificación:8 pruebas específicas,27 de identidad,46 adaptador,10ACC-001,8ACC-002,8ACC-003,11ACC-004,23 corporativas (incluidos cuatro recorridosHTTP de revocación/sesión) y23 reembolsos:164 ejecuciones funcionales/regresión aprobadas;26 del runner aparte. Los períodos ajenos y actores distintos se rechazan antes de crear asiento; el válido conservaTenant, período ycreated_by correctos. PostgreSQL16 desechable con rol restringido comprueba tres escenarios: creación concurrente con un solo vínculo, actor/revisor revocados pese a objetos cacheados yUUID coincidentes que nunca sustituyen el vínculo explícito. Se admitenUUID coincidentes solo tras revisión real almacenada: no se exige diferencia artificial ni se infiere igualdad empresarial. Tests/comandos reproducibles/logs/hashes y criterios en followups.ACC005_full_acceptance del JSON existente.

**Alcance pendiente deACC-005:** ninguno de sus criterios originales de puente interno. **Requisitos externos de esos criterios:** ninguno. Esto no valida identidad legal ante terceros niKYC/RNT; son registros y roles de laboratorio sobre motores/bases/HTTP ejecutables. Provisión/renovación/historial/SSO y administración de roles más amplios conservan sus pendientes del plan general, junto con migraciones/roles/aceptación reales. No se añadieron esos endpoints ni se acredita atomicidad entre las bases corporativa yERP. Las restricciones del puente se aplican al ámbito empresarial, sin cambiar el acceso personal a la billetera de cualquier persona registrada deColombia.

**Estado:ACC-005 CERRADA al100% de sus criterios originales.** Las cuatro tareas anteriores conservan aceptación y regresión aprobada. Solo se añade el tercer hito deACC-005:53/72=73,61%,5/24 tareas cerradas (20,83% de cierres integrales), producción deshabilitada. El corte52/72=72,22%,4/24 y los anteriores se conservan en evidencia y pruebas del generador. ACC-006 es la siguiente; no se desarrolló en esta entrega. Cambios locales respaldados sobre main publicadoc745d0a58, sin nuevo commit/push.

## Cierre secuencial · ACC-006 · 2026-11-11

**Problema y solución implementada:** el posteo genérico admitía tasas del catálogo global sin soporte documental ni vencimiento. Ahora las nuevas contabilizaciones extranjeras requieren la revisión explícita existente con fuente, versión, hash de soporte, ventana válida para la fecha económica y segunda confirmación. Se bloquean monedas desactivadas durante la confirmación; el catálogo histórico no autoriza asientos. Las contrapartidas conservan la tasa original y no buscan una nueva. No se modificaron asientos históricos ni el esquema.

La valoración, revaluación y liquidación usan contexto decimal aislado de precisión, redondeo y trampas del proceso. Se rechazan float, importes no finitos y tasas inválidas; una tasa explícita revisada de1 es distinta de un fallback implícito. El auxiliar de conversión valida monedas/importes/versiones y serializa versiones concurrentes, sin acreditar autenticidad externa por el indicador histórico is_official.

**Implementado y probado:**181 pruebas funcionales/regresiones,26 del runner,96 comprobaciones de navegador en ambos paneles y6 escenarios PostgreSQL16 con rol restringido. Incluyen tasas sin revisión, vigencia, moneda inactiva, precisión hostil, confirmación concurrente, contrapartida histórica y versiones del catálogo. Las tareas1–5 y los reembolsos aprobaron sus regresiones. Tasas y soportes sintéticos; no se consultaron proveedores, bancos niDIAN reales. Evidencia, hashes y salidas en el registro técnico existente de recuperación.

**Alcance pendiente:** ninguno de los criterios originales de validación interna deACC-006 en los pares soportados USD/EUR haciaCOP. **Requisitos externos y alcance global pendiente:** autenticidad de fuentes/tasas legítimas, revisión profesional/productiva, legados/lotes, comisiones, división/tránsito y otras monedas. La revisión del usuario no certifica una fuente de mercado: rate_independently_verified continúa falso. No se declara cierre de esos pendientes ni habilitación productiva.

**Resultado:**ACC-006 cerrada al100% de sus criterios originales internos. Solo se añade su tercer hito:54/72=75,00%;6/24 tareas cerradas=25,00% de cierres. Base y cortes anteriores conservados; producción deshabilitada. ACC-007 no se inició. Cambios acumulados locales sobre main c745d0a58, sin nuevo commit/push, con respaldo y manifiesto verificables.

## Reevaluación y corrección deACC-001 aACC-006 · 2026-11-11

Se revisaron los criterios originales, rutas de creación/posteo/reversión, inmutabilidad, transacción/outbox, bloqueos, vínculo de empresa/actor, FX, reportes y migración. Se ejecutaron pruebas nuevas que fallaban antes de corregir; las regresiones anteriores por sí solas no detectaban estas fallas. No se declara inmunidad ni ausencia universal de defectos.

| Tarea | Resultado de la revisión | Corrección o comprobación |
|---|---|---|
|ACC-001 · Exactitud/aislamiento|Criterios originales aprobados tras corrección|Validación de tasa antes de conversión ORM; rechazo de float/no finitos/exceso de precisión; contexto decimal de reportes aislado.|
|ACC-002 · Inmutabilidad|Regresión aprobada|UUID, identidad, padre cacheado, guardas ORM/SQL verificadas; sin nueva falla encontrada en esos casos.|
|ACC-003 · Idempotencia/outbox|Regresión aprobada|Repetición, contrato distinto, rollback/recepción/proyección y concurrencia verificados; sin nueva falla encontrada en esos casos.|
|ACC-004 · Concurrencia|Aprobada tras corrección|Identidad de cuentas usadas (código/tipo/catálogo) protegida para no invalidar hashes; escrituras individuales/masivas y tres órdenes concurrentes de cambio/posteo probados.|
|ACC-005 · Empresa/actor|Regresión aprobada|Vínculo vigente, titular/revisor, sesión y supresión de resultado al revocar verificados en ORM, HTTP corporativo y PostgreSQL.|
|ACC-006 · FX|Regresión aprobada y entrada reforzada|Fuente/versión/vigencia/moneda, sin fallback global, valoración/revaluación/liquidación y reversión histórica; tasa de cabecera exacta desde el borrador.|

**Hallazgos subsanados:**(1) modificar código/tipo/catálogo de cuenta utilizada rompía el hash histórico; ahora se bloquea bajo el mismo orden de locks del posteo. Nombre visible y activación siguen disponibles. (2) Tasa de cabecera float o con precisión sobrante atravesaba elORM; ahora se rechaza antes de guardar y el valor por defecto esDecimal. (3) El margen de rentabilidad heredaba trampas/redondeo del proceso; ahora usa contexto propio, con prueba del resultado66,6667% para2/3. (4) Dos pruebas de instalación omitían el consentimiento del destinatario; se actualizaron para verificar rechazo sin consentimiento y ejecución posterior con el destinatario real del caso. No se relajó seguridad de billetera.

**Pruebas finales:**328 pruebas funcionales/integración en19 suites, más26 del runner y14 del registro de progreso;38 escenarios PostgreSQL16 con roles restringidos;186 comprobaciones de navegador, incluyendo ambos paneles y recorrido real con cookie/CSRF. Instalación nueva ERP: esquema listo, sin deriva de modelos, migración idempotente y respaldo/restauración aprobados. Las migraciones0007 de ambos árboles solo cambian el estado/default Python, con prueba de ceroSQL de ida/vuelta; no reescriben datos históricos. El primer ensayo se inició antes de crear la migración y marcó pendiente correctamente; se repitió desde cero con fuentes estables y fixtures corregidos. Evidencia, hashes, fallos reproducidos y resultados finales en el JSON/log técnico existente.

**Pendiente y límites:** no se encontraron fallas restantes en los casos ejecutados de los criterios originales soportados. No es certificación de toda entrada o entorno. Las protecciones nuevas de identidad de cuenta cubrenORM, noSQL privilegiado. Conservan sus pendientes los roles/infraestructura productivos, migración histórica real, seguridad/carga independiente, tasas y soportes auténticos, aceptación contable/legal y proveedores/dispositivos reales. No se contactaron bancos/DIAN/proveedores reales ni se habilitó producción. Otras monedas, legados/lotes/comisiones y demás alcance global no se declaran resueltos.

**Porcentaje sin inflación:**54/72=75,00%;6/24 tareas cerradas según criterios originales (25,00% de cierres). La reevaluación/corrección no añade hitos repetidos. ACC-007 no se inició. Cambios anteriores preservados; entrega local respaldada, sin commit/push nuevo.

## Cierre secuencial · ACC-007 · 2026-11-11

**Criterio original conservado:** «Detectar cambio de cualquier cuenta/línea/importe/moneda y proteger asientos SQL; conservar historia». Se acredita el contrato interno de hash versionado y las guardas DML instaladas, sin calificar una infraestructura productiva completa.

**Problemas subsanados:** las guardas anteriores protegían cabeceras/líneas pero permitían editar porSQL la identidad de una cuenta utilizada, invalidando su hash. La presencia estructural de un disparador tampoco probaba que su cuerpo siguiera siendo el esperado. Se añade protecciónSQL para identidad de cuenta utilizada y diagnóstico de cuerpos, adjuntos, estado y configuración de funciones esperados. El auditor de privilegios incluye ahora las cuatro tablas protegidas; no confundeSET ROLE con una sesión productiva cualificada.

**Código y pruebas:** nuevas guardasSQLite/PostgreSQL bloquean cambios deID/empresa/código/tipo/catálogo y eliminación de cuentas utilizadas. Se conserva la edición de nombre visible/activación, que no forman parte del hash financiero existente. Cabeceras/líneas contabilizadas siguen inmutables; se verifican cambios de importe, moneda y referencias, truncado y sombra temporal de tabla padre. El diagnóstico es de lectura: no repara ni reinstala guardas ante una alteración. Reinstalación conDDL transaccional: un fallo revierte la retirada previa. Migración0008 en ambos árboles, sin modificar versión/algoritmo de hash ni registros históricos.

**Verificación final:**313 pruebas funcionales en19 suites, incluidas11 específicas de aceptación y regresiones deACC-001 aACC-006;26 del runner y15 del registro de progreso por separado.13 escenariosPostgreSQL16, con tres carreras de ediciónSQL/posteo dentro de un escenario;82 comprobaciones de navegador entre ambos paneles y recorrido web con sesión/CSRF. Instalación nuevaERP y sus13 pruebas aprobadas. Prueba reproducible adicional de migración de ida/vuelta sobreSQLite no vacío: cabeceras/líneas idénticas, hashes válidos y detección de guarda ausente durante la reversión explícita. Evidencia/comandos/rutas/hashes en elJSON/log técnico existente.

**Alcance pendiente de los criterios internos originales:** ninguno encontrado en el alcance soportado probado. **Requisitos externos/producción pendientes:** roles/RLS/permisos reales completos, migración histórica del cliente, revisión de seguridad y firma/atestación independientes. Un dueño/superusuario puede sustituir/deshabilitar guardas; el diagnóstico compara contra código de aplicación confiable, no certifica un entorno comprometido. El rol de laboratorio sigue sin cualificación productiva y no se declara invulnerabilidad. No se contactaron bancos/DIAN/proveedores reales ni se habilitó producción.

**Resultado:**ACC-007 cerrada al100% de sus criterios originales internos. Se acredita exclusivamente su tercer hito:55/72=76,39%;7/24 tareas cerradas (29,17% de cierres). Cortes previos y denominador conservados. ACC-008 no se inició. Avances anteriores preservados y respaldo local verificado; sin nuevo commit/push.

## Cierre secuencial · ACC-008 · 2026-11-11

**Criterio original:** «Estados y payload versionados; cobro/acuse/confirmación no se fabrican». Cierre del contrato de origen/solicitud, sin sustituir emisión fiscal ni aceptación externa.

**Hallazgos y código:** el contrato puro admitíaCRM ganado, pero el modelo global no tenía pertenencia contable. Se añade vínculo persistido con revisión de operador independiente del titular, vigencia explícita y evidencia; no existe una ruta pública para apropiarse de un lead porUUID. No se mueve el registro legado ni se deduce empresa por coincidencia de identificadores. La API vuelve a comprobar fuente ganada, cliente, importe, vínculo, propietario y revisor antes de aceptar revisión/solicitud; se evita bloqueo cruzado de usuarios de empresas distintas.

El productorCRM también estaba bloqueado: usaba campos/etapas ausentes y convertía importes a float. Se restauran industry/company_size, expected_plan/probability y etapasPROPOSAL/NEGOTIATION mediante migración aditiva0002 en ambos árboles; los datos históricos desconocidos quedan vacíos/null. Registro de prospecto y oportunidad atómicos, importe decimal exacto y transición desde estado persistido; no se reabre un cierre con un objeto desactualizado. Prueba real desdeCRMService hastaWON, revisión y solicitud, sin generar factura/cobro al ganar.

Revisión fiscal persistida y segunda confirmación separadas, con contratos versionados. La cola comprueba que la referencia de revisión exista y coincida con empresa/actor/snapshot/evidencia; rechaza referencias inventadas y estados de entrega desconocidos. La reserva conserva su flujo y valida su sobre/versionado sin aceptar una supuesta aprobación legal. Se conserva el protocolo de intención/outboxv1 y sus identidades; no se reescriben solicitudes previas.

**Integración:** nuevas rutasERP revisar-oportunidad-fiscal/solicitar-factura-oportunidad y cuatro comandos fijos del puente corporativo para revisión/solicitudCRM y reserva. Se mantienen sesión, CSRF, vínculo empresarial y comprobación posterior de permisos. El contrato de respuesta exige REQUEST_ONLY y rechaza supuestos cobros, acuses o aceptación fiscal. PROCESSED indica entrega de cola, nunca aceptaciónDIAN. Un timeout conserva resultado incierto; se reintenta la misma revisión, sin inventar confirmación ni atomicidad distribuida.

**Verificación:**369 pruebas funcionales/regresiones en24 suites, incluidas21 específicas deACC-008 y5 del nuevo contrato/HTTP corporativo;26 del runner y16 del registro de progreso aparte.8 escenariosPostgreSQL16: vínculo/revisión/solicitud concurrentes, cambio de estado, fallo/reintento, entrega sin aceptación fiscal, revocación y revisión cruzada entre empresas sin deadlock.82 comprobaciones de navegador de recorridos existentes. Migración sobre filasCRM legadas sintéticas conservaID/cliente/estado/importe y deja desconocidos históricos sin fabricar; prueba reproducible de migración más13 comprobaciones sobre esquema local migrado, sin deriva. Evidencias/hashes/comandos en elJSON/log técnico existente.

**Pendiente de los criterios internos originales:** ninguno en el alcance soportado probado. **Alcance más amplio y requisitos externos pendientes:** emisión/acuseDIAN auténticos, banco independiente, normativa y soportes reales, múltiples anticipos y otros ajustes/atribución tributaria, formulariosCRM completos, catálogo y recuperación/renovación del vínculo, aceptación profesional/productiva y migración histórica del cliente con respaldo/rollback revisados. Se conserva el texto previo de pendientes en la evidencia para no perderlos; siguen enR03/R04/R06/R12/R18/R20. La revisión documental del operador no se certifica con hashes sintéticos. No se ejecutó pago, emisión fiscal, publicación ni llamada a proveedor real.

**Resultado:**ACC-008 cerrada al100% de sus criterios originales del contrato. Solo se añade su tercer hito:56/72=77,78%;8/24 tareas cerradas (33,33% de cierres). Producción deshabilitada; no se acredita el resto del ciclo fiscal/comercial. ACC-009 no se inició. Cambios acumulados locales, respaldados; sin nuevo commit/push.

## ACC-009 · Incremento local y bloqueo de cierre · 2026-11-11

**Estado:EN EJECUCIÓN, NO cerrada.** Criterio original conservado: «Documentos válidos y acuses reales en habilitación; certificado bajo custodia autorizada». No se puede acreditar con certificados/acuses de laboratorio ni validaciónXSD de referencia.

**Implementado y probado:** fuenteCRM ganada/revisada consultada de forma autenticada, con permisos/vigencia/última revisión y cambios de origen comprobados. Nueva rutaERP fuente-borrador-ubl-crm y puente corporativo; contrato de fuente diferenciaCRM/WON de reserva/CONFIRMED sin acreditar identidad/fiscalidad externas. El panel compartido permite elegir origen, reconsulta antes de generar y limpia estado al cambiar origen o identidad. Se conserva azul metalizado/azul claro/texto blanco, estructura y modo reserva.

**Falla real subsanada:** los borradores vinculados podían repetir la declaraciónXML al serializar elDocument reparsado. La pruebaXSD nueva falló antes de corregir. Ahora se serializa solo documentElement y se añade una sola cabecera. Dos documentosCRM generados en navegadores de ambos paneles pasan elXSD UBL2.1 CS1 de referencia local; no es cualificación del anexoDIAN vigente. Se verifica también parseo correcto del origen reserva. El diagnóstico de resolución usa fecha civilAmerica/Bogota y rechaza fechas no canónicas; nunca habilita transmisión por tener configuración pública válida.

**Pruebas finales:**161 pruebas funcionales/integración en12 suites, incluidas8 nuevas locales y2 HTTP del puente real;26 del runner y16 del registro de progreso por separado. Tres suites de navegador aprobadas: CRM con generación/cifrado/recuperación en ambos paneles y2 XML validados contra14 archivosXSD de referencia íntegros, fuente reserva con rechazo de alteraciones y paquetes cifrados de reserva en ambos paneles.24 pruebas del firmador y24 de acuses/diario son explícitamente de laboratorio. Una prueba del firmador necesitó sockets locales fuera del sandbox; completó correctamente. No se presentan como firma/acuse reales.

**Desarrollo todavía pendiente:** concretar formato fiscal del anexo/perfil aplicable (identidades/catálogos, numeración/CUFE/QR y representación fiscal/PDF-A3); integrar y cualificar firma real/cadena/política/revocación/reloj y custodia autorizada; implementar/verificar transporte del canal y validación de acuses auténticos/resultado incierto. El firmador sigue restringido aLABORATORY_ONLY y la transmisión no cualificada permanece bloqueada.

**Requisitos externos:** definirDIAN directo o proveedor autorizado y perfil/anexo vigente; certificado legítimo con autorización/custodia del cliente, resolución/identidad, software/test set/acceso de habilitación configurados por canal seguro y documentos/acuses reales revisados. Se preguntó canal y disponibilidad de certificado/test set; no se presume respuesta por silencio. No enviar claves privadas/PIN/credenciales al chat. No hubo emisión, pago ni llamada aDIAN/proveedor real. No se acredita aceptación legal ni productiva.

**Progreso sin crédito artificial:**77,78%=56/72;8/24 tareas cerradas;ACC-009 conserva2/3 hitos y sigue abierta. El incremento amplía implementación/pruebas ya acreditadas; no suma aceptación completa. ACC-010 no se inició. Pendientes/evidencias en este seguimiento y elJSON/log técnico existentes; cambios locales respaldados, sin nuevo commit/push.

### Decisión del usuario · Canal DIAN directo

El usuario confirmó integración directamente conDIAN y difirió expresamente ese trabajo para una etapa posterior. No se buscará ni contratará un proveedor intermediario como parte de esta decisión. El canal queda definido; certificado/custodia autorizada, configuración y set de habilitación, transporte y acuses auténticos continúan pendientes, sin afirmar disponibilidad. Se conserva el criterio original deACC-009 y su estado abierto, junto con el desarrollo fiscal restante ya enumerado. El aplazamiento no acredita aceptación completa, no aumenta77,78% ni autoriza el cierre o inicio automático de otra tarea.

## Cierre · ACC-010 · 2026-11-11

**Autorización/secuencia:** el usuario pidió expresamente desarrollarACC-010 después de aplazar la integración directa conDIAN. Se conservaACC-009 abierta y sus criterios íntegros; no recibe aceptación ni se oculta su bloqueo. Este cierre corresponde aACC-010.

**Criterio original:** «DEK por documento; KEK cliente; AAD; no plaintext ERP; recuperación/rotación probadas». Se acredita la opción portátil de cifrado cliente, no custodia hardware ni despliegue productivo.

**Implementado/subsanado:** antes se ignoraba una referencia de recuperación esperada desconocida por elSDK. Se añadió expected_reference opcional de versión/huella a recuperación/rotación y al clientePython; referencia incorrecta se rechaza antes de derivar/descifrar. La prueba de navegador falló antes de la corrección y pasa después. Referencia exacta no demuestra ser la última versión; sin ella se conserva la recuperación legítima de archivos históricos.

Ambos paneles permiten indicar referencia confiable de respaldo al recuperar archivo oBYOS; evitan mostrar plaintext al fallar y mantienen el paquete cifrado anterior. ContraseñasUnicode malformadas se rechazan antes de una conversiónUTF-8 con pérdida;Unicode válido soportado. No cambia el protocolo cifrado/HMACv1. La rotación conserva ciphertext/IV y reenvuelve laDEK con la nuevaKEK, encadenando versión/huella; copias anteriores no quedan revocadas.

**Pruebas finales:**142 pruebas funcionales en10 suites, incluidas9 específicas de aceptación;26 del runner y17 del registro de progreso por separado.136 comprobaciones de navegador entre4 suites y el navegador integrado del fixturePostgreSQL, con ambos paneles.6 escenariosPostgreSQL (2 de pérdida/ambigüedad de commit y4 de roles/cadena/reintento/competencia), servicioHTTPS local y paquetes sintéticos. Se comprobaronDEK distintas por cifrado mediante unwrap independiente, AAD de empresa/documento/dominio, recuperación serializada, clave/ámbito erróneos, referencias incorrectas, manipulación y exclusión de plaintext/llaves enERP. Runtime generado coincide conSDK canónico. Firmador/interop conserva24 pruebas de laboratorio, sin firma fiscal real. Evidencia/hashes/comandos y fallo inicial en elJSON/log técnico existente.

**Alcance pendiente original portátil:** ninguno en los criterios soportados probados. **Límites y pendientes externos/globales:** no se recupera sin secreto/archivo; no se revocan copias antiguas ni se acredita última versión independiente. Custodia/recuperación física/hardware, titularidad/destino/TLS/grants reales, retención/backup, cliente/infraestructura confiables y aceptación productiva permanecen enR07/R08/R17/R20. Se conserva el texto previo de pendientes en evidencia. No se habilitó producción ni se ejecutó pago, firma fiscal real o integraciónDIAN.

**Resultado:**ACC-010 cerrada al100% de sus criterios originales del cifrado portátil cliente. Solo se acredita su tercer hito:57/72=79,17%;9/24 cerradas (37,50% de cierres:1–8 y10). ACC-009 permanece abierta/aplazada. Cambios acumulados preservados y respaldados localmente; sin nuevo commit/push.

## ACC-011 · Drive y OneDrive · 2026-11-11

**Implementado y probado:** destinos elegidos por el usuario: Google Drive o OneDrive. Se añaden adaptadores locales en `DESKTOP/customer-cloud-store/`: OAuth para cliente nativo/público con PKCE S256, state de uso único/caducidad, callback loopback estricto y permisos acotados; tokens solo en memoria. Los adaptadores reciben paquetes ya cifrados del protocolo existente, vinculan empresa/cuenta/carpeta y requieren confirmación de carga. Un plan identifica bytes y destino; después de un resultado incierto se consulta ese mismo plan y se reintentan únicamente sus mismos bytes. Drive preasigna identidad de archivo; OneDrive solicita creación sin reemplazo. Solo se confirma almacenamiento tras leer exactamente los bytes cifrados. No hay fallback a un destino ajeno ni recepción de claves/documentos en claro por el ERP.

La descarga preautorizada de OneDrive exige un host exacto revisado explícitamente; no reenvía bearer ni cookies y rechaza redirecciones. La URL temporal no se incorpora a planes ni recibos. `drive.file` y `Files.ReadWrite.AppFolder` permiten lectura/escritura dentro de su alcance: no se describen como permisos de escritura exclusiva. Los recibos distinguen almacenamiento de autenticación criptográfica, versión vigente, titularidad independiente, aceptación fiscal y cualificación real del proveedor: esas afirmaciones permanecen falsas.

**Pruebas:** 17 pruebas nuevas de contrato con HTTP simulado para ambos proveedores; 15 regresiones de paquetes/API y 13 de recuperación existentes. Cubren PKCE, ámbito, state, caducidad, replay, revocación/403, límites de respuesta, caída tras escritura, recuperación sin segunda carga, colisiones, aislamiento, confirmación y descargas sin credenciales. Estas 45 pruebas no son permisos cloud auténticos. La regresión TestClient requirió IPC fuera del sandbox local; no realizó conexión a cuentas externas.

**Desarrollo pendiente:** integrar el flujo OAuth nativo y los conectores con las interfaces de ambos sistemas; aprovisionar/seleccionar carpeta Drive accesible al scope; cualificar condiciones de creación y descargas reales; operación, retención y recuperación del cliente. Estos son adaptadores ejecutables por código, no una interfaz cloud ya desplegada.

**Requisitos externos:** registrar la aplicación nativa en Google Cloud o Microsoft Entra, fijar redirect y perfil admitidos, autorizar una cuenta administrada por el cliente, comprobar permisos/revocación y resultado incierto con el proveedor real. Se solicitó disponibilidad sin pedir secretos por chat. La elección de plataforma no prueba que esas aplicaciones/cuentas estén preparadas.

**Estado:** ACC-011 permanece parcial 2/3; no recibe el hito de aceptación completa exigente de permisos reales. Progreso conservado: **57/72 = 79,17%; 9/24 tareas cerradas**. ACC-009 continúa aplazada para integración directa DIAN. Producción no habilitada; cambios locales sin nuevo commit ni push. Evidencia añadida al JSON y log técnicos existentes.

## ACC-012 · Controles previos al despacho · 2026-11-11

**Hallazgo y solución codificada:** el despacho genérico existente comprobaba autorización profesional, EPP y descanso, pero carecía de una evaluación de riesgo explícita por orden. Se añade `sg_sst/dispatch_risk.py`: aprobación provisionada para empresa/orden, versión, revisor activo autorizado, vigencia para toda la operación, peligros con controles/soportes, clase de riesgo declarada por trabajador y EPP adicional requerido. Ausencia, revocación, peligro sin control, cobertura incompleta o EPP faltante bloquean el inicio. La huella de la evaluación se liga a la fuente revisada: un cambio entre confirmaciones invalida el despacho. Las constancias antiguas sin esta huella requieren nueva revisión, sin borrar datos ni reiniciar operaciones ya registradas. La consulta de operaciones terminadas conserva acceso aunque venza la evaluación; un cambio de fuente durante la ejecución conduce a incidencia en el flujo de cierre existente.

El catálogo se carga mediante archivo privado `OPERATIONAL_RISK_ASSESSMENT_FILE`, con el lector existente que exige ruta absoluta, ausencia de enlaces, permisos privados, tamaño acotado y JSON sin duplicados. Estructura: UUID de empresa → UUID de orden → evaluación. No se acepta una evaluación enviada por el solicitante como política habilitante ni se habilita por defecto. La clase declarada no certifica afiliación ARL ni cumplimiento normativo. No se incluyen diagnósticos ni decisiones médicas en respuestas de despacho.

**Otra falla corregida:** referencias EPP anidadas y UUID malformados podían producir excepciones antes de la validación de referencias. Ahora se rechazan explícitamente como errores de validación, sin escrituras ni suposiciones sobre aptitud.

**Verificación ejecutada:** 14 nuevas pruebas de riesgo/referencias, 37 de datos laborales y despacho positivo, 22 de protección de transiciones y 14 de permisos/SG-SST: **87 pruebas aprobadas** con ORM/API y datos sintéticos. Se probaron riesgo ausente/ajeno, cambio entre confirmaciones, controles faltantes, clase inválida, EPP adicional, caducidad, revisor no provisionado, ruta positiva, privacidad y referencias inválidas. La evidencia técnica se añade al JSON/log existentes, con comandos y hashes.

**Alcance pendiente:** formularios y recorridos completos, despacho especializado y conexión operacional de ambos sistemas, cualificación PostgreSQL/concurrencia y migración histórica. **Requisitos externos:** políticas laborales/SG-SST y profesionales legítimos, soportes autorizados y comprobación física de aptitud/EPP/descanso. Los datos de prueba no cumplen esos requisitos. No se modificaron reservas, RAT/ADR, pagos ni nómina.

**Resultado:** ACC-012 permanece parcial 2/3; no se declara terminada ni se aumenta el porcentaje por reforzar pruebas. Se conserva **79,17% = 57/72 hitos; 9/24 tareas cerradas**, con ACC-009 aplazada y ACC-011 pendiente de OAuth/cuenta reales e integración de interfaces. Cambios locales, sin commit/push ni habilitación productiva.

## Evaluación transversal ACC-001 a ACC-012 · 2026-11-11

**Resultado de la revisión:** se contrastaron los criterios originales con las rutas y evidencias existentes y se ejecutaron pruebas focalizadas, PostgreSQL desechable, HTTP entre backends y Chromium. No es una certificación exhaustiva de producción. Los cierres internos de 1–8 y 10 se sostienen en las pruebas ejecutadas; 9, 11 y 12 conservan alcance pendiente.

| Tarea | Evaluación verificada | Pendiente concreto |
|---|---|---|
| ACC-001 | Importes exactos, balance y aislamiento; regresión y PostgreSQL aprobados | Cualificación productiva del alcance global, sin reabrir criterios internos cumplidos |
| ACC-002 | Identidad UUID y guardas ORM/SQL; regresión y PostgreSQL aprobados | Despliegue y roles productivos |
| ACC-003 | Idempotencia y outbox atómicos; carreras PostgreSQL aprobadas | Kafka/consumidor externo no acreditados por atomicidad local |
| ACC-004 | Períodos, reversión y orden de bloqueos; carreras PostgreSQL aprobadas | Carga productiva y legados del alcance global |
| ACC-005 | Vínculo empresarial/actor vigente; PostgreSQL y puente HTTP aprobados | Aprovisionamiento/SSO/identidad legal externa |
| ACC-006 | Tasas explícitas y sin fallback; casos monetarios y PostgreSQL aprobados | Autenticidad externa de tasas y otras monedas/legados |
| ACC-007 | Hash y guardas de integridad; PostgreSQL aprobado | Migración histórica del cliente y roles productivos |
| ACC-008 | Contrato CRM/reserva, fuente e idempotencia; PostgreSQL y HTTP aprobados | Interfaces CRM completas y aceptación fiscal/bancaria externa |
| ACC-009 | Borradores locales y recorridos existentes aprobados | Perfil/documento fiscal completo, firma autorizada y DIAN directo aplazado por el usuario |
| ACC-010 | Cifrado, recuperación y rotación; pruebas y ambos paneles aprobados | Custodia/hardware/recuperación física y operación productiva |
| ACC-011 | Conectores locales, API de paquetes y recuperación BYOS probados | OAuth/cuenta reales no disponibles; integración cloud con interfaces y cualificación del proveedor |
| ACC-012 | Datos laborales, controles previos y protección de evidencia probados | Despacho especializado, interfaces de ambos sistemas, PostgreSQL integral/concurrencia y legitimidad profesional/física |

**Fallas encontradas y subsanadas:**

1. El diagnóstico de guardas laborales PostgreSQL aceptaba un disparador con `WHEN (false)`. Se reprodujo el fallo antes de corregirlo. Ahora exige disparador sin condición, sin argumentos/columnas parciales y función del mismo esquema, además del cuerpo y tipo esperados.
2. Las tablas laborales permitían `TRUNCATE` aunque bloquearan actualización/borrado por fila. Se añadió un disparador de sentencia y la migración aditiva `sg_sst/0002_prevent_evidence_truncate.py`. Se probaron bloqueo, detección de ausencia y subida/bajada/subida con filas conservadas. Los entornos existentes deben aplicar la migración antes de usar los servicios que exigen estas guardas; no se reparan automáticamente ni se modificaron bases reales.
3. La configuración/grants BYOS usaba JSON permisivo y comprobaciones de ruta vulnerables a enlaces de directorios padre. Se cambió por apertura mediante descriptores de directorio sin seguimiento de enlaces, verificación del archivo abierto, lectura acotada y rechazo de claves duplicadas/no finitos. Se prueban también permisos públicos, FIFO, exceso de tamaño y ruta relativa.
4. La prueba de trabajador ocupado podía pasar por ausencia de riesgo en la segunda orden, ocultando la condición que pretendía verificar. Ahora provisiona ambos riesgos y exige expresamente el rechazo por trabajador ya asignado.

**Validación:** 283 casos Python funcionales (incluidos 33 HTTP corporativos y 7 nuevos de configuración), 17 pruebas adicionales del registro de progreso, 59 escenarios PostgreSQL contables, 6 laborales y 6 BYOS (2 de pérdida de respuesta y 4 existentes), más 118 comprobaciones de navegador. Las repeticiones tras corregir no se suman como nuevos casos. El navegador BYOS falló inicialmente al invocarlo sin su archivo de fixture; se ejecutó después mediante su arnés HTTPS/PostgreSQL requerido y pasó. Se conserva esta incidencia de ejecución en la evidencia, sin presentarla como falla de producto. La instalación ERP desde cero terminó con schema ready y sin incidencias del system check; la prueba de subida/bajada/subida de guardas contables conservó cabeceras y líneas contabilizadas. La primera invocación de esa prueba carecía de una base inicializada; se repitió después de crearla explícitamente, sin tocar datos previos.

**Límites:** datos sintéticos y PostgreSQL local no prueban autenticidad DIAN, permisos cloud reales, legitimidad profesional/ARL, descanso físico, atestación de hardware ni preparación productiva. No se considera terminada la tarea 12 por endurecer guardas. **Progreso conservado: 79,17% (57/72), 9/24 tareas cerradas.** Sin nuevo commit/push. Evidencia y comandos en el JSON/log técnicos existentes; avances respaldados localmente.

## ACC-013 · Nómina, provisiones y trazabilidad de costos · 2026-11-11

**Hallazgo y solución:** el motor ya conservaba jornadas, centros y componentes de nómina contabilizada, pero una orden podía cambiar su referencia comercial sin invalidar la distribución. Se añade el contrato `sgacd-payroll-operation-cost-v2`: cada operación fija referencia comercial declarada, ventana planificada, estado activo y huella de descripción. La revisión/revalidación compara esa fuente completa; un cambio impide registrar la revisión pendiente y marca la distribución anterior como no vigente, sin afirmar un total completo. Revisión nueva y reintento siguen sin duplicar asiento, gasto ni provisión.

El puente corporativo valida referencias canónicas, cobertura exacta de operaciones, vigencia estructural de ventanas y campos permitidos; rechaza referencias ajenas, duplicadas, ausencia de fuente y campos clínicos. El componente compartido presenta referencia comercial y ventana en ambos paneles, conservando azul metalizado/azul claro/texto blanco, permisos y confirmaciones separadas. El UUID es una referencia comercial declarada; no acredita por sí solo contrato auténtico ni paquete vendido. No se modifica el RAT, reservas ni ADR.

**Compatibilidad:** los paquetes históricos v1 permanecen legibles e inalterados. Al no fijar esta fuente comercial, no reciben calificación de fuente actual por el cálculo v2; el usuario debe volver a revisar para registrar una versión nueva. La interfaz advierte de esa limitación histórica. No se ejecuta migración destructiva ni se recalcula dinero automáticamente.

**Otra falla corregida:** códigos de devengados o tipos de regla recibidos como objetos/listas JSON podían disparar `TypeError` antes de la validación. Ahora producen un rechazo contable explícito; se añadió regresión para valores anidados y nulos.

**Pruebas ejecutadas:** 147 casos en 10 suites de nómina/costos (incluidos 6 nuevos de trazabilidad y 1 de entradas malformadas), 14 de contrato/HTTP corporativo, 42 comprobaciones Chromium entre ERP y Analemática y 3 escenarios PostgreSQL16: reintento concurrente de la misma revisión, planillas competidoras por una novedad y fallo/rollback/reintento. Solo un consumo y un asiento por efecto; integridad contable conservada. Chromium comprueba visualización de trazabilidad, diseño móvil, texto blanco y limpieza por cierre/pérdida de identidad. La primera ejecución HTTP tenía una ruta Python incompleta; se repitió con el directorio backend explícito y pasó. Las repeticiones no se suman como casos adicionales. Comandos, conteos y hashes se registran en el JSON/log técnicos existentes.

**Desarrollo pendiente:** enlace individual de cada minuto de suplemento a jornadas, clasificación por horarios/calendario/festivos con reglas revisadas, otras novedades/ausencias/incapacidades/viáticos, retiro/ajustes de fuentes consumidas y nómina electrónica. **Requisitos externos:** reglas laborales aplicables y soportes/datos legítimos revisados por un profesional; habilitación DIAN cuando corresponda. Las tasas declaradas y pruebas sintéticas no acreditan cumplimiento legal.

**Estado real:** ACC-013 continúa parcial 2/3; este incremento no completa todos sus criterios ni recibe crédito adicional por pruebas. **79,17% (57/72), 9/24 tareas cerradas.** Las tareas 9, 11 y 12 conservan sus pendientes; no se alteraron criterios ni denominador. Cambios respaldados localmente; sin commit/push y sin producción habilitada.

## ACC-014 · IVA, retenciones y políticas explicables · 2026-11-11

**Implementado:** el registro integral de cuenta tributaria conserva la conciliación de IVA generado/descontable y retenciones con asientos reales. Se añade `sgacd-tax-register-v3`: cada línea comercial explica las políticas del documento original por concepto (identidad, código, versión, vigencia, huella, respaldo, categoría, dirección y fecha económica). Se revalida la versión persistida contra la huella y la vigencia original; una nueva versión futura no reclasifica movimientos históricos. El caché de políticas evita repetir consultas de la misma versión dentro del reporte; más de 500 referencias exige reducir el intervalo, sin truncar evidencia ni declarar completitud falsa.

Devoluciones proporcionales, por importe/concepto y sus correcciones conservan el vínculo con la política del original, sin sustituir sus líneas compensatorias verificadas. Las referencias son de la política original, no importes de ajuste recalculados. Reservas u otras fuentes que no capturaron esa política se marcan `NOT_CAPTURED_IN_SOURCE`; no se inventa respaldo. No se modifican importes contables ni se presumen tasas legales, deducibilidad o aceptación fiscal.

**Ambos sistemas:** el puente valida el contrato v3 y mantiene compatibilidad con v2; rechaza metadatos privados, duplicados, versiones inválidas, vigencias incoherentes o cobertura falsa. Los dos paneles muestran código/versión/categoría/vigencia/fecha original y advierten cuando falta política capturada. Se conserva estructura y diseño azul metalizado/azul claro con texto blanco. Las interfaces v2 siguen siendo legibles sin añadirles retrospectivamente una acreditación.

**Fallas subsanadas:** tipos/categorías tributarios enviados como objetos o listas podían producir excepciones no controladas; ahora se rechazan como errores contables. La regresión de devolución por cambio de tipo de cuenta quedó ajustada al bloqueo temprano de identidad de cuentas ya contabilizadas: se demuestra que el cambio se rechaza, la cuenta permanece intacta y la devolución válida aún se puede contabilizar. No se debilitó la guarda para hacer pasar la prueba. La prueba de una segunda versión de política se corrigió para usar una vigencia no superpuesta, respetando la regla existente.

**Pruebas ejecutadas:** 126 casos Python en 9 suites tributarias/compras (incluidos 5 nuevos de explicación), 12 de contrato/HTTP corporativo, 126 comprobaciones Chromium (74 de compras y políticas en ambos paneles, 52 del recorrido contable/tributario ERP) y 6 escenarios PostgreSQL16 de devoluciones/correcciones concurrentes y rollback/reintento. Chromium confirma visualmente la explicación de la política original y verifica importes, limpieza de sesión y diseño móvil. Los reintentos no se suman como nuevos casos. Comandos, logs/hashes y límites se añaden al registro técnico existente.

**Desarrollo pendiente:** captura versionada de políticas en fuentes históricas/reservas que carezcan de ella, períodos declarativos, conciliación multicuenta y cobertura integral de tratamientos turísticos. **Requisitos externos:** marco normativo vigente y aplicabilidad revisados profesionalmente; contraste oficial DIAN/acuses y aceptación profesional/productiva. La integración DIAN continúa aplazada por el usuario; no se cerró con una simulación.

**Estado real:** ACC-014 permanece parcial 2/3; este incremento no completa todos sus criterios. Progreso conservado **79,17% (57/72 hitos), 9/24 tareas cerradas**. No hay commit/push ni despliegue productivo; avances respaldados localmente.

## ACC-015 · Importación multibanco y estados externos · 2026-11-11

**Requisitos recibidos:** el usuario solicita todos los bancos de Colombia y más de 50 cuentas por usuario. Se conserva como objetivo de cobertura; no se interpreta como disponibilidad de APIs, credenciales, consentimiento ni acceso de pruebas. Bold sigue siendo la pasarela elegida; no se presenta como conexión universal de Open Banking. Cualquier persona conserva elegibilidad para la billetera, sin obligación de pertenecer a una empresa o al turismo.

**Incremento codificado:** el CSV neutral admite, además del formato anterior de cinco columnas, el encabezado `transaction_id,date,direction,amount,currency,bank_id,status`. Exige un identificador de banco por extracto y estados explícitos `BOOKED`, `PENDING` o `REVERSED`. El banco es un identificador declarado, no un banco autenticado ni un catálogo oficial. Las referencias se separan por empresa, cuenta y banco; no se persisten identificadores de transacción en claro. `PENDING` y `REVERSED` se muestran sin candidatos y no pueden conciliarse, ni siquiera aportando una resolución manual o agrupando entre lotes. Se aplicó el control a los tres puntos de entrada de revisión; no basta con deshabilitar un botón.

El formato legado conserva su identidad de referencias y permite recuperar revisiones anteriores; no acredita un estado externo verificado. Los importes positivos/COP, fechas no futuras, límite de 5000 bytes/100 filas y tamaño máximo del lote de revisión se mantienen. El estado declarado no constituye recibo bancario ni autorización financiera. No se añaden llamadas a endpoints inventados, depósitos, retiros o pagos simulados.

**Interfaces:** ambos paneles muestran “Pendiente en origen: no conciliable” y “Revertido en origen: no conciliable”; la revisión no se habilita y tampoco se ofrece resolver esas filas como simples diferencias. El backend vuelve a comprobar el bloqueo aunque se eluda la interfaz. Se conservan azul metalizado/azul claro/texto blanco, navegación y dos confirmaciones del titular para movimientos aptos.

**Más de 50 cuentas:** se verificó mediante ORM/API un catálogo de 120 cuentas contables empresariales clasificadas como efectivo, incluida selección de la última y rechazo de acceso ajeno. La clasificación existente soporta hasta 1000 referencias por grupo; esa cota técnica no es un cupo de 50 cuentas por usuario. Esta prueba NO acredita 120 cuentas bancarias personales registradas, números bancarios custodiados, consentimiento ni conexiones activas. El alta y la administración de cuentas personales independientes de empresa siguen siendo desarrollo pendiente y no deben confundirse con el catálogo contable.

**Pruebas:** 162 casos en 11 suites bancarias (incluidos 10 de estados/multicuenta), 30 de contratos/HTTP corporativo, 34 comprobaciones Chromium en ambos paneles y 3 escenarios PostgreSQL16 de consolidación concurrente, liberación y fallo/rollback/reintento. La historia sintética de 20000 líneas conserva sus límites y verificación. La prueba de cambio de identidad de cuenta se ajustó para comprobar su bloqueo temprano y lectura posterior intacta; no se relajaron guardas. En la prueba multicuenta se corrigieron datos duplicados de la fixture y la expectativa del código HTTP de creación; no eran fallas de producto. Los reintentos no se suman al conteo. Evidencias/comandos/hashes en JSON/log existentes.

**Desarrollo pendiente:** gestión de cuentas bancarias personales con custodia y consentimiento; catálogo y adaptadores oficiales por banco/agregador autorizado, sincronización de estados y revocación auténticas, FX, snapshots/carga y cualificación de operación. **Requisitos externos:** perfiles/API/condiciones de cada proveedor, titularidad/consentimiento, acceso autorizado de pruebas y fuentes/recibos legítimos. No hay conexión real a todos los bancos de Colombia ni se afirma que un código CSV habilite una API.

**Estado:** ACC-015 parcial 2/3; no se declara terminada. **79,17% (57/72 hitos), 9/24 tareas cerradas.** Sin commit/push ni habilitación productiva; cambios locales respaldados.

## ACC-016 · Liquidez exacta y consulta corporativa · 2026-11-11

**Falla corregida:** el indicador de liquidez protegía la división final, pero los saldos/sumas previos heredaban el contexto decimal del llamador. Ahora toda la evaluación usa precisión propia mediante el decorador contable existente. Se prueba el mismo resultado con precisión 2, redondeo diferente y trampas de operaciones inexactas activadas. Los saldos, el numerador y el denominador se conservan; un pasivo no positivo produce valor nulo y motivo explícito, no un cero calculado ni infinito.

**Incremento en ambos sistemas:** el resultado identifica moneda, corte económico, unidad “veces”, cuentas fuente, totales por clasificación, revisión de política y referencia del ledger primario bajo el bloqueo empresarial compartido con posteo. Esa referencia describe una lectura coherente actual, no un histórico de publicación inmutable ni una firma independiente. La nueva consulta `quick_ratio` del puente corporativo usa la sesión ERP y vínculo revisado existentes, vuelve a validar autorización y comprueba que el valor concilie con las cuentas y la fórmula. Rechaza fuentes duplicadas, totales alterados, campos privados, contexto incorrecto y falsas afirmaciones de certificación. Ambos backends devuelven el mismo resultado desde el ledger compartido; la revocación de sesión impide la consulta.

La consola Analemática incorpora el selector de liquidez, valor, cuentas/totales, moneda/corte/unidad y advertencia de clasificación declarada. Conserva la estructura y paleta existente. El panel ERP continúa usando el mismo motor y sus controles de edición/historia. Durante Chromium se detectó una referencia de interfaz fuera de su ámbito añadida al integrar la opción; se corrigió y la regresión completa vuelve a exigir cero errores JavaScript.

**Verificación:** 46 regresiones de adaptador/indicadores, 5 pruebas nuevas de precisión/corte/fuentes y ausencia de escritura, 24 regresiones del módulo turístico existente y 4 pruebas nuevas HTTP/contrato corporativo: **79 pruebas Python**. **83 comprobaciones Chromium**: 31 corporativas y 52 del recorrido ERP. Incluyen resultado 3.0000 entre sistemas, trazabilidad visible, denominador cero en API corporativa, rechazo de sesión revocada, diseño móvil y conservación de los flujos anteriores. Las repeticiones y los 17 chequeos del registro de progreso no se suman a las 79. No se modifica ni se desarrolla RAT, ocupación o ADR; la prueba turística preserva las funciones existentes con fixtures desechables.

**Desarrollo pendiente:** cobertura financiera por paquete y sus dimensiones de costos, otros modelos y series/calibración. **Requisitos externos:** fuentes operativas legítimas/independientes y revisión profesional/productiva. RAT/ocupación/ADR permanecen diferidos según decisión previa del usuario. No se deduce exactitud productiva ni autenticidad de datos reales de los fixtures.

**Resultado real:** ACC-016 sigue parcial 2/3; la mejora de liquidez no equivale al cierre de todo el alcance turístico. Se conserva **79,17% = 57/72 hitos, 9/24 tareas cerradas**. Evidencia/comandos/hashes en el JSON/log existentes. Sin commit/push ni habilitación productiva; avances respaldados localmente.

## ACC-017 · Escenarios y evaluación cronológica multiventana · 2026-11-11

**Codificado:** el motor bootstrap existente de 30/90/365 días conserva semilla local, supuestos IID explícitos, percentiles de escenarios y sensibilidad con sorteos comunes. Se aisló su aritmética decimal en entrada, cálculo y agregación: no hereda precisión, redondeo o trampas del llamador. Las pruebas bajo precisión 2 producen los mismos resultados que el contexto normal, sin alterar el generador aleatorio global ni los datos del solicitante.

**Funciones completadas de interfaz:** componente compartido de evaluación de 2–4 ventanas en ERP y Analemática, con caja inicial por ventana, entrenamiento de7–366 días y365 resultados posteriores separados, semilla/trayectorias declaradas y resumen por horizonte. Muestra error terminal medio, conteo de ventanas con resultado dentro del intervalo y superposición; aclara dependencia entre ventanas y falta de calibración productiva. Editar datos invalida el resultado, la pérdida de identidad limpia series y el componente no guarda datos en localStorage. Se conserva el diseño azul metalizado/azul claro y texto blanco. No se incorporan datos ficticios al producto; las series sintéticas existen solo en pruebas.

**Integración y fallas subsanadas:** nuevo comando corporativo de solo lectura, con identidad/CSRF/revalidación del vínculo existentes y contrato que coteja fuentes/fechas/horizontes, errores/medianas/resumen y ausencia de ejecución financiera. Dos ventanas no cabían en el límite genérico de8KB: las rutas analíticas ahora tienen máximo específico de256KB; las escrituras financieras mantienen8KB. Se aplica JSON estricto con rechazo de claves duplicadas/no finitos y profundidad acotada en las rutas analíticas ERP. La prueba demuestra que la ampliación no habilita una escritura financiera grande. Se alineó el proxy de pruebas con el límite real. Durante integración se corrigieron el registro del nuevo comando y una fixture de saltos de línea; las pruebas HTTP/navegador se repitieron con versiones corregidas. El cliente corporativo respeta la cancelación del componente además de su timeout.

**Pruebas finales:**21 regresiones de simulación/sensibilidad/backtesting,4 nuevas de exactitud y cuatro ventanas,7 del parser existente y3 HTTP/contrato/límites: **35 pruebas Python**. **51 comprobaciones Chromium**:20 del nuevo recorrido en ambos paneles y31 de regresión corporativa. Cubren ausencia de filtración de resultados posteriores al entrenamiento, error cero en serie constante de prueba, agregado descriptivo, ventanas superpuestas, identidad, diseño móvil y conservación de lectura/escritura/reversión existentes. Repeticiones y chequeos de progreso no se suman como nuevos casos.

**Rendimiento medido:** máximo técnico del motor con4 ventanas,366 días de entrenamiento,365 resultados posteriores y2000 trayectorias por ventana:2.920.000 sorteos;0,9854s en una ejecución local sintética. Cuerpo JSON compacto132689 bytes. No es p95, medición HTTP/concurrente, SLA productivo ni precisión predictiva. Se conserva el JSON técnico con parámetros/resultado en el registro de evidencia.

**Bloqueo confirmado por el usuario:** no dispone de una serie diaria histórica autorizada de al menos379 días. Ese mínimo permite dos ventanas del formato actual con entrenamiento de7 días y orígenes separados7 días; no es suficiencia estadística para calibrar estacionalidad. Quedan pendientes series legítimas/conciliadas, calibración fuera de muestra, estacionalidad/modelos adicionales, recomendaciones revisadas profesionalmente y cualificación productiva. No se sustituyó el requisito con fixtures ni se afirmó precisión/calibración. Los percentiles no son intervalos de confianza calibrados y el resultado no sirve como autorización de pagos/inversiones.

**Estado real:** ACC-017 continúa parcial2/3; funcionalidad ampliada y probada, aceptación integral pendiente. **79,17% (57/72 hitos),9/24 tareas cerradas.** Sin commit/push ni despliegue productivo. Evidencia y comandos en el JSON/log existentes; cambios locales respaldados.

## ACC-018 · Medición ambiental vinculada a origen · 2026-11-11

**Hallazgo y código:** la unicidad por identificador de actividad no impedía que otro nombre describiera el mismo segmento operativo. Se amplía el contrato con `source_reference` (UUID de orden) y `source_segment` (segmento canónico en mayúsculas), opcionales como pareja para preservar las fuentes históricas. Se valida orden propia/activa y fecha dentro de su ventana en hora Colombia; las órdenes se consultan en lote y se bloquean en orden estable. La segunda confirmación vuelve a comprobar el origen. Una reserva determinista de empresa/orden/segmento se escribe junto con factor, actividad y observación: renombrar actividad o cambiar factor no duplica ese origen y un fallo revierte las reservas nuevas. Reintentar conserva una única observación.

Las correcciones mantienen identificador, fecha, unidad y vínculo de origen; pueden ajustar cantidad/factor mediante el flujo existente, sin reclamar otra vez el segmento. El total corregido sustituye al original. Recuperación/reporte detectan pérdida o alteración de la reserva de origen. Se reforzó la comprobación de dominio, versión y raíz de revisiones, observaciones y reservas, además de payload/huella: no se repara silenciosamente evidencia alterada. La estimación ahora usa un contexto decimal propio incluso para redondear el reparto por pasajero; precisión o trampas del llamador no cambian el cálculo.

**Interfaces y offline:** ambos paneles permiten introducir y muestran orden/segmento; recuperación y corrección conservan esos campos. El borrador cifrado solo admite esa extensión explícita y canónica, conserva el vínculo cifrado y no restaura autorizaciones. Al reconectar, el servidor vuelve a validar la orden; guardar un borrador no acredita titularidad, ejecución física ni autorización financiera. Se conservaron diseño azul metalizado/azul claro/texto blanco y navegación. No se desarrollaron RAT, reservas ni ADR.

**Verificación final:**78 pruebas en6 suites ambientales/ESG/origen y2 HTTP corporativas: **80 pruebas Python**. **118 comprobaciones Chromium/WebCrypto**:48 del recorrido ambiental en ambos paneles,46 offline y24 criptográficas. Cubren renombrado del mismo segmento, factor distinto, duplicado dentro de la evaluación, origen inexistente, cambio de vigencia/actividad entre confirmaciones, reserva eliminada/metadatos alterados, corrección de cantidad con una sola reserva, precisión decimal, recuperación sin repetir autorizaciones y conservación cifrada del origen. El ensayo offline se corrigió para usar una orden propia provisionada en la fixture al reconectar; no se relajó el rechazo de referencias inexistentes. Repeticiones y17 chequeos de progreso no se suman a esos80 casos.

**Límites:** el vínculo es declarado y opcional. No resuelve automáticamente alias de segmentos ni duplicados semánticos de actividades históricas sin origen; requiere un catálogo de fuentes/segmentos legítimo y revisión. Las reservas evitan duplicar observaciones vinculadas, no prueban que una actividad haya ocurrido ni convierten emisiones en un crédito negociable. El registro detecta inconsistencias, sin acreditar resistencia frente a un administrador de base hostil ni cualificación PostgreSQL/concurrencia productiva completa.

**Requisito externo confirmado:** el usuario indicó que no hay factores con fuente/versión/unidad documentadas ni política u obligación ambiental revisada por contador. Por ello no se reconocen pasivos o reservas financieras automáticas, no se emiten compensaciones/créditos ni se afirma certificación ESG. Permanecen pendientes autenticidad/aplicabilidad de factores, soportes, obligación/compensación legítimas y aceptación profesional/productiva.

**Estado:** ACC-018 parcial2/3. Funcionalidad implementada/probada y requisitos externos separados; sin cierre integral ficticio. **79,17% (57/72 hitos),9/24 tareas cerradas.** Cambios respaldados localmente; sin commit/push ni producción habilitada. Evidencia/comandos/hashes en el JSON/log existentes.

## Auditoría y subsanación transversal ACC-001–018 · 2026-11-11

**Base revisada:** árbol de trabajo local de `codex/conectado-20261110`, sobre `c745d0a58523ab3cf5742480e2e7d45b169e705e`. Incluye avances locales posteriores; esta revisión no afirma que estén publicados en main. No se hicieron commits, push, migraciones de bases del cliente ni acciones en cuentas reales.

**Fallas reproducidas y subsanadas:**

1. **ACC-017, integridad del resultado analítico.** El contrato corporativo comprobaba formato y algunas sumas, pero aceptaba resultados que no correspondían a los importes de entrenamiento/resultados posteriores enviados, una trayectoria negativa falsa, fracciones de déficit incompatibles con su conteo y un promedio de error por ventana alterado. Cuatro pruebas de regresión fallaron antes de la corrección. Ahora se cotejan las huellas canónicas de ambas series, caja inicial/cierre, saldos realizados y trayectorias, proporciones y conteos acumulados por horizonte, y medias de error. No se vuelve a ejecutar Monte Carlo en el puente: el cotejo es lineal sobre las observaciones declaradas, sin añadir simulaciones ni autorizar operaciones financieras. Se preservan importes enteros válidos y cálculo independiente del contexto decimal del llamador. Nueve casos específicos y los recorridos HTTP/navegador cubren el contrato reforzado.
2. **ACC-017/experiencia ERP, identidad de componentes.** `CashScenarios` y `CashWindows` tenían la misma clave de React entre hermanos. El recorrido completo reprodujo formularios duplicados y selectores ambiguos después de la actualización de la empresa. Cada componente tiene ahora una clave distinta que conserva usuario/empresa; se verifica que exista un único formulario de cada tipo y que cambiar de empresa borre los valores. Se preservan navegación, identidad azul metalizado/azul claro/texto blanco y adaptación móvil.

La instalación/recuperación BYOS necesitó pruebas fuera del aislamiento IPC de TestClient. El primer intento aislado agotó tiempo sin concluir; se repitió con sockets locales autorizados. Ese intento no se contabiliza como aprobado ni como una falla del producto. La falla inicial del navegador sí era de producto y se conserva como evidencia anterior a la corrección.

### Resultado por tarea, conservando los criterios originales

| Tarea | Revisión técnica y pruebas ejecutadas | Estado y pendiente real |
|---|---|---|
| ACC-001 | Exactitud monetaria, balance, cuenta ajena/inactiva y período ambiguo; SQLite/PostgreSQL/HTTP. | 3/3 originales; producción no acreditada. |
| ACC-002 | UUID, inmutabilidad ORM/SQL, padre cacheado y operaciones masivas. | 3/3 originales; no demuestra resistencia a dueño SQL hostil. |
| ACC-003 | Idempotencia, payload distinto, rollback/reintento y outbox atómico, incluida concurrencia. | 3/3 originales; publicación Kafka/consumidor externo fuera de esta acreditación. |
| ACC-004 | Cierre/posteo/reversión concurrentes y orden de bloqueo PostgreSQL. | 3/3 originales; legados/migración del cliente y carga productiva pendientes globales. |
| ACC-005 | Vínculo explícito vigente, actor/empresa/período, rechazo entre identidades y revalidación del despacho. | 3/3 originales; SSO/provisión y legalidad de identidad externa no acreditados. |
| ACC-006 | Moneda/tasa/fuente/vigencia declaradas, precisión y ausencia de fallback automático. | 3/3 originales internos; autenticidad externa de tasas y revisión profesional pendientes globales. |
| ACC-007 | Hash, cambios de identidad/importe, guardas SQL y diagnóstico. | 3/3 originales internos; PostgreSQL desechable, sin certificar roles/migración productiva. |
| ACC-008 | Estados y solicitudes CRM/reserva versionadas, idempotencia y ausencia de cobros/acuses inventados. | 3/3 originales; no acredita factura aceptada por DIAN. |
| ACC-009 | Borrador fiscal, rutas corporativas, controles de laboratorio y preparación de documento. | 2/3. Faltan perfil/anexo vigente, representación fiscal, firma/custodia y transporte/acuses reales. Usuario aplazó integración directa DIAN. |
| ACC-010 | Sobre cifrado cliente, recuperación/rotación y rechazo de texto claro; pruebas de ambos paneles y recuperación PostgreSQL/HTTPS local. | 3/3 del alcance portátil original; hardware y custodia física no acreditados. |
| ACC-011 | Contratos OAuth/BYOS, configuración privada y recuperación/carga local. | 2/3. Faltan flujo nativo/UI completo y cuentas/apps OAuth/consentimientos, permisos y revocación reales de Drive/OneDrive; usuario confirmó que no están preparados. |
| ACC-012 | Aptitud restringida, EPP, descanso, peligros/riesgo y despacho genérico; guardas/migración PostgreSQL desechable. | 2/3. Faltan procesos especializados/interfaces, legitimidad profesional/datos y cualificación completa de concurrencia/despliegue. |
| ACC-013 | Nómina declarada, correcciones, novedades, trazabilidad y atribución de costos sin doble gasto/provisión. | 2/3. Faltan vínculo individual de minutos a jornadas, calendario/clasificación laboral completa, otras novedades y habilitación profesional/DIAN nómina. |
| ACC-014 | IVA/retenciones internos, políticas originales, devoluciones/contrapartidas y registro explicable en ambos paneles. | 2/3. Faltan cobertura normativa/operacional completa, períodos/multicuenta, fuentes legítimas y contraste oficial DIAN. |
| ACC-015 | Estados externos declarados, rechazo de pendientes/revertidos, agrupación/parciales/períodos/historia y aislamiento. | 2/3. No hay conexión a todos los bancos ni alta/custodia de más de50 cuentas bancarias personales; las120 cuentas del ensayo son cuentas contables empresariales. Faltan conectores/consentimientos y fuentes auténticas. |
| ACC-016 | Ratio exacto con fuentes/moneda/corte/unidad, denominador no calculable y concordancia ERP/corporativo. | 2/3. Faltan dimensiones/ratios por paquete y aceptación de fuentes; RAT/ocupación/ADR siguen aplazados por el usuario. |
| ACC-017 | Semillas/horizontes/sensibilidad, ventanas separadas, integridad reforzada y formularios sin duplicación. | 2/3. Usuario no dispone de serie histórica autorizada; faltan calibración/modelos adicionales y recomendaciones revisadas. |
| ACC-018 | Factor/unidad/vigencia, reservas de origen, correcciones sin doble conteo, metadatos, interfaces y borrador cifrado. | 2/3. Usuario no dispone de factores documentados ni obligación revisada; faltan autenticidad/catálogo de segmentos y reconocimiento válido. Sin pasivos/créditos/compensaciones automáticos. |

**Verificación final de esta auditoría:** 1030 pruebas Python en89 suites (60 funcionales,28 corporativas/HTTP y1 contrato nuevo),453 comprobaciones en11 suites Chromium/WebCrypto, y13 suites PostgreSQL desechables aprobadas. Los17 chequeos del registro de progreso se verifican aparte. Los conteos incluyen únicamente ejecuciones finales aprobadas, sin sumar reintentos ni resultados históricos. Bases y usuarios de prueba desechables; no sustituyen validaciones profesionales, bancarias, cloud o de dispositivos. Los comandos, resultados y hashes se agregan al JSON/log de evidencia ya existentes, bajo `audit_tasks_1_18`.

**Estado conservado:** **79,17% (57/72 hitos);9/24 tareas aceptadas integralmente según la matriz original**. Dentro de las18 revisadas hay9 aceptadas y9 parciales. Repetir pruebas y corregir estas fallas no completa criterios externos ni genera crédito adicional. Producción no habilitada; avances locales respaldados y sin publicación Git en esta entrega.


## ACC-019 · Trazabilidad de soportes y origen en reportes ESG · 2026-11-11

**Desarrollo realizado:** el reporte por corte económico/de conocimiento ahora incluye la huella del soporte efectivo de la actividad y, cuando existe, la orden/segmento operativo original. Al corregir una cantidad, el soporte cambia con la revisión efectiva al corte: consultar el corte anterior conserva el soporte anterior. Orden/segmento permanecen inmutables. La pérdida o alteración de su reserva impide exportar; no se reconstruye evidencia automáticamente. Los formatos históricos sin vínculo siguen siendo legibles.

Ambos paneles muestran y exportan esa trazabilidad enJSON/CSV, con la misma huella integral del reporte. El frontend rechaza campos inesperados, incluidos datos privados agregados a una actividad, y pares de origen incompletos, aunque un emisor recalcule una huella válida. Se conserva el descarte de datos al editar/cambiar identidad y la identidad azul metalizado/azul claro/texto blanco, sin rediseñar la navegación. Las rutas ESG anteriores mantienen compatibilidad.

**Fallas subsanadas:** los reportes y contrato corporativo heredaban trampas/redondeo decimal del llamador; ahora calculan en un contexto propio, probado con una cantidad fraccionaria cuyo producto exige redondeo. Los valores anidados no válidos de marco/límite podían producir errores de tipo: se rechazan como errores de dominio. No se modificaron mediciones históricas ni se reconocieron obligaciones ambientales o movimientos financieros.

**Verificación:**102 pruebas Python en10 suites (84 funcionales ambientales/ESG/origen y18 de contrato/HTTP/recuperación corporativa),52 comprobaciones Chromium de ambos paneles y17 chequeos de progreso aparte. Incluyen corte antes/después de corrección, soporte efectivo, origen, reserva eliminada, precisión/trampas decimales, mapeo inválido, exportación con huella verificable, campos privados/origen incompleto rechazados, resultados vacíos explícitos y vista móvil. Los reintentos no se suman al conteo. Pruebas con fuentes sintéticas locales, no certificación ambiental ni cualificación PostgreSQL/concurrencia productiva nueva. Comandos/hashes en el registro existente, entrada `acc019_effective_source_trace`.

**Alcance pendiente:** catálogo legítimo de mediciones/segmentos, duplicados semánticos fuera del vínculo declarado y snapshots/volumen/concurrencia revisados. **Requisitos externos:** el usuario confirmó que no hay factores documentados ni política/obligación revisada por contador. La autenticidad de factores/soportes y la aplicabilidad de referencias GRI/SASB requieren evidencia y revisión profesional; no se infieren de una huella, un mapeo escrito o una prueba sintética. No se emiten créditos/compensaciones ni se afirma certificación ESG.

**Estado real:** ACC-019 continúa **2/3, parcial**, con el incremento ampliado y probado; aceptación integral pendiente. Progreso global **79,17% (57/72 hitos),9/24 tareas aceptadas**. No hay crédito adicional por reforzar una tarea ya probada. Cambios respaldados localmente; sin commit/push ni producción habilitada.


## ACC-020 · Consultas contables acotadas y verificables · 2026-11-11

**Desarrollo:** se amplía el reconocedor determinista en español con liquidez ácida, además de rentabilidad y cola de facturación. Cada herramienta recibe la empresa resuelta por identidad/permisos del backend; el payload no admite elegir otro tenant, SQL ni acciones. Liquidez exige corte explícito; rentabilidad exige intervalo ordenado/acotado; la cola no acepta filtros de fecha sin implementar. Preguntas desconocidas, instrucciones de pago y combinaciones no soportadas se rechazan, sin intentar ejecutar código ni SQL generado.

**Hallazgo subsanado:** el puente corporativo comprobaba banderas de lectura pero no cotejaba suficientemente intención, fuente y cifras. Ahora comprueba intención correspondiente a la pregunta, esquema acotado, empresa, fechas, origen primario y referencia del ledger; concilia cuentas/ingresos/gastos/resultado/margen con precisión propia. La liquidez utiliza su contrato de clasificación/fuentes/aritmética existente. La cola valida conteos y mantiene aceptación DIAN explícitamente no verificada: transporte no equivale a acuse fiscal. Campos privados inesperados o cambios de fuente, cifras o intervalo se rechazan.

**Interfaces:** nueva consulta de liquidez en ERP y en el asistente corporativo; muestra fuente, moneda, corte y valor/no calculable. Ambas pantallas comprueban aritmética exacta del resultado neto antes de mostrarlo. Editar consulta/empresa invalida respuestas; el asistente corporativo borra también pregunta y fechas al cerrar sesión, cambiar token u ocultar/abandonar página. Se mantienen la paleta azul metalizado/azul claro/texto blanco y navegación; sin cambios en RAT/ADR ni permisos de la billetera.

**Evaluación reproducible:** dataset técnico versionado de41 ejemplos sintéticos, con consultas soportadas, acentos/mayúsculas y entradas no admitidas/inyección. El verificador compara ambos reconocedores, exige igualdad de contratos y cobertura de los alias autorizados. Es regresión de un reconocedor determinista, no precisión de un modelo fundacional ni un ensayo con usuarios reales. No se consume una API de IA ni se envían datos contables a un modelo externo.

**Pruebas finales:**78 pruebas Python (3 de evaluación/contrato,6 de consultas,7 de parser,46 del adaptador y16 HTTP de consulta/liquidez/integración);88 comprobaciones Chromium (54 ERP y34 corporativas), incluidos resultados alterados y borrado de entradas tras logout. Los41 ejemplos son parte de las3 pruebas de evaluación, no41 pruebas adicionales.17 chequeos de progreso verificados aparte. Todos los conteos corresponden a las ejecuciones finales aprobadas y no suman reintentos. Evidencia/comandos/hashes en `acc020_scoped_query_tools` del JSON/log existentes.

**Pendiente y estado real:** aún no hay integración/evaluación de un modelo local o privado para esta función; el reconocedor y sus herramientas no lo sustituyen. Faltan dataset autorizado representativo y evaluación del modelo, voz, ampliación revisada de herramientas/roles y cualificación de privacidad/rendimiento/dispositivos. No se afirma99,8% de precisión, consulta libre universal ni aceptación integral. ACC-020 permanece **parcial2/3**; progreso global **79,17% (57/72 hitos),9/24 tareas aceptadas**. Cambios respaldados localmente, sin commit/push ni producción habilitada.


## ACC-021 · Ensayo supervisado recuperable y cancelación idempotente · 2026-11-11

**Desarrollo:** se añade consulta de estado por identificador UUID, sin volver a ejecutar confirmaciones ni la simulación. Revalida actor/vínculo vigente, empresa, metadatos de cada evento, intención/huella y evidencia de las etapas. Muestra estado preparado, primera/segunda confirmación, simulado, vencido o cancelado. Las confirmaciones existentes son evidencia histórica; `confirmations_restored=false` y `usable_as_payment_authorization=false` permanecen explícitos. El estado leído no es un permiso para pagar ni crear un trabajo de escritorio.

**Hallazgos subsanados:** cancelar otra vez una referencia cancelada antes fallaba como operación cerrada; ahora el reintento valida el evento y devuelve el mismo resultado sin duplicarlo. Se puede recuperar/cancelar una referencia vencida sin habilitar nuevas confirmaciones. El cargador vincula también el UUID interno de la intención con la referencia del evento; cambiarlo incluso junto con una huella recalculada se rechaza. La lectura detecta segunda confirmación huérfana, metadatos cambiados y cancelación/simulación alteradas. El puente corporativo tiene contrato acotado para estos estados y no restaura confirmaciones.

**Interfaces en ambos sistemas:** panel compartido azul metalizado/azul claro/texto blanco con contexto resuelto por backend, nueva referencia, intención/soporte declarados, revisión de preparación, dos botones de confirmación separados, frase exacta de importe/destinatario e impacto adicional. Editar la intención invalida la preparación y las casillas; recuperar tras recarga conserva evidencia del servidor, sin marcar impacto ni cancelación. Un resultado incierto exige recuperar la misma referencia antes de reintentar. La interfaz permite cancelar y descartar datos locales; no contiene un botón de pago real ni datos bancarios inventados. La referencia del beneficiario y huella del soporte son declaradas, no acreditación bancaria.

**Verificación final:**75 pruebas Python (18 del flujo previo,6 de recuperación/alteración,46 del adaptador y5 HTTP corporativas),120 comprobaciones Chromium (32 del flujo nuevo en ambos sistemas y88 de regresión ERP/corporativa), más4 escenarios PostgreSQL16 desechables con rol sin DDL: preparación simultánea, segunda confirmación simultánea, carrera cancelar/simular y reintentos concurrentes de cancelación. Mantienen evidencia única, cancelación efectiva y ausencia de nuevos asientos/pagos.17 chequeos de progreso aparte. No se suman reintentos ni se presentan estos escenarios como cualificación de un ejecutor bancario/productivo. Comandos/hashes en `acc021_recoverable_supervised_rehearsal` del JSON/log existentes.

**Pendiente:** implementar y validar el trabajador de ejecución con permisos mínimos e integración agent-desktop/Open Duet; proveedor/cuenta/beneficiario/soportes y consentimientos legítimos, autorizaciones resistentes a suplantación, recibos/acuse auténticos y recuperación de resultados inciertos. Faltan cualificación de carga/concurrencia de ejecución real, identidad/dispositivos e infraestructura objetivo y aceptación profesional/productiva. No se contactó a Bold/bancos ni se ejecutaron operaciones reales. El flujo existente de reembolso interno financiado se conserva; este ensayo no lo sustituye ni le concede permisos.

**Estado real:** ACC-021 permanece **parcial2/3**. Progreso global **79,17% (57/72 hitos),9/24 tareas aceptadas**. Las pruebas nuevas refuerzan el incremento acreditado y no cierran la ejecución real. Cambios respaldados localmente; sin commit/push, trabajos de escritorio ni producción habilitada.


## ACC-022 · Capturador ambiental con arranque offline y gestión cifrada · 2026-11-11

**Desarrollo real:** capturador independiente en `/contabilidad-offline/`, enlazado desde ERP/Analemática y generado desde una sola fuente para ambos orígenes. Formulario de medición, factor, soporte y origen opcional; importación estructurada como opción técnica. Después de habilitarlo con conexión, arranca en frío sin red y permite guardar/desbloquear borradores. No es una copia offline de todas las pantallas del ERP. El UUID empresarial declarado no autentica titularidad offline; la revisión online existente vuelve a comprobar usuario, empresa y fuentes.

**Caché restringida:** worker de alcance exclusivo a esa ruta. VerificaSHA-256, tipo/tamaño y carácter público de cuatro archivos estáticos antes de almacenarlos; sus descargas omiten credenciales y rechazan respuestas privadas/no-store, redirecciones e integridad alterada. No se cachean APIs, sesiones ni administración. Si falla la instalación, no se presenta como lista para operar offline ni se crea caché parcial. Los borradores permanecen cifrados enIndexedDB, separados de la caché pública.

**Almacén:** catálogo de identificadores/versiones por empresa sin desbloquear contenido; eliminación con contraseña, versión esperada y comparación transaccional contra cambios de otra pestaña. Límites de100 borradores por empresa y500 totales por origen/navegador. Alcanzarlos rechaza altas sin eliminar datos; todavía permite actualizar borradores existentes. Exportación/restauración cifrada, rotación de contraseña y reanudación online supervisada se conservan. No hay evicción automática; el navegador sí puede desalojar almacenamiento y la interfaz indica conservar una copia cifrada y contraseña separadas. No se guardan contraseñas ni se restauran autorizaciones.

**Bloqueos encontrados y corregidos:** el preview con autenticaciónHTTP impedía descargar archivos sin credenciales; se publican únicamente cinco rutas estáticas exactas del capturador, sin abrir panel/API ni archivos desconocidos. La redirección del directorio apuntaba al puerto interno del contenedor: ahora es relativa. Laumask restrictiva producía archivos públicos ilegibles para un usuario web distinto: el generador fija0644 en estos archivos de código público y0755 en su directorio, sin cambiar llaves ni directorios privados. Los despliegues web y el preparador corporativo incluyen el paquete.

**Verificación final:**100 comprobaciones Chromium/WebCrypto (20 del capturador,34 de cifrado/catálogo/conflictos/cuotas y46 de los dos paneles con reconexión),4 pruebas Python de empaquetado y14 comprobaciones de aislamiento con Nginx real desechable. Incluyen arranque sin red, desbloqueo explícito, ausencia de contenido/contraseña en la copia cifrada, rechazo de recurso alterado/privado, carrera guardar/eliminar, cuotas sin pérdida de datos, conservación de autorizaciones no restauradas, formularios móviles y publicación sin abrir panel/API. Nginx prueba las rutas generadas en un gateway aislado con autenticación de prueba; no acredita el despliegue completo niTLS productivo.17 chequeos de progreso aparte. Evidencias/comandos/hashes en `acc022_cold_offline_capture` del JSON/log existentes; reintentos no sumados.

**Pendientes:** más dominios de captura y colas/sincronización ampliadas, conflictos específicos por dominio y versiones/recuperación/retención operativa revisadas. No se aplica CRDT genérico a importes, autorizaciones o asientos. Faltan SQLite/custodia nativa y pruebas físicas Android/iOS/escritorio, además de carga, actualizaciones y recuperación en infraestructura objetivo. La captura web ambiental y la simulación de red de Chromium no cierran estos requisitos. No se preparan ni liquidan pagos offline.

**Estado real:** ACC-022 continúa **parcial2/3**; progreso global **79,17% (57/72 hitos),9/24 tareas aceptadas**. Cambios respaldados localmente; sin commit/push ni producción habilitada.


## ACC-023 · Medición HTTP y optimización de contexto con controles intactos · 2026-11-11

**Código y fallas subsanadas:** estadísticas con contexto decimal propio y objetivo expresado como decimal exacto; no se aceptan booleanos/float/valores ilimitados como objetivo o duración. Se conservan latencias fallidas, colas, p50/p95/p99/máximo y conteos crudos fuera del objetivo, sin ocultarlos por redondeo. El evaluador distingue cobertura/abstenciones y exactitud sobre todas las muestras; predicciones suministradas no acreditan que se ejecutó un modelo. El benchmark ORM ahora conserva intentos fallidos, etapas omitidas e invariantes y escribe el informe antes de terminar con error; no pierde toda la evidencia al fallar una operación.

**Hallazgo de carga:** el modo anterior agotó el límite del ERP en2 de80 solicitudes de prueba y lo presentaba como503. Ahora el puente conserva429 y unRetry-After numérico acotado, con mensaje propio y sin copiar el cuerpo del ERP. No hay reintentos financieros automáticos ni se desactivaron/aumentaron cuotas para aprobar pruebas.

**Optimización implementada:** contexto opcional de sesión/actor/empresa/CSRF en una sola petición antes del comando, y lectura más identidad en una sola petición para reportes. Se mantienen comprobación de empresa y actor del vínculo, sesión web/MFA, CSRF, autorización antes del despacho y revocación después de obtener resultados. La lectura agrupada conserva importes como texto decimal y contratos originales; no sustituye por float las cifras del motor. Se probaron el modo anterior y el nuevo con consultas, compras/IVA, contabilización/contrapartida, resultado perdido, confirmaciones e identidad revocada.

La opción es `CORPORATE_LEDGER_COMBINED_CONTEXT_ENABLED=1` en el backend corporativo, una vez disponibles los nuevos endpoints del ERP. Por defecto sigue el camino anterior; desactivar la variable permite regresar a él. Solo se habilitó en fixtures y benchmarks de esta entrega, sin cambiar configuración productiva ni credenciales. No se eliminan controles para ahorrar tiempo ni se cachean autorizaciones entre peticiones.

**Medición final reproducible:**100 compras sintéticas,400 operaciones ORM; tres perfiles HTTP de20 intentos por cada uno de cuatro flujos:240 intentos HTTP en total. Las fuentes no cambiaron durante los perfiles y su hash coincide entre los cuatro informes. Se conservaron dos429 en el perfil anterior; los160 intentos de los perfiles unificados terminaron sin errores. Código de salida0 del recolector significa captura/invariantes correctas, no cumplimiento automático de250ms.

| Flujo HTTP,20 intentos por perfil | p95 anterior,4 clientes (ms) | p95 unificado,4 clientes (ms) | Máximo unificado,4 clientes (ms) | p95 unificado,1 cliente (ms) |
|---|---:|---:|---:|---:|
| trial_balance | 266.799 | 213.257 | 214.684 | 60.092 |
| profitability | 360.706 | 197.143 | 202.183 | 54.691 |
| quick_ratio | 281.984 | 279.038 | 290.720 | 86.069 |
| commercial_queue | 259.986 | 291.979 | 330.501 | 84.100 |

El gateway de medición HTTP se serializa expresamente porque la fixture comparte sesión SQLAlchemy;4 clientes miden espera/contención ante ese servidor, no un pool ASGI/PostgreSQL productivo. El primer tramo usa HTTP loopback real, ASGI se procesa dentro de la fixture y el tramo hacia ERP usaHTTP/WSGI real. Se declaran por separado el informe previo de preparación, la provisión/login y el control anónimo, que no se contabilizan como intentos medidos. Se conservan duraciones en nanosegundos y estados HTTP por intento; estadísticas recalculadas contra esos datos. No se seleccionó un origen ni una base del cliente.

**Objetivo todavía incumplido:** con4 clientes, liquidez y cola comercial conservan muestras superiores a250ms. En la última medición ORM el posteo tuvo máximo264.305ms (1 muestra fuera de objetivo) y el registro tributario máximo448.206ms (9 muestras fuera). No se eligió una repetición anterior más rápida para declarar éxito. Son mediciones sintéticas en hardware cloud compartido; no son latencia completa de un evento de negocio hasta el ledger ni unSLA independiente del equipo. El clasificador sigue `NOT_EVALUATED`: no hay precisión99,8% acreditada.

**Verificación:**65 pruebas Python aprobadas (13 de métricas,4 del contrato de medición y48 de HTTP/seguridad/integración),34 comprobaciones Chromium del panel con la opción unificada y17 chequeos de progreso aparte. Los640 intentos de rendimiento se informan como observaciones, no como640 tests adicionales aprobados. Informes completos, comandos, muestras/hashes y resultado de cada perfil incorporados en `acc023_measured_context_optimization` del JSON/log existentes.

**Pendientes y estado:** carga representativa, optimización/cualificación sostenida en infraestructura objetivo y PostgreSQL/pools, medición evento-a-ledger/dispositivos/proveedores y evaluación independiente; modelo real y dataset autorizado representativo para calidad/privacidad. ACC-023 continúa **parcial2/3**. Progreso global **79,17% (57/72 hitos),9/24 tareas aceptadas**. Avances respaldados localmente; sin commit/push ni producción habilitada.


## ACC-024 · Recuperación y fronteras de archivos/permisos · 2026-11-11

**Implementado y probado:** lectura de claves/archivos regulares limitada y sin seguir enlaces mediante descriptores POSIX, validación de permisos sobre el archivo abierto y rechazo de FIFO sin bloqueo. Creación exclusiva anclada al directorio, comprobación de sustitución del padre, sincronización de archivo/directorio y limpieza que conserva un archivo reemplazado por otro inode. Cabecera autenticada estricta: campos exactos, tipos sin booleanos como enteros, SHA-256, fecha UTC, sin duplicados ni números no finitos. Se conservan restauración a destino nuevo, fuente intacta, recuperación de WAL y exclusión deliberada de llaves de aplicación.

**Hallazgos reales subsanados:** el rol limitado fallaba al bloquear monedas y el catálogo relacionado durante la revisión FX. El perfil declarativo incorpora únicamente UPDATE(id), además de SELECT, para estos bloqueos; no ejecuta GRANT automáticamente ni concede edición de atributos. El contrato PostgreSQL ahora verifica el rechazo de cambios de nombre en ambos catálogos. La prueba antigua necesitaba SELECT de cuentas y usaba un posteo FX directo que el motor rechaza correctamente; se actualizó a revisión y segunda confirmación, conservando los controles del motor.

**Verificación reproducible:** `python -m unittest discover -s BACKEND/deployment/tests -p test_encrypted_backup.py -v`:20 pruebas; con PYTHONPATH de deployment/tests, `python -m unittest accounting_sql_check schema_readiness_check -v`:22 pruebas. `python BACKEND/deployment/tests/mfa_postgres_check.py`:PostgreSQL16 Docker desechable,52 escenarios contables, backup/restore a otra base y comparación de tablas/filas, secuencias, funciones, triggers, columnas, restricciones e índices; integridad, protecciones SQL y origen intacto verificados. Incluye restauración MFA con las llaves originales de la fixture, separadas del archivo. Las17 pruebas del registro son controles de coherencia adicionales, no hitos funcionales. Los intentos anteriores fallidos por permisos/fixture quedaron identificados; no cuentan como pruebas aprobadas. Evidencia y hashes en el registro técnico existente, clave `acc024_restore_and_file_boundaries`.

**Alcance pendiente y requisitos externos:** no se acredita recuperación integral del cliente: faltan documentos y llaves/medios legítimos, todos los roles/rutas y funciones privilegiadas/RLS, aceptación independiente y mediciones RPO/RTO acordadas en infraestructura objetivo, despliegue y reversión reales. El CLI endurecido requiere POSIX; no se cualifica una variante Windows nativa. La instantánea SQLite viva todavía abre base/WAL por ruta: el directorio fuente debe ser privado y estable, no se declara resistente a sustitución hostil de esa fuente. El dump contable PostgreSQL de prueba es temporal y privado; no constituye una solución de custodia productiva cifrada.

**Estado:** ACC-024 conserva2/3, sin aceptación integral. Total57/72=79,17%;9/24 tareas aceptadas. Producción deshabilitada. Cambios locales respaldados; sin commit ni push en esta entrega.


## Evaluación integral ACC-001 aACC-024 · 2026-11-11

**Resultado verificable:**24 tareas contrastadas con matriz/criterios/registros;9 aceptadas dentro del alcance original y15 parciales. Se mantiene57/72=79,17%; ninguna repetición de prueba o corrección documental añade crédito. El estado actual por tarea está en la tabla siguiente; los cortesR01–R20 anteriores conservan su contexto histórico. Producción sigue deshabilitada.

**Fallas subsanadas en código:** las vistas contables antiguas ahora validan el vínculo vigente administrador/empresa, revalidan al terminar y rechazan contexto/cabecera discordantes. Interpretan fechas canónicas, rechazan duplicados/intervalos invertidos y devuelven errores sanitizados/no-store. Los saldos usan UUID, catálogo explícitamente acotado a empresa y movimientos contabilizados/valorados en la base principal; conservan cuentas sin movimiento y reemplazan el agregado por cuenta por una sola consulta agregada. Los ratios respetan el mes del corte, usan decimales exactos y muestran no calculable ante denominador no positivo. Flujo de caja no configurado responde501 explícito, sin ceros inventados. Se preservan rutas y estructura visual; no se cambió el RAT.

**Fallas de verificación subsanadas:** el perfil contable omitía contratos nuevos; ahora incorpora todos los módulos contables y schema-readiness, con pruebas de cobertura del catálogo y ausencia de duplicados. La tanda corporativa única agotaba180s: ahora31 módulos tienen procesos, logs y límites independientes. La prueba de atestación no creaba OutboxEvent ni obtenía el consentimiento actual del destinatario; se corrigió su fixture y se comprueba rechazo sin consentimiento, aceptación con consentimiento y posterior rechazo por revocación, sin tocar los controles de producción. ESG figurabaPENDIENTE pese a2/3 hitos; se corrigió aPARCIAL, sin cierre ni crédito adicional.

**Pruebas ejecutadas:**1778 pruebas de regresión contable/instalación en149 suites/pasos, todos aprobados sin skips; incluye los13 casos nuevos de presentación (antes fallaban11 casos originales).17 pruebas del runner,17 del progreso y4 del paquete offline adicionales.14 suites Chromium con563 comprobaciones declaradas,11 contratos PostgreSQL desechables y14 controles Nginx aprobados.12 suites transversales de seguridad completadas; su conteo incluye wrappers de pruebas ya cubiertas y no se suma como cobertura única. Dependencias:sin requisitos incompatibles según pip check. Instalaciones ERP/Turismo nuevas y sus controles completados; no migración de datos históricos de clientes.

**Trazabilidad:** la pasada contable definitiva conservó un manifiesto estable y hashes verificados. Después cambiaron solo dos módulos de prueba: atestación y control de instalación. Se repitieron28+13+13 pruebas sobre los archivos persistidos y se comprobó que todas las fuentes de aplicación y los demás módulos permanecían idénticos. El primer control de instalación Turismo contenía una omisión explícita del caso ERP: se conserva ese resultado y se sustituye mediante una nueva prueba negativa404, no reinterpretando un skip como aprobado. La primera tanda con timeout, la pasada serial sustituida/cancelada y los intentos fallidos de diagnóstico no se presentan como aprobaciones finales. Informes, comandos, hashes, manifiesto y detalle de las24 tareas en el registro técnico existente, clave`audit_acc001_acc024`. No hay validación de hardware/DIAN/bancos/cloud reales ni prueba independiente de seguridad por estas fixtures.

| Tarea | Estado en criterios originales | Implementado y contrastado | Desarrollo/requisitos pendientes |
|---|---|---|---|
| ACC-001 | Aceptada3/3 | Validación exacta y aislamiento; regresiones ORM/PostgreSQL. | Ninguno en el criterio original; cualificación productiva separada. |
| ACC-002 | Aceptada3/3 | UUID y guardas ORM/SQL; intentos de mutación rechazados. | Ninguno en el criterio original; operadores privilegiados no quedan inmunizados. |
| ACC-003 | Aceptada3/3 | Idempotencia, conflicto de payload y outbox atómicos. | Ninguno en el criterio original; transporte externo se evalúa en sus tareas. |
| ACC-004 | Aceptada3/3 | Cierre/posteo/reversión y orden de bloqueos PostgreSQL. | Ninguno en el criterio original; carga productiva pendiente. |
| ACC-005 | Aceptada3/3 | Vínculo empresa/actor vigente; vistas antiguas ahora lo verifican explícitamente. | Ninguno en el puente original; administración global/roles productivos no acreditados. |
| ACC-006 | Aceptada3/3 | Cotización FX revisada, dos confirmaciones y bloqueo de fallback. | Ninguno en la validación interna original; autenticidad de fuentes FX pendiente. |
| ACC-007 | Aceptada3/3 | Hashes y guardas SQL; detección de alteraciones y restauración. | Ninguno en los criterios originales; auditoría independiente/privilegios reales pendiente. |
| ACC-008 | Aceptada3/3 | Contrato CRM/reserva y estados sin inventar cobro/acuse. | Ninguno en el contrato original; emisión DIAN pertenece aACC-009. |
| ACC-009 | Parcial2/3 | Borradores y fuentes CRM/reserva, límites fiscales e interfaces probados. | Desarrollo fiscal/custodia/transporte; certificado, resolución, test set y acuses DIAN reales. Integración directa aplazada por el usuario. |
| ACC-010 | Aceptada3/3 | Cifrado cliente, AAD, recuperación/rotación y rechazo de alteraciones. | Ninguno en el protocolo cliente original; custodia física y aceptación productiva separadas. |
| ACC-011 | Parcial2/3 | Adaptadores BYOS/OAuth y fallos/reintentos locales. | Aplicación OAuth, cuenta/grants legítimos Drive/OneDrive, revocación/recuperación con proveedor real; no disponibles. |
| ACC-012 | Parcial2/3 | Aptitud cifrada, EPP, descanso/riesgo por trabajador y guardas. | Completar procesos especializados, interfaces/conexión operacional y concurrencia/migración; evidencias profesionales y dispositivos reales. |
| ACC-013 | Parcial2/3 | Nómina declarada, correcciones y trazabilidad de costos/jornadas. | Minutos por recargo/jornada, calendario/clasificación laboral, novedades adicionales y nómina DIAN; revisión profesional y personal legítimo. |
| ACC-014 | Parcial2/3 | Impuestos internos versionados, fuentes, devoluciones y trazas. | Fuentes sin política, cobertura declarativa/multicuenta y contraste DIAN; normativa/tratamiento turístico revisados profesionalmente. |
| ACC-015 | Parcial2/3 | Importación neutral, estados y conciliación;120 cuentas empresariales de prueba. | Conectores/catálogo bancario, consentimientos, cuentas personales, FX/carga. No acredita conexión a todos los bancos ni cuentas personales del usuario. |
| ACC-016 | Parcial2/3 | Liquidez exacta/cortes y vistas antiguas corregidas. | Ratios por paquete/costos y fuentes operativas legítimas/calibración. RAT, ocupación y ADR diferidos por instrucción del usuario. |
| ACC-017 | Parcial2/3 | Simulación30/90/365 y ventanas cronológicas en ambos paneles. | Estacionalidad/modelos/recomendaciones revisadas; serie auténtica diaria de379 días y validación fuera de muestra. Usuario no dispone de ella. |
| ACC-018 | Parcial2/3 | Factores, unidades, fuentes y correcciones append-only. | Factores y evidencias auténticos, aplicabilidad/obligación revisadas; no reconocer pasivos/créditos ficticios. |
| ACC-019 | Parcial2/3 | Reportes ESG con corrección efectiva y trazas; estado corregido aPARCIAL. | Aplicabilidad GRI/SASB, soportes/factores legítimos y revisión profesional; no hay certificación ambiental. |
| ACC-020 | Parcial2/3 | Herramientas deterministas acotadas de lectura y fuentes. | Modelo privado/local evaluado, calidad/privacidad, dataset consentido y capacidades adicionales; no se ejecutó un LLM financiero. |
| ACC-021 | Parcial2/3 | Ensayo durable, dos confirmaciones y revisión de impacto, cancelación y recuperación. | Executor real agent-desktop/Open Duet, bancos/cuentas/recibos/autorizaciones legítimos. Ensayo no paga ni crea autorización financiera. |
| ACC-022 | Parcial2/3 | Captura ambiental web en frío, cifrado y conflictos; rutas Nginx exactas. | Más dominios, colas/sincronización, almacenamiento SQLite nativo y pruebas físicas Android/iOS/escritorio. No es ERP completo offline. |
| ACC-023 | Parcial2/3 | Métricas exactas, muestras fallidas y contratos HTTP/optimización opcional. | Persisten picos sobre250ms en mediciones anteriores; infraestructura/carga objetivo y modelo/dataset real. No se revalida SLA midiendo durante esta regresión concurrente. |
| ACC-024 | Parcial2/3 | Backups autenticados, permisos limitados, restauración PostgreSQL y dos instalaciones nuevas. | Roles/rutas/RLS y funciones privilegiadas completos; llaves/documentos/medios reales, RPO/RTO acordados, despliegue/reversión y aceptación independiente. |

**Estado posterior del hallazgo legado:** subsanado localmente en la auditoríaH001–H072 inferior: importación, serialización y lecturas autorizadas reparadas, sin montar rutas ni habilitar escrituras. El diagnóstico original se conserva en el registro técnico. ACC-024 conserva los pendientes de aceptación integral.

**Entrega:** cambios locales en la rama de trabajo, respaldo privado verificado del acumulado;sin commit,push,despliegue ni publicación. Se preservan los archivos originales y las evidencias históricas. Los pendientes reales de aplicaciones, profesionales, proveedores, datos, hardware y operación permanecen abiertos.


## Auditoría explícita H001–H072 · 2026-11-11

**Base y resultado:** se conservaron24 tareas, tres hitos por tarea y72 créditos posibles. La numeración corresponde a incremento, verificación y aceptación completa, en ese orden, paraACC-001 hastaACC-024. Resultado:57 acreditados y15 pendientes;79,17%;9/24 tareas con aceptación original completa. Incremento acreditado puede tener alcance parcial: no significa módulo íntegro ni habilitación productiva. Ningún documento o repetición de prueba añadió crédito.

**Fallas corregidas:** el indicador dependía del contexto decimal del llamador y fallaba con trampas/precisión restrictivas; ahora calcula con contexto propio. Se añadieron numeración estableH001–H072, criterio/referencias/pendiente por hito y rechazo temprano de IDs de tarea fuera de la base. Invertir registro/matriz no altera números ni resultados. El adaptador legado de viewsets, antes inimportable por módulos/serializadores e imports inexistentes, ahora tiene serialización UUID de solo lectura, permisos por vínculo vigente y consultas explícitamente acotadas a empresa. Los asientos expuestos por ese adaptador son contabilizados; el borrador/UUID ajeno no se entrega. No se registraron rutas nuevas: las escrituras genéricas no se exponen y la contrapartida alternativa devuelve409 para remitir al flujo revisado, sin escribir el libro.

**Pruebas y evidencia:**1.807 pruebas en148 suites/pasos de regresión contable, sin skips; manifiesto de fuentes estable y hashes verificados. Incluye21 pruebas del progreso y19 de presentación.18 pruebas adicionales del runner,4 del paquete offline y55 comprobaciones Chromium de cifrado/recuperación y borradores cifrados aprobadas. Los fallos previos(21 pruebas del progreso:1 fallo/3 errores;19 de presentación:6 errores) quedan registrados como diagnóstico, nunca como aprobación. Se conservaron las pruebas PostgreSQL, instalaciones y recorridos de la auditoría anterior sin sumarlos como reejecuciones actuales. No cambiaron migraciones, guardasSQL, transporte de proveedores ni interfaces montadas. Registro técnico existente:clave`audit_milestones_001_072`, con criterios y evaluación individual de los72 hitos.

| Hito | Tarea | Etapa | Estado registrado | Referencias |
|---|---|---|---|---:|
| H001 | ACC-001 | Incremento | Acreditado | 3 |
| H002 | ACC-001 | Pruebas | Acreditado | 6 |
| H003 | ACC-001 | Aceptación | Acreditado | 1 |
| H004 | ACC-002 | Incremento | Acreditado | 3 |
| H005 | ACC-002 | Pruebas | Acreditado | 4 |
| H006 | ACC-002 | Aceptación | Acreditado | 1 |
| H007 | ACC-003 | Incremento | Acreditado | 2 |
| H008 | ACC-003 | Pruebas | Acreditado | 4 |
| H009 | ACC-003 | Aceptación | Acreditado | 1 |
| H010 | ACC-004 | Incremento | Acreditado | 10 |
| H011 | ACC-004 | Pruebas | Acreditado | 9 |
| H012 | ACC-004 | Aceptación | Acreditado | 1 |
| H013 | ACC-005 | Incremento | Acreditado | 6 |
| H014 | ACC-005 | Pruebas | Acreditado | 7 |
| H015 | ACC-005 | Aceptación | Acreditado | 1 |
| H016 | ACC-006 | Incremento | Acreditado | 17 |
| H017 | ACC-006 | Pruebas | Acreditado | 16 |
| H018 | ACC-006 | Aceptación | Acreditado | 1 |
| H019 | ACC-007 | Incremento | Acreditado | 11 |
| H020 | ACC-007 | Pruebas | Acreditado | 6 |
| H021 | ACC-007 | Aceptación | Acreditado | 1 |
| H022 | ACC-008 | Incremento | Acreditado | 22 |
| H023 | ACC-008 | Pruebas | Acreditado | 26 |
| H024 | ACC-008 | Aceptación | Acreditado | 1 |
| H025 | ACC-009 | Incremento | Acreditado | 12 |
| H026 | ACC-009 | Pruebas | Acreditado | 16 |
| H027 | ACC-009 | Aceptación | Pendiente | 0 |
| H028 | ACC-010 | Incremento | Acreditado | 8 |
| H029 | ACC-010 | Pruebas | Acreditado | 11 |
| H030 | ACC-010 | Aceptación | Acreditado | 1 |
| H031 | ACC-011 | Incremento | Acreditado | 6 |
| H032 | ACC-011 | Pruebas | Acreditado | 11 |
| H033 | ACC-011 | Aceptación | Pendiente | 0 |
| H034 | ACC-012 | Incremento | Acreditado | 14 |
| H035 | ACC-012 | Pruebas | Acreditado | 9 |
| H036 | ACC-012 | Aceptación | Pendiente | 0 |
| H037 | ACC-013 | Incremento | Acreditado | 16 |
| H038 | ACC-013 | Pruebas | Acreditado | 19 |
| H039 | ACC-013 | Aceptación | Pendiente | 0 |
| H040 | ACC-014 | Incremento | Acreditado | 23 |
| H041 | ACC-014 | Pruebas | Acreditado | 27 |
| H042 | ACC-014 | Aceptación | Pendiente | 0 |
| H043 | ACC-015 | Incremento | Acreditado | 14 |
| H044 | ACC-015 | Pruebas | Acreditado | 20 |
| H045 | ACC-015 | Aceptación | Pendiente | 0 |
| H046 | ACC-016 | Incremento | Acreditado | 4 |
| H047 | ACC-016 | Pruebas | Acreditado | 8 |
| H048 | ACC-016 | Aceptación | Pendiente | 0 |
| H049 | ACC-017 | Incremento | Acreditado | 4 |
| H050 | ACC-017 | Pruebas | Acreditado | 5 |
| H051 | ACC-017 | Aceptación | Pendiente | 0 |
| H052 | ACC-018 | Incremento | Acreditado | 5 |
| H053 | ACC-018 | Pruebas | Acreditado | 13 |
| H054 | ACC-018 | Aceptación | Pendiente | 0 |
| H055 | ACC-019 | Incremento | Acreditado | 4 |
| H056 | ACC-019 | Pruebas | Acreditado | 8 |
| H057 | ACC-019 | Aceptación | Pendiente | 0 |
| H058 | ACC-020 | Incremento | Acreditado | 3 |
| H059 | ACC-020 | Pruebas | Acreditado | 11 |
| H060 | ACC-020 | Aceptación | Pendiente | 0 |
| H061 | ACC-021 | Incremento | Acreditado | 6 |
| H062 | ACC-021 | Pruebas | Acreditado | 10 |
| H063 | ACC-021 | Aceptación | Pendiente | 0 |
| H064 | ACC-022 | Incremento | Acreditado | 5 |
| H065 | ACC-022 | Pruebas | Acreditado | 8 |
| H066 | ACC-022 | Aceptación | Pendiente | 0 |
| H067 | ACC-023 | Incremento | Acreditado | 5 |
| H068 | ACC-023 | Pruebas | Acreditado | 5 |
| H069 | ACC-023 | Aceptación | Pendiente | 0 |
| H070 | ACC-024 | Incremento | Acreditado | 6 |
| H071 | ACC-024 | Pruebas | Acreditado | 6 |
| H072 | ACC-024 | Aceptación | Pendiente | 0 |

### Pendientes discriminados de los15 hitos de aceptación

| Hito pendiente | Desarrollo/verificación técnica restante | Requisito externo |
|---|---|---|
| H027 | Completar y cualificar documento/firma/transporte y ciclo fiscal. | DIAN directa aplazada; certificado, resolución, test set y acuses legítimos. |
| H033 | Cualificar integración, revocación, caída y recuperación con el destino real elegido. | Drive/OneDrive: no existe aplicación OAuth registrada ni grants/cuenta autorizados disponibles. |
| H036 | Procesos especializados, interfaces/conexión operacional, concurrencia y migración histórica. | Datos y autorización profesional legítimos de aptitud/EPP/descanso/riesgo y pruebas físicas. |
| H039 | Minutos individuales por recargo/jornada, calendario legal, novedades adicionales y nómina DIAN. | Personal/soportes legítimos, reglas laborales revisadas y habilitación de nómina electrónica. |
| H042 | Cobertura fiscal completa, fuentes sin política capturada, períodos declarativos y multicuenta. | Tratamiento tributario revisado y contraste oficial DIAN; no equivale a declaración aceptada. |
| H045 | Catálogo/conectores bancarios, gestión personal de más de50 cuentas por usuario, FX y carga. | Consentimientos, fuentes/API bancarias auténticas o agregador autorizado;120 cuentas empresariales de laboratorio no prueban cuentas personales conectadas. |
| H048 | Ratios por producto/paquete, dimensiones de costo y calibración con fuentes operativas. | Series y supuestos legítimos/revisión profesional. RAT/ocupación/ADR diferidos expresamente, sin desarrollarlos aquí. |
| H051 | Modelos/estacionalidad y recomendaciones más amplias, calibración y validación fuera de muestra. | Serie diaria histórica autorizada de al menos379 días: usuario confirmó que no dispone de ella. |
| H054 | Completar cualificación ambiental, deduplicación y tratamiento de obligaciones cuando corresponda. | Factores, soportes y política/obligación revisados; usuario no dispone de esa documentación. No reconocer pasivos ni créditos inventados. |
| H057 | Completar cualificación de marcos y cobertura de reportes ESG. | Aplicabilidad GRI/SASB y soportes/factores verificados por profesionales; no certificación sintética. |
| H060 | Conectar y evaluar un modelo local/privado y capacidades pendientes mediante herramientas acotadas. | Dataset consentido, equipo suficiente y evaluación independiente de calidad/privacidad. No afirmar99,8% sin medición. |
| H063 | Executor financiero real agent-desktop/Open Duet con permisos mínimos y recibos verificables. | Cuentas/beneficiarios/proveedor legítimos y autorizaciones explícitas de cada operación real. El ensayo no ejecuta pagos. |
| H066 | Más dominios, colas/sincronización y conflictos, almacenamiento nativo SQLite cifrado. | Android/iOS/escritorio físicos, herramientas de compilación y validación de actualización/recuperación. Web offline ambiental no es ERP completo sin red. |
| H069 | Optimización/carga representativa y medición evento-a-ledger; evaluación real del clasificador. | Infraestructura/hardware y dataset autorizados. Mediciones anteriores aún tienen picos sobre250ms; no se acredita SLA ni99,8%. |
| H072 | Rutas/permisos/RLS/funciones privilegiadas completos, restauración integral, despliegue y reversión. | Llaves/documentos/medios reales, RPO/RTO acordados, infraestructura objetivo y aceptación independiente. El adaptador legado ya fue reparado localmente. |

**Seguimiento y entrega:** `PROGRESO.md` y `progreso.json` ahora muestran el índice completo; se regeneran desde el mismo registro. El hallazgo del adaptador legado señalado en el corte anterior queda subsanado localmente;ACC-024 yH072 siguen abiertos por su alcance restante. Producción no habilitada. Sin commit,push ni despliegue; acumulado preservado en respaldo privado verificado.


## Ejércitos propios de Analemática y ERP turístico · 2026-11-11

**Directriz aplicada:** SGA-CD se tomó como referencia estructural. La réplica vive en los backends propios de Analemática y del ERP de empresas turísticas; no importa agentes/servicios de SGA-CD ni requiere que ese backend esté levantado. Las funciones del ledger y la identidad empresarial ya existentes se reutilizan como biblioteca en cada proceso. Turismo Nacional es institucional, no ERP: no se añadió un ejército contable a ese sistema, y se verificó404 para las nuevas rutas empresariales y los prefijos heredados.

**Los tres generales:** Jarvi es el General operativo; Neko es el General conversacional; SOUP es el General optimizador de procesos de los agentes. La voz fluida es una función separada, todavía sin nombre/proveedor confirmado ni audio en vivo integrado. Neko admite texto/transcripción acotados: prepara un borrador y no convierte la voz en aprobación financiera. El usuario confirma una misión y Jarvi delega realmente por Coroneles, Capitanes, Tenientes, Sargentos y Soldados. Hay29 agentes lógicos por backend(58 entre ambos), incluidos los tres generales; no son58 procesos LLM arrancados. Cada backend tiene estado mayor, jerarquía, política, API, adaptadores y namespace de auditoría propios.

**Código canónico:**

- `BACKEND/ANALEMATICA-BACKEND/gestion_contable/contabilidad/agent_army/`.
- `BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/agent_army/`.
- Primitivas comunes del motor: `core_erp/accounting/agent_army_runtime.py`, `agent_army_staff.py`, `agent_army_engines.py` y `agent_army_api.py`; ningún backend llama al servicio SGA-CD para ejecutar esas misiones.

**Incremento operativo:** cinco tareas concretas con datos del ledger: balance de comprobación, rentabilidad, liquidez, diagnóstico de integridad acotado a20 asientos y estado actual de la cola comercial. La cola no certifica DIAN y la muestra no certifica toda la cadena. Los soldados consultan/verifican las fuentes; la traza refleja los rangos y herramientas que efectivamente se ejecutaron. Si falla el lector, no se afirma haber ejecutado el verificador. Los resultados incompletos exigen revisión, sin inventar cifras ni permisos. Las misiones se registran con scope/digest y request_id idempotente; su consulta/repetición vuelve a validar actor, empresa y vínculo, sin volver a ejecutar herramientas ni sustituir una instantánea anterior por cifras actuales.

**Neko y SOUP:** Neko interpreta preguntas admitidas y devuelve un borrador con confirmed:false, sin ejecutar la misión ni aceptar roles/empresa del texto. SOUP evalúa muestras reales de tiempo por herramienta y estados bloqueados/pendientes, y produce recomendaciones. No ejecuta entrenamiento ni promociona modelos/procesos automáticamente; backend_72_tests_passed queda sin acreditar en su contrato, sin fabricar una aprobación de los72 hitos.

**Motores:** Open Duet y agent-desktop tienen configuración propia por backend y asignación explícita a administrador/empresa; los ejemplos están deshabilitados. Open Duet acepta solo planificación con memoria desactivada y recibe nombres/estados de tareas, sin saldos/documentos/identidades. agent-desktop solo dispone de una sonda status con ejecutable fijado por SHA-256 y límites de salida/tiempo; no controla pagos ni interfaces financieras. Las llamadas a motores se hacen fuera de la transacción contable; se reserva su ejecución antes de llamar y se conserva resultado incierto sin reintento automático. Configuración real, equipos y proveedores siguen sin cualificar.

**API nativa**, con autenticación nativa y un único provider_id autorizado en la consulta:

- GET `/api/v1/accounting-army/`: catálogo/estructura y configuración declarada de motores.
- POST `/api/v1/accounting-army/intake/`: Neko prepara una solicitud.
- POST `/api/v1/accounting-army/missions/`: Jarvi ejecuta una misión confirmada.
- GET `/api/v1/accounting-army/missions/<request_id>/`: informe persistido autorizado.
- GET `/api/v1/accounting-army/missions/<request_id>/optimization/`: evaluación de SOUP.
- POST `/api/v1/accounting-army/missions/<request_id>/engines/<engine>/`: plan/sonda explícitamente compartidos, sin acción financiera.

El ERP publica su API en su proceso habitual. Analemática dispone de entrada nativa independiente `deployment.army_wsgi:application`, settings/URLs propios y target Docker `analematica-army`; necesita su configuración revisada de identidad/BD nativas. Su gateway anterior se conserva. El target está preparado y el arranque nativo de Django fue probado; no se construyó/publicó una imagen productiva ni se cambió el despliegue del usuario.

**Validación final:**1.859 pruebas en151 suites/pasos aprobadas sin skips y con manifiesto de fuentes estable. Dentro de ese total hay52 pruebas específicas(30 de dominio/API,17 de estado mayor/motores y5 HTTP);19 pruebas del verificador de fuentes son adicionales. Los tres procesos HTTP de laboratorio usan ORM/JWT reales y datos sintéticos: ambos ejércitos funcionan sin SGA-CD y Turismo rechaza sus rutas. Open Duet se verificó con MockTransport; agent-desktop con un ejecutable temporal fijado por hash, sin acreditación de hardware. También se comprobó el arranque nativo de Analemática con un origen SGA-CD inalcanzable, sin módulos SGA-CD cargados. No se suman los intentos previos ni las repeticiones para inflar cobertura o porcentaje. Evidencia, hashes, manifiesto y límites en el registro técnico existente, clave`native_erp_analematica_agent_armies`.

**Pendientes concretos:** configuración/roles/BD nativos y despliegue de Analemática; construcción/cualificación de imagen en infraestructura objetivo; motores reales por backend y permisos/directorios por instancia; concurrencia PostgreSQL/volúmenes, retención de auditoría y control de escritores privilegiados; audio/voz fluida; entrenamiento/evaluación/promoción supervisada de candidatos; herramientas adicionales de los servicios ERP e integración de paneles. Las operaciones financieras mantienen sus flujos existentes de consentimiento, dos autorizaciones y revisión de impacto cuando corresponda; el nuevo ejército consulta y diagnostica, sin contabilizar, pagar, retirar, firmar ni publicar por sí solo.

**Estado y entrega:** la base original permanece57/72=79,17%, con9/24 tareas aceptadas. Estas mejoras no cierran por sí solas los requisitos restantes deACC-020/021/024 ni agregan hitos. Trabajo local respaldado; sin commit,push,activación de motores ni despliegue productivo.

## Entrega consolidada y liderazgo de Analemática · 2026-11-11

Directriz nueva: Analemática será el sistema líder; se autoriza un único commit
consolidado del avance y el cambio de nombre del repositorio a Analematica.
Se trasladaron íntegramente OpenJarvis, N.E.K.O y Soup desde
BACKEND/SGA-CD-BACKEND/app/agents a BACKEND/ANALEMATICA-BACKEND/agents: 13.888
archivos verificados byte a byte, incluidos enlaces simbólicos si existen.
Manifestación técnica: evidencias/traslado-generales-20261111.json.
También se centralizaron el estado mayor heredado y sus tres contratos; SGA-CD
conserva exportaciones de compatibilidad para no romper sus endpoints. El ERP
conserva adaptadores, aislamiento empresarial y estado propio sobre el núcleo
canónico de Analemática. No se activa entrenamiento, voz ni acceso financiero.
El indicador contable se mantiene en 79,17 % (57/72); mover fuentes y publicar
código no acredita requisitos externos ni habilita producción.

Verificación del consolidado: 1.859 pruebas en 151 suites/pasos sin fallos.
El control global de estabilidad detectó el ajuste de BACKEND/deployment/Dockerfile
durante esa ejecución; se comprobó que fue la única fuente del manifiesto que
cambió. Se repitieron después las suites de dominio, estado mayor, HTTP y runner
con fuentes finales estables (52 pruebas de agentes y 19 del runner). Se validaron
los tres contratos centralizados, la ausencia de las tres carpetas anteriores,
191 fuentes Python y las rutas/contexto de empaquetado Docker. No se construyeron
imágenes ni se acreditó activación de los proyectos externos por moverlos.

GitHub: main remoto comprobado en c745d0a antes de preparar la entrega, sin
divergencia. La API rechazó el cambio de nombre solicitado con Forbidden;
el token de gh tampoco autentica. El acceso Git admite la comprobación de push.
No afirmar que el nombre remoto cambió ni modificar origin a una URL inexistente.
La publicación se confirmará comparando el SHA remoto después del push normal.
