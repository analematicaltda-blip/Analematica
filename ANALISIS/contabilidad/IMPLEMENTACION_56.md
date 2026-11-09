# Implementación 56 · Medición ambiental sin pasivos automáticos

H16 pasa de pendiente a ejecución. El incremento funcional y su verificación de ACC-018 se incorporan al registro estable, manteniendo su aceptación completa abierta. **Avance: 52,78 % (38/72); aceptación completa 0/24.** Los paquetes del plan quedan en 4 verificados localmente, 9 en ejecución y 7 pendientes. Los 20 hitos todavía no están completados.

## Funcionalidad disponible en ambos sistemas

El panel contable de ERP y Analemática incorpora «Estimación ambiental trazable». El titular indica actividad, fecha, cantidad, unidad, factor, versión, vigencia, geografía, límite del sistema y huella de fuente. No se suministran factores reales predeterminados ni se consultan fuentes externas. El formulario utiliza la identidad azul/azul claro/blanco y funciona en móvil.

El motor compartido usa Decimal, admite vehículo-km, pasajero-km, litros de combustible y kWh, y exige correspondencia exacta de unidad y vigencia. Rechaza identidades duplicadas, factores ausentes o sin usar, cantidades negativas, floats, notación exponencial, valores no finitos y contratos con campos inesperados. El reparto por pasajero solo se permite para vehículo-km con un número entero positivo; no se vuelve a multiplicar una cantidad ya expresada en pasajero-km.

Cada partida conserva factor, versión, fuente y producto exacto. El total se redondea a seis decimales después de sumar, evitando perder emisiones pequeñas por redondear cada fila. Los límites de combustión directa, electricidad por ubicación y ciclo de vida se mantienen separados; mezclarlos retira el total combinado. Una huella reproducible vincula empresa y entradas ordenadas. **No es una firma, acreditación de procedencia ni prueba de autenticidad del factor.**

La API permite hasta 30 actividades y 10 factores, con cantidades/factores de hasta 1.000.000.000 y seis decimales. El parser contable limita a 8 KiB el contrato HTTP. El formulario presenta una actividad/factor por consulta. Las consultas posteriores reemplazan el resultado; modificar campos o perder la identidad lo retira. La estimación no persiste documentos ni factores y no se presenta como inventario ambiental histórico.

## Integración y controles

El endpoint ERP exige la identidad empresarial verificada y devuelve una respuesta privada/no-store. Analemática reutiliza el puente de origen fijo, doble sesión y CSRF. El puente valida empresa, entradas devueltas, esquema, digest y banderas de lectura. No admite sobrescribir empresa u origen desde el cuerpo.

La estimación no escribe en el ledger, no transfiere dinero, no reconoce pasivos, no emite créditos de carbono y no certifica ESG. Por ser una consulta sin efectos persistentes, no introduce confirmaciones financieras ficticias. Cualquier reconocimiento contable posterior requerirá obligación real, política revisada, cuentas, autorizaciones y evidencia propias.

## Verificación

Las pruebas del nuevo servicio incluyen total y reparto exactos, vigencias/unidades incompatibles, límites, duplicados, precisión acumulada, huella por empresa y versión, entradas sin mutación y rechazo de empresa ajena en el endpoint. Una prueba HTTP contrasta el mismo resultado de ambas APIs y rechaza unidades incompatibles.

El navegador recorre ambos paneles con factores sintéticos explícitos: ausencia de valor predeterminado, total 12,345600 kg CO2e, reparto 3,086400, edición, cero explícito, libro sin cambios, vista móvil y limpieza al perder identidad. El código TypeScript de cuatro componentes pasa verificación estricta aislada; esto no acredita compilación Next completa.

**420 pruebas Python aprobadas** en la regresión contable final, con fuentes estables. Incluyen 16 pruebas nuevas del motor/API y una integración HTTP nueva. La regresión de navegador y las pruebas ambientales suman **239 comprobaciones aprobadas**: 50 ERP, 27 corporativas, 52 apertura/políticas, 28 nómina, 32 conciliación, 32 hoteleras y 18 ambientales. No se repitieron escenarios PostgreSQL en esta entrega: las nuevas rutas son de lectura, sin esquema ni persistencia nuevos; los 45 escenarios de la entrega55 son evidencia histórica, no una nueva ejecución.

Resultados finales, hashes y capturas: [evidencia 56](evidencias/implementacion-56.json).

## Pendientes de H16 y ACC-019 ambiental

- Registro persistente versionado y revisado de factores y mediciones, con custodia soberana de soportes y recuperación. La huella declarada no sustituye ese soporte.
- Validar fuentes legítimas, territorio, tecnología/combustible, gases incluidos, potenciales de calentamiento, unidades y fronteras con profesionales. «kg CO2e» no asegura por sí solo comparabilidad metodológica.
- Integrar rutas, consumo y ocupación reales, atribución por servicio y mecanismos contra duplicidad de actividades entre consultas; la exclusión actual de duplicados se limita a una solicitud.
- Modelar incertidumbre, factores compuestos y emisiones indirectas, sin sumar dos veces combustión y ciclo de vida. No se declaran créditos retirados ni compensación efectiva.
- Separar la medición ambiental de una eventual obligación contable y su valoración monetaria. No existe causación automática por vender un servicio.
- Completar reportes GRI/SASB aplicables, trazabilidad y revisión independiente antes de afirmar cumplimiento ESG. ACC-019 sigue pendiente.

No se hicieron commits, push, cambios en main, despliegues, pagos ni solicitudes a DIAN o bancos. Continúan desarrollos locales y cualificaciones externas de otros hitos; este incremento no cierra el plan.
