# Seguimiento único · Motor contable y20 hitos finales

Actualización:2026-11-11. Este archivo concentra desde ahora las novedades, hallazgos, bloqueos y siguientes acciones. No crear un informe Markdown por entrega o análisis. Los documentos anteriores se conservan como historia/evidencia; las matrices JSON y sus verificadores mantienen sus contratos.

## Estado real

**70,83% (51/72 hitos de la matriz original). Aceptación completa3/24 tareas. Producción no habilitada.** El plan restante tiene 2 hitos verificados localmente, 10 en ejecución y 8 pendientes; ninguno acredita cierre integral de todo el alcance. La existencia de código o una prueba sintética no sustituye aceptación profesional, de proveedor o física.

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
| R19 · Medir rendimiento y endurecer seguridad | En ejecución | Medición rehecha sobre las fuentes72:100 documentos sintéticos secuenciales, cuatro flujos, sin errores; máximo de consulta166.293ms. No acredita HTTP, concurrencia, carga productiva ni99.8% IA; clasificador no evaluado. | Hardware/carga objetivo, dataset autorizado y revisión de seguridad independiente para cualificación productiva. |
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
| 4 | ACC-004 | Periodos, concurrencia y contrapartidas | EN ESPERA · conservar implementación previa |
| 5 | ACC-005 | Puente TourismProvider a Tenant y actor verificables | EN ESPERA · conservar implementación previa |
| 6 | ACC-006 | Monedas, FX y valoración | EN ESPERA · conservar implementación previa |
| 7 | ACC-007 | Hash canónico versionado y controles SQL | EN ESPERA · conservar implementación previa |
| 8 | ACC-008 | Contrato CRM y reserva hacia facturación | EN ESPERA · conservar implementación previa |
| 9 | ACC-009 | XML, representación y firma fiscal | EN ESPERA · conservar implementación previa |
| 10 | ACC-010 | Envelope encryption cliente y recuperación | EN ESPERA · conservar implementación previa |
| 11 | ACC-011 | Conectores BYOS y OAuth mínimos | EN ESPERA · conservar implementación previa |
| 12 | ACC-012 | Órdenes, novedades y controles SG-SST | EN ESPERA · conservar implementación previa |
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
