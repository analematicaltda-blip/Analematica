# Implementación 06 · Consulta web y estados contables verificables

Estado: desarrollo local. Se conserva el motor compartido y no se habilitan pagos, fiscalidad ni producción. No se hicieron commits ni push.

## ERP turístico

Nueva ruta `/dashboard/prestador/mi-negocio/gestion-contable/indicadores-ledger`, enlazada desde la pantalla contable existente. Reutiliza la sesión ERP y consulta el listado de empresas autorizadas; no acepta saldos ni credenciales en URL. El usuario inicia sesión mediante el acceso seguro existente y selecciona su empresa.

El panel consulta rentabilidad y liquidez ácida de los endpoints del núcleo compartido. Muestra periodo, moneda, ingresos, gastos, resultado, margen, liquidez, revisión de clasificación y cuentas de origen de rentabilidad. Presenta avisos específicos cuando falta clasificación, el denominador no permite calcular o los saldos requieren revisión. Conserva importes como cadenas decimales: no convierte dinero a `Number` ni recalcula el ledger en el navegador.

Al cambiar de empresa, identidad o fechas se ocultan inmediatamente los resultados anteriores y se cancelan solicitudes pendientes. No se reutilizan valores de otro contexto. Errores de autorización o respuestas incompletas no se muestran como ceros. Consulta exclusivamente GET, sin configuración, posteo ni transferencias.

Panel azul metálico, bordes celestes y texto blanco. Fechas y recarga accesibles mediante etiquetas, foco visible, tabla de fuentes y avisos de estado/error. Adaptación móvil verificada en el componente.

## Analemática

Se corrigió un hallazgo: el panel estático mostraba conciliación al 100%, cierre, estado fiscal y montos de depreciación antes de consultar un libro mayor autenticado. Esos seis estados ahora indican que están pendientes de verificación. Las respuestas del asistente dejan de rellenar conclusiones contables o tributarias; no constituyen evidencia de conciliación o cierre.

Se conserva la estructura y los campos de configuración, distinguiéndolos de saldos verificados. La conexión autenticada de la consola corporativa al Tenant contable aún está pendiente; no se reutilizan tokens entre sistemas ni se inventa equivalencia entre identidades. Este corte no presenta la consola de Analemática como una consulta contable terminada.

## Verificación y límites

- Tipado TypeScript estricto de la nueva ruta, panel e imports: sin errores.
- Chromium: valores decimales; cambio de empresa; permiso denegado; clasificación pendiente; respuesta incompleta; fechas inválidas; salida de sesión; texto blanco y superficie azul; ausencia de desbordamiento móvil; peticiones GET; estados iniciales de Analemática sin certificaciones ficticias.
- El navegador usa respuestas API sintéticas controladas. Es una prueba de contrato de interfaz, no un recorrido integrado con Django ni con cuentas reales. Los permisos y cálculos backend tienen evidencia separada en los cortes 04 y 05.
- Parser de fuentes: sin errores sintácticos. Conserva advertencias de páginas heredadas; no acredita compilación completa ni navegación de todas las rutas.
- Prueba de navegador añadida al workflow existente; no ejecutada en GitHub porque no se ha publicado este trabajo.

Evidencia: `evidencias/implementacion-06.json`. No hay migraciones ni cambios de datos en este corte.

Pendientes: recorrido completo navegador→sesión→backend real, vinculación contable de la consola Analemática, formulario supervisado de clasificación, cobertura profesional de cuentas, resolución del bloqueo de compilación completa `@sarita/shared-ui`, pruebas de accesibilidad completas y verificación con datos reales. Continúan pendientes DIAN, BYOS, nómina, ratios por habitación/paquete y demás puntos de la matriz. No se cierra el plan maestro.
