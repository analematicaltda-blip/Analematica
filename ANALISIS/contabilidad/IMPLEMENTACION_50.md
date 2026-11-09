# Implementación 50 · Ejecución del plan de subsanación

**Avance global: 44,44 % (32/72 hitos), frente a 41,67 % (30/72).** Se acredita un incremento funcional verificado de ACC-015 (comparación neutral de extractos con el ledger). Las mejoras de recuperación/paginación/snapshots/asistente refuerzan tareas ya acreditadas y no duplican puntos. Alcance completo aceptado: 0/24; producción no habilitada.

**No están subsanados los 20 paquetes.** Hay cuatro verificados localmente (H01–H04), tres en ejecución con alcance parcial (H14, H17, H20) y trece pendientes. Los estados y criterios originales se conservan en PLAN_SUBSANACION_20_HITOS.md y plan-subsanacion-20.json; los pendientes incluyen desarrollo local y validaciones externas, no solamente credenciales.

## H02 · Recuperación después de perder una respuesta

ERP expone estado de la reserva, última revisión y su historial, asiento y contrapartida comprobados contra recibo/origen/hashes. El puente corporativo usa únicamente la empresa/actor enlazados y la sesión ERP correspondiente. Falta de prueba de origen o vínculo revocado bloquean acceso; el servicio no reconstruye evidencia ausente.

La prueba provoca una pérdida HTTP después de que el ERP confirmó el asiento. Analemática recibe resultado incierto, consulta el estado persistido y obtiene el mismo journal; reintentar devuelve replay sin duplicarlo. Ambos paneles recuperan la revisión; la segunda autorización queda desmarcada. La consola corporativa conserva el estado del asiento/contrapartida al cambiar de selección y bloquea otra contrapartida tras revertir. No hay atomicidad distribuida entre SQLAlchemy y Django.

## H03 · Catálogos grandes e historial

El catálogo ofrece paginación explícita de100 cuentas por UUID, búsqueda acotada y empresa/chart/tipo/actividad verificados. El modo legado conserva su contrato y rechaza un resultado excesivo. Ambos paneles cargan más páginas de cuentas y reservas, buscan cuentas fuera de la primera página, evitan duplicados y recuperan revisiones. El historial pagina20 versiones; se probaron25 revisiones conservando el orden y todas las versiones.

La revisión de liquidez ahora solicita100 cuentas por página, manteniendo su límite de2000: el anterior límite de20 páginas de10 cuentas hacía fallar catálogos válidos por encima de200. El panel tributario también usa paginación explícita. Los recorridos Chromium verifican más de500 cuentas y20 reservas en ambos sistemas. Una inserción concurrente anterior al cursor requiere recargar el listado: la paginación no promete un snapshot histórico de catálogo.

La búsqueda carga hasta100 coincidencias del servidor por consulta y filtra las cuentas ya cargadas; la navegación general permite seguir cargando el catálogo. Los UUID conservan el contexto y las cuentas ya seleccionadas no desaparecen al filtrar. Las páginas y parámetros permanecen restringidos al origen/empresa autorizados.

## H04 · Reportes coherentes

Balance de prueba, pérdidas/ganancias, balance general y rentabilidad usan la base principal y el bloqueo de empresa compartido con el posteo. Fechas de tipo incorrecto o intervalos inválidos, empresa inactiva y moneda base histórica incompatible se rechazan. El reporte entrega una referencia al último asiento observado; esa referencia no equivale a una publicación histórica inmutable ni a una firma independiente.

La carrera PostgreSQL hace coincidir un posteo con un balance. El resultado corresponde al estado anterior o posterior completo, con sumas iguales y watermark del mismo estado. No mezcla una lectura de réplica atrasada con el ledger actual. La cota de consultas del balance cambia de3 a8 consultas constantes para cubrir transacción, empresa, moneda y referencia; no se acredita una mejora de latencia ni la meta250ms.

El cambio de día UTC expuso una fecha de reconocimiento futura para Colombia: el formulario usa Bogotá y los fixtures HTTP reciben la fecha contable del ERP, en lugar de inferirla con date.today() UTC.

## H14 · Comparación bancaria parcial

Nuevo panel ERP compara un CSV neutral UTF-8 (máximo5000bytes/100 filas) con movimientos reales contabilizados de una cuenta explícitamente clasificada como efectivo/equivalente por el propietario. Requiere clasificación íntegra, cuenta/empresa activas, moneda COP, importes exactos y fechas válidas. No se aplica FX implícito.

Distingue candidato único, sin coincidencia, varios candidatos y una misma línea propuesta para varias transacciones. Un recibo revertido deja de ser candidato. Verifica hash de los asientos, limita candidatos y presenta referencias de fila en forma de digest; no devuelve identificadores bancarios originales. El archivo vive en memoria de cliente/solicitud, se descarta al salir/ocultar/cambiar contexto y no se persiste mediante este servicio. No se acredita borrado forense de memoria ni revisión independiente de todos los logs de infraestructura.

**Es una comparación de lectura, no una conciliación confirmada:** no autentica el origen bancario, no importa historial persistente ni crea cobros/pagos/asientos. Repetirla no cambia el ledger. Se verificó con ORM, API, panel real y PostgreSQL. Pendientes importación persistente/idempotente, revisión/confirmaciones de coincidencias, extractos legítimos, conexión bancaria y excepciones de moneda/fechas. H14 conserva su dependencia de conciliación de legados H05 para cualquier activación completa.

## H17 y H20 · Incrementos, sin cierre completo

El asistente corporativo consulta rentabilidad y cola comercial mediante el mismo servicio de lectura ERP, con sesión/empresa enlazadas, CSRF y parser acotado. Pruebas de inyección/empresa elegida por el cliente se rechazan y el ledger permanece igual. Editar la consulta borra la respuesta. Es un vocabulario determinista; no se afirma comprensión abierta, modelo privado evaluado, voz ni capacidad de ejecutar órdenes financieras.

Se ejecutó la regresión/recuperación local, pero H20 sigue abierto: faltan benchmark en hardware objetivo, precisión IA, roles y medios reales, RPO/RTO y el cierre de los otros paquetes. Las pruebas de fixtures no sustituyen aceptación profesional, fiscal, bancaria ni física.

## Verificación

- **286 pruebas Python** del perfil contable completo aprobadas.
- **34 escenarios contables PostgreSQL**, incluidos corte/posteo concurrentes y comparación bancaria; prueba global también conserva sus controles de recuperación.
- **30 comprobaciones Chromium corporativas** y **53 del ERP** aprobadas, con ambas APIs reales y bases aisladas.
- TypeScript estricto de ReservationRecognition, TaxReconciliation y BankComparison sin errores; no equivale a un build Next completo.
-14 pruebas del runner y7 del registro de avance aprobadas.

Las fuentes se mantuvieron estables durante la corrida backend. Después se ajustaron solo dos archivos frontend para conservar/bloquear el estado de contrapartida en la consola; ese recorrido volvió a verificarse en navegador. La evidencia registra esas diferencias y mantiene las fuentes backend sin cambios.

Evidencia: evidencias/implementacion-50.json. Capturas de sesión: /tmp/remediation-corporate-final-50.png y /tmp/remediation-erp-final-bank-50.png. Sin commits, publicación ni operaciones sobre cuentas reales.
