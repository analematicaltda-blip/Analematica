# Implementación 57 · Registro ambiental revisado y recuperación

**Avance global: 52,78 % (38/72), sin crédito duplicado de ACC-018.** H16 continúa en ejecución. El plan conserva 4 paquetes verificados localmente, 9 en ejecución y 7 pendientes; aceptación completa 0/24. No se declara subsanado el conjunto de 20 hitos.

## Problema resuelto

La estimación anterior no conservaba historial confirmado ni impedía volver a registrar una actividad en otra solicitud. Ahora ERP y Analemática permiten revisar la medición, persistir esa revisión y confirmarla mediante una segunda autorización del mismo titular. El resultado puede recuperarse por el identificador de revisión ante recarga o resultado incierto, sin restaurar casillas de autorización.

Se conserva el cálculo exacto junto con actividades, factores, versiones, vigencias, geografías, fronteras, huellas de sus fuentes y huella declarada del soporte de la actividad. El registro confirmado contiene la revisión originaria, fecha de conocimiento registrada por la aplicación y huella de consistencia. Las vistas de recuperación recalculan el resultado y contrastan revisión, confirmación, versiones de factores y reservas de actividades.

La segunda confirmación no vuelve a interpretar campos editables: utiliza la revisión persistida y verifica que pertenece al titular actual. Cambiar entradas o identificador de recuperación retira el resultado y las autorizaciones de la interfaz. Recuperar una revisión individual repone sus campos desde el snapshot, muestra factor y actividad y exige confirmar nuevamente; recuperar una observación confirmada conserva su historial y no habilita otra confirmación.

## Versiones, duplicados y atomicidad

Cada actividad usa un identificador único dentro de la empresa. Una vez confirmada, otra revisión no puede apropiarse de ese identificador, aunque cambie cantidad o soporte. Los factores se identifican por código y versión: reutilizar la misma versión con otra tasa, fuente o geografía se rechaza. Una versión nueva puede utilizarse en actividades nuevas y conserva la evidencia anterior.

Los escritores del servicio se serializan mediante bloqueo de empresa. Factores, reservas de actividades y confirmación se registran dentro de una transacción. Si alguna actividad entra en conflicto o falla el sellado final, no quedan reservas parciales. Los reintentos de la misma revisión recuperan la observación original. Una actividad futura puede estimarse, pero no registrarse como hecho observado.

Las claves deterministas usan la PK del outbox; esto no equivale a restricciones semánticas SQL independientes para escritores que eludan el servicio. Las huellas tampoco son WORM, firmas independientes o defensa contra modificación privilegiada coordinada de toda la evidencia.

## Integración y alcance

Las rutas siguen exigiendo empresa verificada, titular personal activo y respuestas privadas/no-store. El puente corporativo conserva origen fijo, doble sesión, CSRF, operaciones explícitas y comprobación de empresa/fuentes/resultado. No se envían documentos originales ni llaves: se persisten códigos, cantidades, factores y huellas declaradas, que siguen siendo información privada de la empresa.

El registro ambiental no escribe asientos, no reconoce pasivos ni compensaciones, no emite créditos de carbono y no realiza pagos. La confirmación certifica la declaración del titular, no autenticidad científica o legal. No se presenta como un nuevo cálculo tributario.

API: hasta 30 actividades y 10 factores en el contrato acotado existente. Formulario: una actividad/factor por revisión. Los lotes creados mediante API se pueden consultar, pero su confirmación por recuperación en la interfaz se limita a revisiones individuales. No hay buscador o paginación de todo el historial: la recuperación usa un UUID conocido.

## Pendientes que siguen abiertos

- Incorporar fuentes legítimas y soportes en almacenamiento soberano, validación profesional y factores cualificados.
- Integrar identificadores operativos auténticos. La exclusión actual evita repetir el mismo código; no detecta al operador que asigna otro código al mismo viaje.
- Desarrollar corrección/contrapartida ambiental revisada para mediciones erróneas, conservando la historia. Los registros actuales no se editan ni liberan.
- Añadir búsqueda histórica, cortes explícitos y exportación, incertidumbre y reglas de agregación profesionalmente revisadas.
- Cualificar restricciones/roles SQL, custodia, retención y restauración de todo el conjunto de pruebas; los timestamps de la aplicación no son tiempo certificado.
- Completar valoración de obligaciones reales y reportes ESG cuando proceda, con aprobaciones propias; ninguna estimación se convierte automáticamente en pasivo.

Resultados de pruebas y capturas: [evidencia 57](evidencias/implementacion-57.json). No se hicieron commits, push, actualizaciones de main, despliegues, pagos ni solicitudes bancarias/DIAN reales.

## Verificación final ejecutada

- **437 pruebas Python aprobadas**, incluidas 16 nuevas del registro ambiental y una nueva integración HTTP corporativa.
- **48 escenarios PostgreSQL aprobados** y ensayo de restauración local. Los tres nuevos verifican una sola observación ante reintento simultáneo, exclusión de actividad entre dos revisiones y rechazo de una versión de factor competidora con contenido diferente.
- **253 comprobaciones Chromium aprobadas**: 50 ERP, 27 corporativas, 52 apertura/políticas, 28 nómina, 32 conciliación, 32 hoteleras y 32 ambientales.
- TypeScript estricto de cuatro componentes sin errores. No se acredita build Next completo.
- Fuentes estables en `/tmp/sgacd-environmental-57-final`; las huellas de evidencias se verificaron. Esta comprobación no constituye firma ni aprobación de producción.
