# Implementación 51 · Aperturas conservadas y políticas tributarias

**Avance global: 44,44 % (32/72), sin incremento de puntos.** Las correcciones refuerzan tareas ya acreditadas; no se acredita dos veces una misma tarea. Aceptación completa: 0/24. De los 20 paquetes, 4 están verificados localmente, 5 en ejecución y 11 pendientes. No se han completado los 20 ni habilitado producción.

## H05 · Conciliación de saldos iniciales

Los dos paneles permiten revisar saldos originales de balance en COP y confirmar por separado su apertura. El servicio exige titular/empresa verificados, período abierto único para nuevos asientos, origen balanceado, soporte declarado por huella y revisión vigente del mismo actor. No inventa contrapartidas, no convierte FX y no pone a cero los saldos originales. La doble confirmación es un flujo de revisión, no una firma digital del soporte.

El asiento se registra atómicamente con recibo y prueba de origen. Repetir la misma revisión recupera el mismo asiento. Cambiar una cuenta o borrar todos los saldos originales bloquea los reportes: no permite ocultar una discrepancia. La contrapartida exacta conserva el original; retirar una cuenta del catálogo activo no invalida un origen histórico íntegro. El diagnóstico diferencia una referencia preservada y conciliada de un legado pendiente.

Para libros que ya contienen la apertura, el titular puede indicar expresamente su UUID. Solo se vincula si coinciden fecha, empresa, moneda, cada cuenta e importe, hash y estado sin contrapartida; no puede haber fechas económicas anteriores. La vinculación puede referir un período cerrado porque únicamente registra evidencia, sin editar ni duplicar el asiento o su hash. Una discrepancia exige conciliación separada. La carrera PostgreSQL conserva un solo registro de vinculación.

Límites: máximo100 cuentas de origen no nulas; empresas COP y asientos v2 exactos. No se califican legados arbitrarios, archivos contables reales, migración por lotes, valoraciones FX ni fuente cambiaria autorizada. La prueba de origen usa eventos existentes; no constituye custodia independiente frente a un operador privilegiado de base de datos. H05 continúa en ejecución.

## H06 · Política explícita de cálculo

El titular declara código, vigencia, redondeo y componentes en puntos básicos. Revisar y registrar son confirmaciones separadas. Cada versión conserva su huella y no admite sobrescritura ni vigencias solapadas; carreras para la misma versión rechazan el competidor. La consulta selecciona explícitamente empresa, versión, fecha, categoría y dirección.

El cálculo utiliza centavos enteros y redondeo por componente HALF_UP, independiente del contexto Decimal. Separa impuesto generado y retención; no cobra impuesto positivo a categorías exenta/excluida. La simulación de nota crédito invierte los importes, sin emitir una nota fiscal real. Los casos sintéticos100,00 +19,00 -2,50 =116,50 verifican el contrato; esas tasas son datos de prueba, no una recomendación tributaria.

No se infiere normativa ni se certifica cumplimiento DIAN. Esta entrega registra políticas y calcula propuestas; todavía debe conectarse al reconocimiento/solicitud fiscal con reglas revisadas, retenciones contabilizadas e IVA descontable. Tampoco reemplaza una versión dentro de una vigencia ya registrada: requiere tratamiento posterior explícito. El historial API pagina 20 versiones; el panel muestra su primera página. H06 continúa en ejecución.

## Integración y conservación visual

ERP y Analemática usan el mismo renderizador de apertura/políticas y el mismo ledger. El puente corporativo mantiene vínculo independiente, doble sesión, CSRF y acciones permitidas por nombre; no acepta escoger otra empresa desde una orden. Vincular una apertura devuelve correctamente ausencia de escritura en el ledger, diferenciada de registrar su evidencia.

Las pantallas conservan azul metalizado, azul claro y texto blanco. Edición, cambio de contexto y cierre de sesión limpian propuestas/resultados y confirmaciones; no se restauran autorizaciones. Los controles móviles y los flujos se verifican en Chromium contra ambas APIs con datos sintéticos. No se promete borrado forense de memoria.

## Verificación y pendientes

Los resultados y recuentos finales se conservan en [evidencia51](evidencias/implementacion-51.json). Se ejecutan regresión contable, concurrencia/restauración PostgreSQL, ambos paneles y comprobación TypeScript estricta de componentes. Esto no equivale a un build Next completo: falta resolver el paquete compartido del entorno para esa aceptación.

El [plan de 20 hitos](PLAN_SUBSANACION_20_HITOS.md) conserva todos los criterios y dependencias. H07–H13, H15–H16 y H18–H19 aún requieren desarrollo local, además de las validaciones externas indicadas; no se presentan todos los pendientes como falta de credenciales. Continúan firma/UBL, transporte y acuses DIAN auténticos, BYOS/recuperación, guardas SST, nómina/costos, analítica turística, sostenibilidad, aprobaciones financieras y sincronización offline cifrada. H14/H17/H20 también conservan su alcance parcial.

No se ejecutaron pagos, accesos fiscales reales, cambios de datos de clientes, commits, push ni actualización de main.

### Resultados finales

- **308 pruebas Python aprobadas**, sin omisiones.
- **37 escenarios contables PostgreSQL aprobados**, incluidos carreras de apertura nueva, vínculo existente y registro de versión tributaria; restauración local también aprobada.
- **135 comprobaciones Chromium aprobadas**:52 nuevas en cuatro recorridos ERP/Analemática (apertura nueva/existente),53 de regresión ERP y30 corporativas.
- TypeScript estricto de cuatro componentes:0 errores; sintaxis JS y controles de progreso aprobados.
- Suite final con fuentes estables y logs/manifiesto verificables en `/tmp/sgacd-remediation-51-release`; su reporte y hashes se conservan en la evidencia JSON. No es certificación productiva.

La regresión corporativa detectó una espera frágil del test:150ms no garantizaban que terminara una página bajo carga. Se sustituyó por esperar el estado inactivo del formulario y se repitió el recorrido completo con éxito; no se redujeron las aserciones de catálogo. Una ejecución inicial con Python fuera del entorno virtual falló por dependencias ausentes y no se cuenta como prueba aprobada.
