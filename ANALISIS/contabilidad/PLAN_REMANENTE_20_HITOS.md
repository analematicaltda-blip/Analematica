# Nuevo plan de subsanación · 20 hitos restantes

**Base conservada:61,11 % (44/72).** Este plan organiza el trabajo faltante; no reinicia la matriz ni acredita puntos por documentar. Los cuatro paquetes anteriores verificados se conservan en su registro histórico. No se declara100% ni habilitación productiva.

La solicitud autoriza la ejecución automática del desarrollo y pruebas locales reversibles. Cada hito tiene hallazgo, implementación, prueba de cierre y evidencia externa. Los bloqueos externos permiten continuar con trabajo independiente. Las acciones reales, gasto, publicación y controles financieros conservan las autorizaciones exigidas.

**Orden de ejecución:** R01 → R02 → R09 → R03 → R10 → R11 → R12 → R04 → R07 → R08 → R13 → R14 → R15 → R16 → R17 → R18 → R19 → R05 → R06 → R20.

| Hito | Prioridad | Hallazgo que se subsana | Entregable |
|---|---|---|---|
| R01 · Recuperar y verificar el corte interrumpido | P0 | La interrupción dejó código tributario sin pruebas y no permitió confirmar la creación del archivo de tests. | Código + pruebas + evidencia; cierre: Fuentes actuales coinciden con el manifiesto; pruebas contables sin omisiones; no se elimina trabajo ni se altera Git. |
| R02 · Conectar política tributaria, reserva y ledger | P0 | La política versionada cotizaba impuestos mientras el desglose de la reserva seguía siendo manual; la integración escrita quedó sin verificar. | Código + pruebas + evidencia; cierre: Ambos backends generan el mismo asiento balanceado; evidencia ausente/alterada, versión inválida y fuente cambiada bloquean; reintento no duplica. |
| R03 · Completar retenciones, compras e IVA descontable | P1 | Las retenciones se cotizan, pero no tienen un flujo completo de contabilización; falta cobertura del IVA descontable. | Código + pruebas + evidencia; cierre: Casos gravados/exentos/excluidos y devoluciones concilian auxiliares, saldo fiscal y ledger sin redondeos ocultos ni duplicados. |
| R04 · Completar documento fiscal y representación | P1 | El UBL actual es borrador estructural; faltan campos y reglas del perfil fiscal y representación requerida. | Código + pruebas + evidencia; cierre: XML/representación coinciden con identidad, numeración, líneas y totales revisados; casos incompletos o inválidos no avanzan. |
| R05 · Cualificar firma y custodia del cliente | P1 | La firma disponible solo admite certificados y política de laboratorio; no acredita custodia ni confianza fiscales. | Código + pruebas + evidencia; cierre: Documento, certificado o política alterados se rechazan; evidencia de custodia/recuperación; ninguna llave maestra retenida por el proveedor. |
| R06 · Completar transporte DIAN y acuses auténticos | P1 | El verificador y diario actuales son de laboratorio; no hay SOAP/WS-Security cualificado ni estados oficiales autenticados. | Código + pruebas + evidencia; cierre: Aceptado, rechazado, pendiente y resultado incierto son distintos; acuse ajeno/alterado se rechaza; un timeout no consume otro consecutivo. |
| R07 · Completar almacenamiento soberano operativo | P1 | BYOS PostgreSQL funciona en pruebas; faltan provisionamiento y operación real de ambos paneles y conectores requeridos. | Código + pruebas + evidencia; cierre: Cifrar/subir/recuperar/descifrar y revocar en ambos paneles; caída o respuesta perdida no duplica ni deja documentos claros en el ERP. |
| R08 · Completar recuperación y rotación de custodia | P1 | El paquete portátil permite recuperación/rewrap, pero faltan coordinación de versiones y validación física de custodia. | Código + pruebas + evidencia; cierre: Restauración recupera documento y referencias; rotación y revocación tienen alcance explícito; no se restauran autorizaciones vencidas. |
| R09 · Implementar despacho SG-SST positivo y transversal | P0 | El genérico bloquea activación porque aún no existe autorización cualificada de aptitud, EPP y jornada; faltan módulos especializados. | Código + pruebas + evidencia; cierre: Caso apto y autorizado puede iniciar; aptitud vencida, EPP faltante, fatiga, relación ajena o revocación impiden inicio y reanudación con auditoría. |
| R10 · Completar nómina y costos por operación | P1 | La nómina actual cubre una base acotada; faltan novedades, recargos/viáticos y dimensiones turísticas completas. | Código + pruebas + evidencia; cierre: Mismo turno no duplica costo ni provisión; recargos, deducciones y contrapartidas concilian con ledger y fuente operacional. |
| R11 · Completar legados, lotes y valoración FX | P1 | La apertura acotada no cubre legados no coincidentes, lotes grandes ni valoración/revaluación cambiaria completa. | Código + pruebas + evidencia; cierre: Descuadre o tasa ausente bloquean; propuesta/asiento coinciden; reintento no duplica y reversión preserva moneda/base/tasa originales. |
| R12 · Completar conciliación bancaria y casos parciales | P1 | Existen correspondencias revisadas, pero faltan saldos completos, casos parciales/ambiguos, instrumentos/FX y autenticidad bancaria. | Código + pruebas + evidencia; cierre: Archivo repetido no duplica; coincidencias de otra empresa/divisa/importe no concilian; explicación de diferencias y trazabilidad completas. |
| R13 · Completar ratios turísticos y calibración | P2 | RevPAR/GOPPAR acotados no completan ocupación/ADR/cupos/paquetes ni denominadores y calibración independientes. | Código + pruebas + evidencia; cierre: Margen/ADR/ocupación y ratios aplicables concilian con ledger y capacidad; cero o fuente faltante son no calculables; sin datos futuros. |
| R14 · Completar corrección ambiental y reportes ESG | P2 | Hay estimaciones y correcciones; faltan formularios, búsqueda/cortes/exportación, incertidumbre y mapeos ESG aplicables. | Código + pruebas + evidencia; cierre: Correcciones sustituyen sin duplicar; reporte reproducible conserva origen/corte y no emite certificaciones o créditos ficticios. |
| R15 · Completar asistencia contable privada evaluada | P2 | El asistente determinista funciona, pero falta evaluar modelo privado/abierto, cobertura y calidad con datos autorizados. | Código + pruebas + evidencia; cierre: Consultas enlazan reportes; inyección y empresa ajena se rechazan; calidad/errores/privacidad medidos en dataset autorizado. |
| R16 · Completar orquestación supervisada del motor | P1 | El ensayo financiero no es un trabajador de ejecución ni está unido al broker limitado con proveedor/recibos reales. | Código + pruebas + evidencia; cierre: Cambiar importe/destino invalida autorizaciones; permisos vencidos no se reutilizan; resultado incierto se recupera sin duplicar; pruebas reales solo autorizadas. |
| R17 · Completar operación offline y sincronización nativa | P1 | El borrador IndexedDB cifrado no equivale a arranque offline completo ni SQLite/custodia nativa multiplataforma. | Código + pruebas + evidencia; cierre: Desconexión/reinicio/reconexión no pierden ni duplican novedades; conflictos no se ocultan y las aprobaciones deben renovarse online. |
| R18 · Completar recorridos e interfaces de ambos sistemas | P1 | Varias rutas nuevas tienen pruebas API pero no formularios o recorridos completos en los dos paneles. | Código + pruebas + evidencia; cierre: Recorridos completos en ambos sistemas con evidencia visual, teclado/contraste/móvil y datos correctamente aislados; funciones pendientes no aparentan éxito. |
| R19 · Medir rendimiento y endurecer seguridad | P1 | No están acreditados250ms ni precisión99,8%; faltan carga representativa, revisión de privilegios y pruebas independientes. | Código + pruebas + evidencia; cierre: Informe reproducible ligado a fuentes/hardware/dataset; sin garantías universales; ningún fallo crítico abierto se acepta como producción. |
| R20 · Restauración integral y aceptación final | P0 | La recuperación/despliegue reproducibles y aceptaciones externas de todo el alcance siguen incompletos. | Código + pruebas + evidencia; cierre: Todos los criterios anteriores tienen evidencia vigente; restauración y reversión demostradas; pendientes externos resueltos antes de declarar100%. |

## R01 · Recuperar y verificar el corte interrumpido

**Hallazgo:** La interrupción dejó código tributario sin pruebas y no permitió confirmar la creación del archivo de tests.

**Implementación:** Inventariar cambios conservados, restaurar pruebas ausentes, comprobar evidencias anteriores y ejecutar regresión con manifiesto estable.

**Cierre verificable local:** Fuentes actuales coinciden con el manifiesto; pruebas contables sin omisiones; no se elimina trabajo ni se altera Git.

**Dependencias:** Ninguna. Matriz anterior: H20.

**Evidencia externa para aceptación completa:** Ninguna para este cierre local acotado.

## R02 · Conectar política tributaria, reserva y ledger

**Hallazgo:** La política versionada cotizaba impuestos mientras el desglose de la reserva seguía siendo manual; la integración escrita quedó sin verificar.

**Implementación:** Calcular componentes desde versiones persistidas, ligar evidencia a la revisión y revalidarla antes de solicitud y asiento; conservar flujos manuales identificados.

**Cierre verificable local:** Ambos backends generan el mismo asiento balanceado; evidencia ausente/alterada, versión inválida y fuente cambiada bloquean; reintento no duplica.

**Dependencias:** R01. Matriz anterior: H06, H07.

**Evidencia externa para aceptación completa:** Tratamiento tributario y soportes legítimos revisados profesionalmente; la coincidencia interna no equivale a legalidad fiscal.

## R03 · Completar retenciones, compras e IVA descontable

**Hallazgo:** Las retenciones se cotizan, pero no tienen un flujo completo de contabilización; falta cobertura del IVA descontable.

**Implementación:** Implementar hechos de venta/compra, bases y cuentas por componente, vigencias, ajustes y contrapartidas; rechazar reglas o cuentas incompletas.

**Cierre verificable local:** Casos gravados/exentos/excluidos y devoluciones concilian auxiliares, saldo fiscal y ledger sin redondeos ocultos ni duplicados.

**Dependencias:** R02. Matriz anterior: H06.

**Evidencia externa para aceptación completa:** Reglas tributarias vigentes, responsabilidades y revisión de un profesional autorizado.

## R04 · Completar documento fiscal y representación

**Hallazgo:** El UBL actual es borrador estructural; faltan campos y reglas del perfil fiscal y representación requerida.

**Implementación:** Conectar fuente comercial/políticas, validar campos y esquemas vigentes, notas/cargos/anticipos y representación fiscal; mantener borrador diferenciado.

**Cierre verificable local:** XML/representación coinciden con identidad, numeración, líneas y totales revisados; casos incompletos o inválidos no avanzan.

**Dependencias:** R02, R03. Matriz anterior: H07.

**Evidencia externa para aceptación completa:** Anexo DIAN vigente, resolución e identidad legítimas, formatos/ejemplos autorizados y revisión fiscal.

## R05 · Cualificar firma y custodia del cliente

**Hallazgo:** La firma disponible solo admite certificados y política de laboratorio; no acredita custodia ni confianza fiscales.

**Implementación:** Adaptar firma al perfil aprobado, cadena/política/revocación/reloj y custodia cliente, con recuperación y revocación controladas.

**Cierre verificable local:** Documento, certificado o política alterados se rechazan; evidencia de custodia/recuperación; ninguna llave maestra retenida por el proveedor.

**Dependencias:** R04, R08. Matriz anterior: H08.

**Evidencia externa para aceptación completa:** Certificado legítimo, política de confianza, medios/HSM/equipos y revisión independiente que correspondan.

## R06 · Completar transporte DIAN y acuses auténticos

**Hallazgo:** El verificador y diario actuales son de laboratorio; no hay SOAP/WS-Security cualificado ni estados oficiales autenticados.

**Implementación:** Implementar cliente de habilitación con destinos fijos, límites, autenticación aprobada, seguimiento y reintentos de resultado incierto ligados a numeración.

**Cierre verificable local:** Aceptado, rechazado, pendiente y resultado incierto son distintos; acuse ajeno/alterado se rechaza; un timeout no consume otro consecutivo.

**Dependencias:** R04, R05. Matriz anterior: H09.

**Evidencia externa para aceptación completa:** Acceso DIAN/proveedor autorizado, credenciales mediante canal seguro, test set, resolución y acuses auténticos.

## R07 · Completar almacenamiento soberano operativo

**Hallazgo:** BYOS PostgreSQL funciona en pruebas; faltan provisionamiento y operación real de ambos paneles y conectores requeridos.

**Implementación:** Completar perfiles/grants de cliente, cargas/versiones, revocación, límites, caída y recuperación; implementar OAuth/conectores solo si son necesarios.

**Cierre verificable local:** Cifrar/subir/recuperar/descifrar y revocar en ambos paneles; caída o respuesta perdida no duplica ni deja documentos claros en el ERP.

**Dependencias:** R01. Matriz anterior: H10.

**Evidencia externa para aceptación completa:** Destino propiedad del cliente, consentimiento, TLS/roles/grants y retención/backup legítimos.

## R08 · Completar recuperación y rotación de custodia

**Hallazgo:** El paquete portátil permite recuperación/rewrap, pero faltan coordinación de versiones y validación física de custodia.

**Implementación:** Implementar referencias de última versión, conflicto de ramas, respaldo y recuperación bajo política explícita; integrar custodia nativa requerida.

**Cierre verificable local:** Restauración recupera documento y referencias; rotación y revocación tienen alcance explícito; no se restauran autorizaciones vencidas.

**Dependencias:** R07. Matriz anterior: H11.

**Evidencia externa para aceptación completa:** Política/medios reales del cliente y pruebas físicas de recuperación/hardware cuando aplique.

## R09 · Implementar despacho SG-SST positivo y transversal

**Hallazgo:** El genérico bloquea activación porque aún no existe autorización cualificada de aptitud, EPP y jornada; faltan módulos especializados.

**Implementación:** Crear y conectar el contrato verificable de aptitud, EPP, recursos y jornada/descanso; integrar todas las rutas, tareas, ejecutores y guardas SQL requeridas.

**Cierre verificable local:** Caso apto y autorizado puede iniciar; aptitud vencida, EPP faltante, fatiga, relación ajena o revocación impiden inicio y reanudación con auditoría.

**Dependencias:** R01. Matriz anterior: H12.

**Evidencia externa para aceptación completa:** Reglas SG-SST, roles profesionales y evidencia de aptitud legítima; nunca inferirla de texto libre ni exponer clínica.

## R10 · Completar nómina y costos por operación

**Hallazgo:** La nómina actual cubre una base acotada; faltan novedades, recargos/viáticos y dimensiones turísticas completas.

**Implementación:** Implementar reglas versionadas para novedades y provisiones, vincular turnos/servicios/centros de costo y documento electrónico sin dispersión implícita.

**Cierre verificable local:** Mismo turno no duplica costo ni provisión; recargos, deducciones y contrapartidas concilian con ledger y fuente operacional.

**Dependencias:** R02, R09. Matriz anterior: H13.

**Evidencia externa para aceptación completa:** Reglas laborales revisadas, datos legítimos de personal y habilitación de nómina electrónica para aceptación oficial.

## R11 · Completar legados, lotes y valoración FX

**Hallazgo:** La apertura acotada no cubre legados no coincidentes, lotes grandes ni valoración/revaluación cambiaria completa.

**Implementación:** Agregar migración revisada por lotes, diferencias identificadas y tasas con fuente/vigencia; ajustar mediante contrapartidas conservando libros anteriores.

**Cierre verificable local:** Descuadre o tasa ausente bloquean; propuesta/asiento coinciden; reintento no duplica y reversión preserva moneda/base/tasa originales.

**Dependencias:** R01. Matriz anterior: H05.

**Evidencia externa para aceptación completa:** Saldos/soportes originales, fuente FX autorizada y revisión contable profesional.

## R12 · Completar conciliación bancaria y casos parciales

**Hallazgo:** Existen correspondencias revisadas, pero faltan saldos completos, casos parciales/ambiguos, instrumentos/FX y autenticidad bancaria.

**Implementación:** Implementar conciliación de período, pagos parciales/cargos y diferencias explícitas, con identidad de fuente y conectores mínimos autorizados.

**Cierre verificable local:** Archivo repetido no duplica; coincidencias de otra empresa/divisa/importe no concilian; explicación de diferencias y trazabilidad completas.

**Dependencias:** R11. Matriz anterior: H14.

**Evidencia externa para aceptación completa:** Extractos legítimos; permisos/consentimiento bancarios si se integra API; revisión profesional.

## R13 · Completar ratios turísticos y calibración

**Hallazgo:** RevPAR/GOPPAR acotados no completan ocupación/ADR/cupos/paquetes ni denominadores y calibración independientes.

**Implementación:** Implementar observaciones operativas versionadas, costos por producto y ratios con corte económico/de conocimiento y fuente verificable.

**Cierre verificable local:** Margen/ADR/ocupación y ratios aplicables concilian con ledger y capacidad; cero o fuente faltante son no calculables; sin datos futuros.

**Dependencias:** R10, R11. Matriz anterior: H15.

**Evidencia externa para aceptación completa:** Series operativas reales y supuestos financieros revisados.

## R14 · Completar corrección ambiental y reportes ESG

**Hallazgo:** Hay estimaciones y correcciones; faltan formularios, búsqueda/cortes/exportación, incertidumbre y mapeos ESG aplicables.

**Implementación:** Completar consulta histórica, evidencia/duplicados semánticos, interfaz y reportes con fuente/unidad/marco explícitos; separar medición de obligación contable.

**Cierre verificable local:** Correcciones sustituyen sin duplicar; reporte reproducible conserva origen/corte y no emite certificaciones o créditos ficticios.

**Dependencias:** R01, R11. Matriz anterior: H16.

**Evidencia externa para aceptación completa:** Factores, soportes y marcos revisados; obligación/compensación legítima si se reconoce financieramente.

## R15 · Completar asistencia contable privada evaluada

**Hallazgo:** El asistente determinista funciona, pero falta evaluar modelo privado/abierto, cobertura y calidad con datos autorizados.

**Implementación:** Incorporar modelo local/privado mediante herramientas de lectura acotadas, evaluación reproducible y respuestas con fuentes; sin SQL libre ni permisos de escritura.

**Cierre verificable local:** Consultas enlazan reportes; inyección y empresa ajena se rechazan; calidad/errores/privacidad medidos en dataset autorizado.

**Dependencias:** R13. Matriz anterior: H17.

**Evidencia externa para aceptación completa:** Dataset consentido, capacidad del equipo y revisión de calidad/privacidad; no afirmar99,8% sin medición.

## R16 · Completar orquestación supervisada del motor

**Hallazgo:** El ensayo financiero no es un trabajador de ejecución ni está unido al broker limitado con proveedor/recibos reales.

**Implementación:** Conectar tareas al motor agent-desktop/Open Duet mediante permisos mínimos, dos autorizaciones separadas del mismo solicitante y revisión adicional de impacto.

**Cierre verificable local:** Cambiar importe/destino invalida autorizaciones; permisos vencidos no se reutilizan; resultado incierto se recupera sin duplicar; pruebas reales solo autorizadas.

**Dependencias:** R12, R15. Matriz anterior: H18.

**Evidencia externa para aceptación completa:** Beneficiario/cuenta/proveedor/recibos legítimos y autorización explícita de cada acción real; no pagar por predicción, ubicación o simulación.

## R17 · Completar operación offline y sincronización nativa

**Hallazgo:** El borrador IndexedDB cifrado no equivale a arranque offline completo ni SQLite/custodia nativa multiplataforma.

**Implementación:** Implementar captura y cola cifrada por dominio, arranque sin red, conflictos visibles, sincronización idempotente y almacenamiento nativo requerido.

**Cierre verificable local:** Desconexión/reinicio/reconexión no pierden ni duplican novedades; conflictos no se ocultan y las aprobaciones deben renovarse online.

**Dependencias:** R08, R09. Matriz anterior: H19.

**Evidencia externa para aceptación completa:** Dispositivos Android/iOS/escritorio y herramientas de compilación/hardware para pruebas físicas.

## R18 · Completar recorridos e interfaces de ambos sistemas

**Hallazgo:** Varias rutas nuevas tienen pruebas API pero no formularios o recorridos completos en los dos paneles.

**Implementación:** Conectar pantallas y estados reales, recuperación de errores, permisos, accesibilidad y vista móvil; conservar azul metalizado/azul claro/texto blanco.

**Cierre verificable local:** Recorridos completos en ambos sistemas con evidencia visual, teclado/contraste/móvil y datos correctamente aislados; funciones pendientes no aparentan éxito.

**Dependencias:** R02, R07, R10, R13, R14, R16, R17. Matriz anterior: H07, H10, H13, H16, H18, H19.

**Evidencia externa para aceptación completa:** Aceptación de usuarios/roles reales cuando corresponda; no sustituirla por fixtures.

## R19 · Medir rendimiento y endurecer seguridad

**Hallazgo:** No están acreditados250ms ni precisión99,8%; faltan carga representativa, revisión de privilegios y pruebas independientes.

**Implementación:** Ejecutar benchmark por flujo con percentiles/máximo/errores, revisar SQL/RLS/roles, dependencias, auditoría y fugas; corregir y volver a medir.

**Cierre verificable local:** Informe reproducible ligado a fuentes/hardware/dataset; sin garantías universales; ningún fallo crítico abierto se acepta como producción.

**Dependencias:** R18. Matriz anterior: H20.

**Evidencia externa para aceptación completa:** Hardware/carga objetivo, dataset autorizado y revisión de seguridad independiente para cualificación productiva.

## R20 · Restauración integral y aceptación final

**Hallazgo:** La recuperación/despliegue reproducibles y aceptaciones externas de todo el alcance siguen incompletos.

**Implementación:** Restaurar datos/archivos/referencias con roles reales, comprobar RPO/RTO, reversión y operación; consolidar entregables y preparar publicación revisable.

**Cierre verificable local:** Todos los criterios anteriores tienen evidencia vigente; restauración y reversión demostradas; pendientes externos resueltos antes de declarar100%.

**Dependencias:** R01, R02, R03, R04, R05, R06, R07, R08, R09, R10, R11, R12, R13, R14, R15, R16, R17, R18, R19. Matriz anterior: H20.

**Evidencia externa para aceptación completa:** Medios/llaves/grants reales, aceptación profesional y de proveedor; publicación/producción solo con la autorización correspondiente.

## Control de ejecución

El registro JSON conserva estados de código, aceptación y cierre por separado. VERIFICADO_LOCAL no equivale a aceptación productiva. Solo se marca fully_closed cuando se cumplen todos los criterios aplicables. No se sustituye el denominador global de72 hitos ni se duplica evidencia ya acreditada.

Revalidar pruebas afectadas cuando cambie código posterior; conservar logs/manifiestos y registrar lo no ejecutado. No reescribir una función operativa sin justificarlo. Ningún pago, envío DIAN o trabajo de control se autoriza por existir un plan, un borrador o una predicción.

Los pendientes de producción se mantienen en `ANALISIS/produccion/PENDIENTES-PRODUCCION-ECOSISTEMA.md`; el registro contable original permanece en `progress-registry.json`.

## Ejecución inicial comprobada · corte68

- **R01:** cierre local acotado verificado. Evidencias67 conservadas y sus hashes comprobados; ningún archivo eliminado dentro del manifiesto contable; cambios de fuente identificados y regresión actual con manifiesto estable. No afirma un respaldo integral ni aceptación productiva.
- **R02:** incremento verificado localmente en API/ORM y HTTP corporativo→ERP, con asiento real del ledger de prueba. Aceptación tributaria completa pendiente; no emisión DIAN ni pago.
- **576 pruebas Python aprobadas**, incluidas14 nuevas de política/reserva y2 del puente corporativo. No se duplican créditos globales.
- **R03–R20:** trabajo remanente por ejecutar según dependencias; no se marcan completos por existir este plan. Detalle: [implementación68](IMPLEMENTACION_68.md).

## Incremento69 · R09 en ejecución

Se implementaron registros persistentes por trabajador, controles de vigencia/empresa/permisos y despacho positivo de orden genérica con dos confirmaciones; fin hacia VALIDACION y jornada registrada.37 casos nuevos locales y migración SQLite fresca; alcance especializado, interfaces, cualificación PostgreSQL y aceptación profesional siguen pendientes. [Contrato](OPERACION_DATOS_SEGURIDAD_TRABAJADOR.md) y [reporte69](IMPLEMENTACION_69.md). R09 no está cerrado íntegramente.

## Incremento70 · R03 en ejecución

Se implementaron posteo tributario por componente y contrapartidas revisadas de hechos comerciales declarados;28 casos nuevos y2 pruebas corporativas HTTP. Faltan fuentes nativas, conciliación unificada y alcance profesional/productivo. No se declara cierre integral. [Reporte70](IMPLEMENTACION_70.md).

## Incremento71 · R03/R18 y medición independiente de R19

Registro integrado visible, validación por lotes y medición local reproducible; el máximo de conciliación pasó de547.209ms a134.922ms en100 documentos sintéticos secuenciales. Avance actual63,89% (46/72), conservando la base histórica61,11%; sin SLA ni precisión IA aceptadas. Los cierres globales y dependencias se conservan abiertos. [Reporte71](IMPLEMENTACION_71.md).

## Incremento72 · Compras nativas y recorridos R03/R18

Captura de proveedor/factura, posteo revisado, reserva de documento/huella, catálogo propio de gastos y formularios en ambos paneles; recarga y contrapartida verificadas. No cierra historia, fiscalidad completa ni todas las interfaces. [Reporte72](IMPLEMENTACION_72.md).

## Actualización73 · R10 en ejecución

El backend del ERP ya relaciona nómina contabilizada con jornadas y operaciones, conserva costo sin asignar y exige dos confirmaciones.23 pruebas nuevas aprobadas; sin otro asiento ni pago. [Entrega73](IMPLEMENTACION_73.md). Faltan conexión corporativa, interfaces y reglas/documento laboral completos: no se cierra R10. Estado actual del plan restante:2 verificados localmente,5 en ejecución y13 pendientes; aceptación completa no acreditada. El porcentaje global vigente es63,89% (46/72);61,11% es la base histórica del plan restante.

## Actualización74 · R10 y R18

Subsanada localmente la desconexión del nuevo flujo de costos con Analemática y ambos paneles: comandos autenticados, contrato de respuesta, formulario con capacidad explícita, dos confirmaciones, recuperación y descarte al cerrar sesión.12 pruebas nuevas HTTP/contrato y40 comprobaciones Chromium. [Entrega74](IMPLEMENTACION_74.md). R10 conserva pendientes laborales/electrónicos/productivos y R18 otros recorridos; no se modifican sus aceptaciones completas ni el denominador.

## Actualización75 · Liquidación declarada de suplementos

R10 y R18 incorporan horas extra y recargos por minutos/factores/divisor declarados desde ambos paneles, con base explícita de contribuciones. Asiento, detalle y costo operacional concilian; segunda planilla superpuesta no vuelve a causar salario base.16 pruebas ORM nuevas, un recorrido HTTP adicional y68 comprobaciones Chromium (suplementos y regresión base). [Entrega75](IMPLEMENTACION_75.md). Se mantienen abiertos clasificación legal/horarios reales, otras novedades, nómina electrónica y cualificación productiva; no se cierra R10 ni se duplica el porcentaje de ACC-013.

## Actualización76 · R12 y R18

Se adelantó el subconjunto COP independiente de valoración FX: coincidencias ambiguas seleccionadas, diferencias pendientes por fila, conciliación parcial sin falsa completitud, reservas de referencias pendientes, liberación/revisión y lectoresv2.17 pruebas ORM/API,2 HTTP corporativas y6 de contrato nuevas;70 comprobaciones Chromium del flujo parcial y regresión completa. [Entrega76](IMPLEMENTACION_76.md). R12 continúa en ejecución: pendientes saldos completos, división/agrupación de importes, FX y fuente auténtica; R11 conserva su dependencia para valoración. Estado del plan:2 verificados localmente,6 en ejecución y12 pendientes; no se declara cierre de los20.

## Actualización77 · Saldos y cobertura de período declarado

R12 y R18 añaden cotejo explícito de apertura/cierre, entradas/salidas y movimientos contables sin asociación, calificación separada de período y control de cambios retroactivos.14 pruebas ORM,1 HTTP y4 de contrato nuevas;78 comprobaciones Chromium (período y regresión parcial) y capturas de ambos paneles. [Entrega77](IMPLEMENTACION_77.md). No autentica al banco por una declaración del propietario; siguen pendientes snapshots/volumen, períodos sin movimientos, importes divididos/agrupados, FX y aceptación bancaria/profesional. Los20 hitos conservan sus criterios completos, sin créditos porcentuales duplicados.
