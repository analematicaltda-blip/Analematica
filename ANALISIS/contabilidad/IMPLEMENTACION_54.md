# Implementación 54 · Conciliación revisada y liberación con historial

**Avance global: 50,00 % (36/72), sin nuevos créditos.** Este flujo amplía ACC-015, ya acreditada. H14 permanece en ejecución: no se ha verificado autenticidad bancaria ni conciliación completa de saldos. De los 20 paquetes, 4 están verificados localmente, 7 en ejecución y 9 pendientes; aceptación completa 0/24. No se declara completado el plan.

## Flujo disponible en los dos sistemas

ERP y Analemática comparten formulario, servicio y reglas de revisión. El titular elige una cuenta clasificada como efectivo, carga un CSV neutral y compara fechas/direcciones/importes contra líneas reales contabilizadas. La comparación anterior sigue siendo de solo lectura.

El nuevo flujo guarda una primera revisión de 1–30 coincidencias únicas, evidencia declarada por huella, versión/huella de clasificación y responsable. La segunda confirmación reserva las referencias y líneas asociadas y registra prueba de confirmación. No genera asientos, cobros, pagos ni movimientos bancarios. Recuperar el mismo resultado y reintentar la confirmación no duplican reservas ni registros financieros.

Se persisten registros derivados (fecha, dirección, importe, digest de referencia, línea/asiento y hashes), no el archivo CSV ni sus identificadores originales. La referencia se resume con SHA256 y contexto de empresa/cuenta; esto **no es anonimización ni cifrado**. Una huella declarada por el titular tampoco prueba que el archivo haya sido emitido por un banco. bank_verified y bank_connected permanecen en false.

La interfaz requiere confirmaciones separadas, muestra coincidencias y permite recuperar el estado sin restaurar autorizaciones. Se conserva la identidad azul/azul claro/blanco y el comportamiento móvil. Descartar retira archivo y resultados locales; no borra registros ya confirmados en el servidor. El catálogo limita 200 cuentas con aviso de truncamiento.

## Exclusividad y consistencia

Todas las escrituras del servicio toman el bloqueo de empresa. Una línea contable o referencia de transacción con reserva activa no puede reutilizarse desde otro archivo, aunque se cambie su identificador o importe. Las propuestas competidoras pueden existir antes de confirmar, pero solo una puede adquirir la misma línea.

Confirmar revalida cuentas, clasificación revisada, pertenencia/moneda COP, importes, fecha, lado y hash v2 del asiento. Una clasificación cambiada, cuenta ajena, divisa/valoración no admitida, línea faltante, movimiento revertido, revisión antigua o actor distinto bloquean. Las reservas y la prueba se escriben atómicamente: si falla la prueba, no queda una reserva parcial.

La exclusividad está implementada por el servicio bajo bloqueo de empresa y probada en PostgreSQL. **No existe una restricción SQL independiente de reserva activa por línea**, ni protección contra un escritor privilegiado que eluda el servicio. Los eventos outbox tampoco son un soporte WORM ni una firma independiente. Esto sigue siendo una condición de cualificación de seguridad/operación, no una garantía de invulnerabilidad.

## Liberación sin borrar evidencia

Para corregir una asociación se registra otra revisión con un motivo admitido (asociación incorrecta, soporte retirado o corrección contable) y huella del soporte. Una segunda confirmación del mismo actor añade la liberación. La confirmación, las reservas anteriores y su revisión permanecen en el historial; no se cambian ni eliminan líneas del ledger.

Una liberación repetida recupera el mismo resultado. Otra revisión de liberación no puede sobrescribir una ya confirmada. Después de liberar, una nueva revisión puede asociar el mismo movimiento con otra prueba y otro identificador de confirmación. La versión anterior queda históricamente confirmada y liberada; reintentar su confirmación no la reactiva.

Si aparece una contrapartida después de confirmar, recuperar estado marca requires_review y no presenta la coincidencia como válida actualmente. Permite revisar/liberar esa asociación sin reescribir contabilidad. Retirar una cuenta del catálogo activo no elimina la recuperación histórica mediante API; la navegación histórica de cuentas fuera del catálogo activo requiere ampliación de interfaz.

## Identidad e integración corporativa

Las rutas están en el API contable existente y exigen titular/empresa verificados, sesión y respuestas privadas/no-store. El puente corporativo conserva vínculo independiente, origen fijo, doble sesión, CSRF y una lista cerrada de operaciones. Verifica empresa, cuenta, huella de origen y/o declaración de conciliación según la operación. Ninguna URL, empresa o actor aportados libremente por el cliente sustituyen el contexto autorizado.

No hay transacción distribuida entre los dos backends. Ante un resultado incierto se recupera el estado por cuenta/huella del archivo o se reintenta la misma revisión. No se inventa otro resultado ni se restaura una autorización del navegador.

## Pendientes para completar H14

- Extractos legítimos, autorización del titular y contrastación independiente de titularidad/autenticidad; conectores bancarios con permisos mínimos si se habilitan.
- Identidad del instrumento bancario, conciliación de saldos inicial/final de un período y vínculo con el soporte soberano original.
- Archivos reales de proveedores, formatos adicionales, FX, fechas de valor, cargos/intereses, devoluciones, lotes parciales y resolución explícita de coincidencias ambiguas o ausentes.
- Liberación parcial, búsqueda/historial ampliados, navegación de cuentas retiradas, escalamiento y presupuesto de consultas de historias extensas.
- Restricciones/roles SQL, custodia independiente, retención, respaldos y revisión de logs/telemetría. Las pruebas del servicio no certifican ausencia forense del CSV en toda una infraestructura.
- Integrar únicamente evidencias calificadas a aplicaciones de anticipos u otras decisiones financieras; una confirmación declarada no autoriza un pago ni sustituye la revisión profesional.

Los otros paquetes del plan también conservan desarrollo local y validaciones externas pendientes. No se presenta el 50 % como aceptación bancaria ni como cierre de los 20 hitos.

Resultados y evidencias consolidados en [implementacion-54.json](evidencias/implementacion-54.json). Sin commits, push, cambios en main, pagos ni solicitudes bancarias reales.

## Verificación final

- **378 pruebas Python aprobadas**, incluidas 23 de conciliación/liberación y 2 nuevas de integración HTTP corporativa. Sin omisiones.
- **43 escenarios contables PostgreSQL aprobados** y restauración local. Los cuatro nuevos verifican revisión concurrente, confirmación/reintento, liberación/reintento y dos extractos intentando adquirir la misma línea.
- **195 comprobaciones Chromium aprobadas**: 53 ERP, 30 corporativas, 52 de apertura/políticas, 28 de nómina y 32 de conciliación/liberación.
- TypeScript estricto de cuatro componentes sin errores; sin acreditar build Next completo.
- Suite final con fuentes estables en `/tmp/sgacd-bank-54-final`; reporte y hashes en evidencia54. Los resultados son de entornos aislados con datos sintéticos, no aceptación productiva.
