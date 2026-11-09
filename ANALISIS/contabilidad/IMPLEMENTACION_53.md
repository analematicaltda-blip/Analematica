# Implementación 53 · Nómina base revisada y causación real

**Avance global: 50,00 % (36/72), desde 47,22 % (34/72).** Primer incremento funcional y verificación de ACC-013. No se acredita aceptación completa, normativa vigente ni pagos. Los 20 paquetes conservan sus criterios: 4 verificados localmente, 7 en ejecución y 9 pendientes; H13 sigue en ejecución. Aceptación completa: 0/24.

## Flujo operativo en ERP y Analemática

Ambos paneles usan el mismo formulario y libro mayor. El titular selecciona planilla, contrato, días, política y cuentas; revisa la propuesta y luego confirma por separado la causación. La política no contiene tarifas legales por defecto. Reglas, vigencia, versión y divisor se declaran expresamente y se conservan con una huella; esa declaración no certifica validez laboral.

La propuesta obtiene salario, estado y pertenencia del empleado/contrato desde las fuentes actuales. Acepta una base proporcional para contratos fijos/indefinidos CO: salario contractual × días declarados / divisor declarado. Calcula en centavos enteros con HALF_UP, sin floats ni redondeo monetario implícito. Los componentes declarados pueden ser deducción del trabajador, aporte del empleador o provisión; no se clasifican automáticamente como salud, pensión, prima u otra obligación legal.

La primera confirmación persiste revisión, responsable, versión, cuentas y fuentes, sin postear. La segunda recalcula/compara la fuente, valida nuevamente identidad, período, moneda y cuentas y crea un asiento real mediante LedgerEngine. Detalles, cabecera CONTABILIZADA, recibo y prueba de origen se registran atómicamente. Si falla la prueba, se revierte todo; no queda un estado financiero fingido. El evento usa una clave estable por planilla. Repetir la misma revisión recupera el asiento y no duplica salario, aportes ni provisiones.

El caso sintético usa salario contractual 1000,00, 15 días y divisor 30: base 500,00, deducción declarada 20,00, neto 480,00, aporte 60,00 y provisión 40,00. Débitos/créditos suman 600,00. Estas cifras son datos de prueba, no tasas recomendadas ni una liquidación normativa. No se crea orden bancaria, dinero transferido, documento oficial ni estado PAGADA.

## Controles de origen y recuperación

Se exigen empresa propia activa, vínculo verificado vigente y actor personal activo; el UUID de proveedor no se equipara al Tenant. Bloqueo proveedor→empresa→planilla y lecturas de contrato/empleado con bloqueo protegen la propuesta/posteo. La revisión corresponde al mismo actor y a la última versión de esa planilla. Una versión de política ya declarada no puede redefinirse con otro contenido.

Período cerrado/ambiguo, fuente cambiada, cuenta ajena/inactiva/tipo incorrecto, contrato inactivo/solapado, deducción mayor que base o saldo inicial sin conciliar bloquean la operación. Una planilla distinta no puede volver a causar un intervalo que ya tiene detalle del mismo trabajador. El modo base rechaza novedades asignadas o pendientes de asignación y ausencias/incapacidades superpuestas, en lugar de omitirlas.

Recuperar estado verifica revisión, recibo, hash del asiento, importe por cuenta, cabecera y proyección del detalle. Una alteración de totales impide reintentar como si nada hubiera ocurrido. Retirar al trabajador después de contabilizar no destruye el origen histórico. La recuperación no restaura confirmaciones. Una contrapartida conserva el original, pero no se ofrece todavía un flujo laboral completo de reversión/reapertura: no se vuelve a causar automáticamente esa misma planilla.

El puente corporativo conserva doble sesión, origen fijo, CSRF, vínculo independiente y lista de acciones permitidas. Verifica empresa y planilla en la propuesta/resultado y que no haya transferencia. No existe atomicidad distribuida SQLAlchemy–Django; ante respuesta incierta se consulta/reintenta la misma revisión persistida.

## Interfaz y alcance acotado

Se conservan azul metalizado, azul claro y texto blanco, con tablas desplazables y formulario móvil. El panel muestra reglas persistidas, cuentas, componentes y resultados, permite añadir/eliminar trabajadores, invalida propuesta/autorizaciones al editar y limpia datos ante cambio de identidad. El cierre de sesión ERP y la pérdida del token corporativo descartan los datos del panel. No se promete borrado forense de memoria.

El catálogo declara su límite: 20 planillas recientes, 100 contratos y 200 cuentas; la UI informa truncamiento. El núcleo admite 1–10 trabajadores y 1–8 componentes por revisión, exclusivamente COP, períodos de hasta 32 días calendario y fuentes compatibles. La pantalla permite un componente agregado de cada clase. Son límites explícitos de este incremento; búsqueda/paginación de nómina completa y componentes laborales especializados permanecen pendientes.

El centro de costo del empleado se conserva en la fuente para trazabilidad; el asiento agregado todavía no incorpora dimensiones de costo por centro/paquete. La proyección DetalleLiquidacion contiene base, días y totales; sus otros campos legales en cero son valores de esquema, **no cálculos de obligaciones legales**. El desglose autorizado está en la revisión persistida. El serializador legado conserva estados históricos como NOT_VERIFIED; la ruta de estado revisado comprueba el nuevo origen. Reconciliar históricos y homologar todas las proyecciones es trabajo pendiente.

## Qué continúa pendiente en H13

- Reglas laborales vigentes aceptadas por profesional, fuentes y documentos legítimos, evidencia de jornada y autorizaciones reforzadas.
- Novedades, recargos/horas, incapacidades, ausencias, contratos especiales, prestaciones y aportes reglamentarios detallados.
- Pipeline operación–personas–finanzas con guardas SST completas y asignación por servicio/paquete; geolocalización no causa nómina por sí sola.
- Documentos laborales electrónicos oficiales, aceptación tributaria y pagos con sus autorizaciones específicas.
- Reversión/reapertura del negocio, escalamiento por lotes, migraciones nativas reales, conciliación y custodia independiente de evidencia.
- Auditoría de los restantes auxiliares/indicadores laborales y de protección de campos cifrados legados; este incremento no valida todo el módulo.

Las rutas legadas liquidar/contabilizar sin esta revisión permanecen en503; no se habilita el cálculo antiguo ni la ejecución ciega por un agente. Los nuevos endpoints son revisar-nomina, contabilizar-nomina-revisada, estado-nomina-revisada y fuentes-nomina-revisada dentro del API contable existente.

Resultados finales y evidencias: [implementacion-53.json](evidencias/implementacion-53.json). Sin pagos, acciones DIAN reales, commits, push ni actualización de main.

## Verificación final

- **353 pruebas Python aprobadas**, incluidas 22 del nuevo cálculo/causación y 1 de integración HTTP corporativa. Sin omisiones.
- **39 escenarios contables PostgreSQL aprobados**, incluidos competencia por revisión y posteo/reintento de la misma planilla: un asiento y un detalle; restauración también aprobada.
- **163 comprobaciones Chromium aprobadas**: 53 ERP, 30 corporativas, 52 de apertura/políticas y 28 del nuevo panel de nómina. Datos sintéticos; cierre ERP y pérdida de token por evento storage corporativo verificados en los harness respectivos.
- TypeScript estricto de cuatro componentes sin errores; no se acredita build Next completo.
- Suite final con fuentes estables y logs/manifiesto verificables en `/tmp/sgacd-payroll-53-release`. Su reporte y hashes se conservan en evidencia53. Los ensayos intermedios durante cambios no se presentan como cierre de regresión.

Se corrigieron fallos encontrados en desarrollo: el estado monetario de cabecera se relee desde base antes de verificar el posteo; las expectativas de prorrateo se contrastaron con el salario real del fixture. Los recorridos de limpieza usan los controles disponibles en cada harness, sin asumir un botón/login de navegación que el harness no incluye.
