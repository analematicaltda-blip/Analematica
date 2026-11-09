# Plan de implementación contable · Analemática y ERP turístico

**Seguimiento único actual:** [novedades, hallazgos y pendientes](CIERRE_20_HITOS.md). Actualizar ese archivo; no abrir un análisis por entrega.

Directriz base: matriz de siete pools recibida del usuario el 2026-11-08. Estado: **inicio de implementación, no producción**. Se conserva y refuerza el motor compartido; no se sustituye el sistema ni se ejecutan migraciones sobre datos reales.

- [Directriz y contratos](DIRECTRIZ.md).
- [Matriz de implementación](matriz-pools.csv): tareas, prioridad, dependencias, responsables por área y criterios verificables.
- [Hallazgos y primera corrección](HALLAZGOS_01.md).
- [Posteo e informes, implementación02](IMPLEMENTACION_02.md): recibos/outbox transaccionales, identidad ERP, hashes versionados, FX y reportes.
- [Decisiones de arquitectura](DECISIONES.md): consistencia, cifrado, regulación, autorizaciones y límites de medición.
- [Entrega al repositorio](../entregas/ENTREGA_MAIN_37.md): consolidación, pruebas y estado de publicación.

Código canónico contable: `BACKEND/ANALEMATICA-BACKEND/core_erp/accounting`. Los modelos contables de Analemática y ERP turístico son proxies de ese núcleo. `BACKEND/deployment/tourism_bindings.py` preserva los namespaces originales. El UUID de TourismProvider no equivale al UUID de Tenant contable: usar el vínculo verificado antes de conectar nuevos flujos.

Última ampliación: [implementación77](IMPLEMENTACION_77.md), saldos y cobertura de período bancario declarado desde ERP y Analemática; [contrato y pendientes](OPERACION_COSTOS_NOMINA.md). Avance global63,89%, sin cierre de los20 hitos ni aceptación productiva.

## Orden de ejecución

1. **Fundación y seguridad del ledger (Pool3/4):** invariantes monetarias, ámbito empresarial, periodos, idempotencia, auditoría, concurrencia y reversión. Primera corrección entregada con nueve pruebas ORM; todavía falta integrar el flujo completo de posteo y sus efectos.
2. **Eventos y ciclo comercial (Pool1/3):** outbox transaccional, contratos versionados y consumidores idempotentes; después facturación y bóveda cliente/BYOS.
3. **Operación, personal y costos (Pool2):** novedades verificadas, aptitudes/permisos, reglas laborales vigentes y causaciones trazables.
4. **Fiscalidad e integraciones (Pool1/4):** adaptadores oficiales de habilitación con secretos del cliente y estados pendientes/aceptados/rechazados; sin comprobantes inventados.
5. **Analítica explicable y sostenibilidad (Pool5/6):** proyecciones reproducibles, ratios definidos, simulaciones y factores versionados.
6. **Asistencia supervisada (Pool7):** consultas de solo lectura y sugerencias con evidencia; ejecución separada con dos autorizaciones del solicitante y tercera de impacto.

En cada corte: reproducir hallazgo → evaluar dependencias → corregir en alcance limitado → probar aislamiento e integridad → registrar evidencia y actualizar matriz. Un archivo, una regla declarada o un hash no acreditan un proceso operativo. No se presupone un 99.8% de precisión, latencia250ms ni inmunidad a vulneración.

Las tareas pendientes del plan anterior siguen en [el registro del ecosistema](../produccion/PENDIENTES-PRODUCCION-ECOSISTEMA.md). La contabilidad no habilita por sí sola pagos, DIAN, bancos, nómina electrónica, publicación, datos de salud, automatización de cuentas ni billetera empresarial para empleados.

La implementación02 avanza el backend y sus contratos; no activa publicación externa, tributación, bancos, bóveda cliente, nómina, IA ni libera producción. Consultar sus límites y migraciones antes de usar el código con una base existente.

- [Implementación03](IMPLEMENTACION_03.md): consumidor local transaccional, estados/reintentos y proyección diaria con recibos. [Operación del worker](OPERACION_PROYECCIONES.md). Publicación externa y producción siguen pendientes.

- [Implementación04](IMPLEMENTACION_04.md): rentabilidad empresarial con cuentas de origen y periodos.
- [Implementación05](IMPLEMENTACION_05.md): clasificación revisada y liquidez ácida desde el libro mayor. Cobertura y evidencia requieren validación contable real.

- [Implementación06](IMPLEMENTACION_06.md): panel web de indicadores ERP y eliminación de conclusiones contables iniciales sin evidencia en Analemática.

- [Progreso verificable](PROGRESO.md): línea base de 24 tareas y 72 hitos; ver [implementación07](IMPLEMENTACION_07.md) para el recorrido integrado ERP.

- [Implementación08](IMPLEMENTACION_08.md): formulario de clasificación ERP, revisión, conflictos y guardado supervisado; progreso 22,22 %.

- [Implementación09](IMPLEMENTACION_09.md): historial paginado verificable de revisiones, API y consulta ERP; avance 22,22 %.

- [Implementación10](IMPLEMENTACION_10.md): cálculo de liquidez con revisión histórica explícita; progreso 22,22 %.

- [Implementación11](IMPLEMENTACION_11.md): escenarios Monte Carlo reproducibles de caja, API protegida y pruebas; avance 25,00 %.

- [Implementación12](IMPLEMENTACION_12.md): backtesting temporal de caja con holdout separado y API empresarial; avance 25,00 %.

- [Implementación13](IMPLEMENTACION_13.md): sensibilidad aditiva con remuestreo común y API empresarial; progreso 25,00 %.

- [Implementación14](IMPLEMENTACION_14.md): formulario ERP de escenarios y sensibilidad con sesión real; avance 25,00 %.

- [Implementación15](IMPLEMENTACION_15.md): interfaz ERP de backtesting y comparación de errores; avance 25,00 %.

- [Implementación16](IMPLEMENTACION_16.md): backtesting de múltiples ventanas con errores agregados y solapamiento explícito; avance 25,00 %.

- [Implementación17](IMPLEMENTACION_17.md): inmutabilidad SQL local de asientos/líneas contabilizados y políticas históricas; avance 25,00 %.

- [Implementación18](IMPLEMENTACION_18.md): disponibilidad condicionada a controles SQL y endurecimiento PostgreSQL; avance 27,78 %.

- [Implementación19](IMPLEMENTACION_19.md): recuperación comprobada del ledger PostgreSQL aislado. [Procedimiento de validación](OPERACION_RECUPERACION.md). Avance 27,78 %.

- [Implementación20](IMPLEMENTACION_20.md): auditor de privilegios PostgreSQL de solo lectura, roles temporales reales y readiness opcional; avance 27,78 %.

- [Implementación21](IMPLEMENTACION_21.md): perfil revisable y flujo central contable real con rol PostgreSQL limitado; avance 27,78 %.

- [Implementación22](IMPLEMENTACION_22.md): contrapartida multimoneda neutra a valor histórico, concurrencia y rol restringido probados; avance 27,78 %.

- [Implementación23](IMPLEMENTACION_23.md): diagnóstico empresarial de conciliación, API/CLI y rol limitado, sin reescritura; avance 27,78 %.

- [Implementación24](IMPLEMENTACION_24.md): panel ERP de diagnóstico, hallazgos y cuentas pendientes, sin reparaciones automáticas; avance 27,78 %.

- [Implementación25](IMPLEMENTACION_25.md): SDK de sobre cifrado cliente, AAD y rewrap con interoperabilidad; avance 30,56 %. No bóveda completa.

- [Implementación26](IMPLEMENTACION_26.md): preview estructural de sobres fiscales con alcance empresarial y lector JSON acotado; avance 30,56 %. Sin almacenamiento.

- [Implementación27](IMPLEMENTACION_27.md): destino PostgreSQL cliente explícito, idempotencia y controles de inmutabilidad; avance 33,33 %. Sin activación UI/API ni aceptación BYOS completa.

- [Implementación28](IMPLEMENTACION_28.md): respaldo y restauración del destino documental PostgreSQL desechable, con sobres idénticos y controles conservados; avance 33,33 %.

- [Implementación29](IMPLEMENTACION_29.md): revocación SQL en conexión abierta y desconexión/reintento sin duplicación; avance 33,33 %.

- [Implementación30](IMPLEMENTACION_30.md): contrato versionado de solicitud de factura, totales exactos y claves deterministas; avance 36,11 %. Sin productor CRM ni emisión fiscal.

- [Implementación31](IMPLEMENTACION_31.md): solicitudes de factura persistidas en outbox con rollback y concurrencia comprobados; avance 36,11 %. Sin productor CRM ni consumidor fiscal.

- [Implementación32](IMPLEMENTACION_32.md): importes fiscales en centavos enteros, independientes del contexto decimal global; avance 36,11 %. Hallazgos de integración de reservas documentados.

- [Implementación33](IMPLEMENTACION_33.md): confirmación de reservas con empresa/titular verificados y estados válidos; eliminación de SIM-123; avance 36,11 %.

- [Implementación34](IMPLEMENTACION_34.md): confirmación concurrente y revocación tras lectura inicial verificadas en PostgreSQL; avance 36,11 %.

- [Implementación35](IMPLEMENTACION_35.md): evento de confirmación de reserva atómico y único, sin historial retrospectivo fabricado; avance 36,11 %.

- [Implementación36](IMPLEMENTACION_36.md): consulta empresarial de cola comercial, sin confundir estados de transporte con aceptación fiscal; avance 36,11 %.

- [Implementación37](IMPLEMENTACION_37.md): panel ERP de cola comercial, contrato y sesión real probados en Chromium; avance 36,11 %.

- [Implementación38](IMPLEMENTACION_38.md): preguntas contables acotadas de solo lectura, herramientas autorizadas y fuentes explícitas; avance 38,89 %. Sin LLM o SQL generado.

- [Implementación39](IMPLEMENTACION_39.md): interfaz de consulta contable con fuentes explícitas, sesión real y limpieza por contexto; avance 38,89 %.

- [Implementación40](IMPLEMENTACION_40.md): limpieza al volver al contexto y rechazo de respuestas tardías verificados; avance 38,89 %.

- [Implementación41](IMPLEMENTACION_41.md): respuestas contables privadas/no-store y Vary comprobados en errores y sesión real; avance 38,89 %.

- [Implementación42](IMPLEMENTACION_42.md): parser exclusivo de consultas de 8 KiB, profundidad limitada y rechazo de JSON ambiguo; avance 38,89 %.

- [Implementación43](IMPLEMENTACION_43.md): agregación de rentabilidad limitada a cuentas relevantes sin omitir controles generales; avance 38,89 %.

- [Implementación44](IMPLEMENTACION_44.md): flujo funcional ERP de reserva a revisión persistida y solicitud con dos confirmaciones, UI/API/PG probados; avance global 38,89 %.

- [Implementación45](IMPLEMENTACION_45.md): reserva con prestación declarada a asiento real y contrapartida, con doble confirmación y efectos monetarios verificados; avance global 38,89 %.

- [Implementación46](IMPLEMENTACION_46.md): consola Analemática conectada por vínculo y doble sesión a reportes reales del ledger ERP; avance global 38,89 %. [Preparación del puente](OPERACION_PUENTE_CORPORATIVO.md).

- [Implementación47](IMPLEMENTACION_47.md): aplicación de recibos previos de anticipos al reconocimiento, cartera neta, contrapartida y exclusión de reutilización; avance global 38,89 %.

- [Implementación48](IMPLEMENTACION_48.md): escritura corporativa y contrapartida reales, conciliación tributaria en ambos sistemas, bloqueo transversal de reversión de anticipos y retirada de aceptación/firma DIAN ficticias; avance global **41,67 %**. [Reporte por frentes](PROGRESO.md), [bloqueos por tarea](BLOQUEOS_POR_TAREA.md) y [habilitación DIAN](DIAN_HABILITACION.md).

- [Plan autónomo de 20 hitos](PLAN_SUBSANACION_20_HITOS.md): hallazgos, dependencias, criterios y bloqueos externos. [Implementación49](IMPLEMENTACION_49.md): H01 verificado localmente, aislamiento del API legado y retirada de XML/URL; avance global 41,67 % sin créditos duplicados.

- [Implementación50](IMPLEMENTACION_50.md): H02–H04 verificados localmente; H14 comparación bancaria de lectura y H17 asistente corporativo como incrementos parciales. **Avance global44,44 %**; cuatro de20 paquetes verificados locales, sin acreditar cierre de los 20.

- [Implementación51](IMPLEMENTACION_51.md): apertura COP nueva o vinculación exacta de apertura existente sin duplicación, políticas tributarias versionadas y cálculo explícito de impuesto/retención en ambos paneles. Avance global44,44 %;4/20 paquetes verificados localmente, 5 en ejecución y 11 pendientes.

- [Implementación52](IMPLEMENTACION_52.md): privacidad y alcance empresarial/clínico de SG-SST, métricas sin denominador ficticio, suspensión interna auditada; planillas acotadas y retirada de éxito contable ficticio. Avance global47,22 % por incremento parcial ACC-012; H12/H13 siguen abiertos.

- [Implementación 53](IMPLEMENTACION_53.md): nómina base declarada con doble revisión, causación real de base/deducciones/aportes/provisiones y recuperación idempotente, desde ERP y Analemática. Avance global **50,00 %**, sin acreditar nómina normativa completa ni pagos.

- [Implementación 54](IMPLEMENTACION_54.md): conciliación de correspondencias persistente y liberación con historial, dos confirmaciones para cada flujo y reservas exclusivas bajo bloqueo de empresa, en ambos paneles/APIs. Avance global50,00 % sin duplicar ACC-015; autenticidad bancaria y saldo integral siguen pendientes.

- [Implementación 55](IMPLEMENTACION_55.md): disponibilidad diaria revisada sobre habitaciones físicas y RevPAR/GOPPAR desde ledger contabilizado, en ambos paneles; 403 pruebas Python, 45 escenarios PostgreSQL y 227 comprobaciones de navegador. Avance global50,00 %; 4 hitos verificados localmente, 8 en ejecución y 8 pendientes.

- [Implementación 56](IMPLEMENTACION_56.md): estimación ambiental explícita por actividad/factor en ambos paneles y APIs, precisión decimal, procedencia y fronteras separadas; sin pasivos automáticos ni certificación ESG. Incremento y verificación ACC-018: **52,78 % (38/72)**; H16 en ejecución.

- [Implementación 57](IMPLEMENTACION_57.md): mediciones ambientales persistentes con dos confirmaciones, recuperación sin restaurar autorizaciones, versiones inmutables de factores y exclusión de actividades ya registradas. Avance52,78 % sin repetir créditos ACC-018; H16 permanece abierto.

- [Implementación 58](IMPLEMENTACION_58.md): borradores ambientales cifrados en IndexedDB, recuperación/cambio de contraseña sin red, conflicto entre pestañas y reanudación online con dos confirmaciones en ambos sistemas. ACC-022 aporta incremento y verificación: **55,56 % (40/72)**; H19 en ejecución, sin aceptación nativa/productiva.

- [Implementación 59](IMPLEMENTACION_59.md): exportación y restauración de copias cifradas en ambos paneles, sin red ni autorizaciones restauradas; rechaza contraseña/contexto incorrectos y sobrescritura con copias diferentes. Avance55,56 % sin repetir ACC-022.

- [Implementación 60](IMPLEMENTACION_60.md): borrador UBL en memoria en ambos paneles, aritmética BigInt, escape seguro y cuatro documentos comprobados contra XSD de referencia con procedencia conservada; sin firma, CUFE ni validación DIAN. ACC-009 aporta incremento y verificación: **58,33 % (42/72)**; H07 en ejecución.

- [Implementación61](IMPLEMENTACION_61.md): documentos cifrados recuperables y rotación KEK con paquetes autenticados/versionados en ambos paneles, sin enviar llaves o texto claro al servidor. Runtime reproducible del SDK existente. Avance58,33 % sin créditos repetidos; H11 en ejecución, custodia/almacenamiento soberano reales pendientes.

- [Implementación62](IMPLEMENTACION_62.md): API independiente del cliente, paquetes versionados en PostgreSQL, rol mínimo, revocación, cargas cifradas directas y recuperación histórica. Ruta Chromium/HTTPS/PostgreSQL real aislada; paneles cerrados sin perfil aprobado. [Operación BYOS](OPERACION_BYOS_PAQUETES.md). Avance58,33 % sin repetir ACC-011; H10 en ejecución.

- [Implementación63: firma XAdES local de laboratorio](IMPLEMENTACION_63.md), [operación y límites](OPERACION_FIRMANTE_LOCAL.md). H08 en ejecución; no cualifica firma DIAN ni custodia hardware.

- [Implementación64: ensayo financiero persistente ERP/corporativo](IMPLEMENTACION_64.md) y [operación](OPERACION_SIMULACION_FINANCIERA.md). Primer incremento verificado de ACC-021; sin pagos, RPA de ejecución ni aceptación completa.

- [Implementación65: corrección ambiental conservando el original](IMPLEMENTACION_65.md) y [operación](OPERACION_CORRECCIONES_AMBIENTALES.md). Revisión efectiva en ambos paneles; sin créditos globales duplicados ni certificación ESG.

- [Implementación66: acuses y reintentos de laboratorio H09](IMPLEMENTACION_66.md), [operación](OPERACION_ACUSES_LABORATORIO.md) y [faltantes para cerrar cada paquete](CIERRE_20_HITOS.md). Sin aceptación DIAN ni créditos globales duplicados.

- [Implementación67: vías de elusión del despacho genérico](IMPLEMENTACION_67.md) y [operación](OPERACION_GUARDAS_DESPACHO.md). Planificación/suspensión auditadas; activación bloqueada hasta cualificar aptitud, EPP y jornada.

- [Nuevo plan:20 hitos restantes](PLAN_REMANENTE_20_HITOS.md), [registro de ejecución](PLAN_REMANENTE_20_HITOS.json) y [entrega68](IMPLEMENTACION_68.md). Base original preservada; política/reserva/ledger verificados localmente, aceptación fiscal pendiente.

- [Implementación69](IMPLEMENTACION_69.md): datos persistentes por trabajador, autorización profesional cifrada, EPP, jornadas/descanso, revocaciones y despacho genérico con doble confirmación. [API y operación](OPERACION_DATOS_SEGURIDAD_TRABAJADOR.md). Sin datos ficticios ni cierre contable automático.

- [Implementación70](IMPLEMENTACION_70.md): compras/ventas con IVA descontable/generado y retenciones por componente, posteo y contrapartidas con dos confirmaciones, API ERP y puente Analemática. [Contrato](OPERACION_HECHOS_TRIBUTARIOS.md).

- [Implementación71](IMPLEMENTACION_71.md): conciliación integrada en ambos paneles, validación de fuentes/sumas en lote y benchmark reproducible. [Operación](OPERACION_CONCILIACION_INTEGRAL.md), [medición](OPERACION_BENCHMARK.md). Primer incremento ACC-023;63,89%, sin aceptación productiva.

- [Implementación72](IMPLEMENTACION_72.md): compras nativas desde ambos paneles, proveedor/factura persistentes, catálogo con gastos, reserva contra bypass y dos confirmaciones. [Operación](OPERACION_COMPRAS_NATIVAS.md).
