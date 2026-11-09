# Implementación 48 · Escritura corporativa, conciliación tributaria y bloqueo de aceptación DIAN ficticia

**Avance global: 41,67 % (30/72 hitos), frente al 38,89 % anterior (28/72).** Incremento de 2,78 puntos porcentuales sin cambiar tareas ni ponderaciones. Producción no habilitada; aceptación completa 0/24.

## Resultado funcional

**Analemática escribe en el libro mayor compartido.** Su consola carga reservas/cuentas de la empresa fijada por el vínculo, persiste la revisión de prestación y contabiliza solo después de una segunda confirmación. Permite anticipos simples según el flujo revisado y registra contrapartidas mediante otras dos confirmaciones. Los reportes se actualizan desde el ledger: no existe un saldo corporativo paralelo.

Verificación real entre servicios: navegador → FastAPI/SQLAlchemy → HTTP/cookie/CSRF → Django → motor contable. En la prueba aislada, el resultado pasa de 10 a 110 COP después del reconocimiento de 100 y vuelve a 10 después de la contrapartida. El reintento devuelve el mismo asiento. No se transfirió dinero.

**Conciliación tributaria operativa en ERP y Analemática.** Se elige una cuenta de pasivo revisada y un intervalo de hasta 366 días. El reporte usa movimientos contabilizados, contrasta las fuentes de reconocimiento/revisión y sus hashes, distingue contrapartidas y separa movimientos no atribuibles. Caso comprobado: impuesto de reserva 15,97 COP más movimiento previo no atribuible de 5 COP; no oculta este último. Una contrapartida compensa el impuesto conservando el original. Cuenta/empresa ajenas, fuente alterada, valoración incompatible o más de 2.000 movimientos bloquean el reporte.

Esto es conciliación interna de lo registrado, no determinación normativa de IVA/retenciones, declaración ni cruce con DIAN. No se interpreta cualquier pasivo como impuesto por su código: el propietario selecciona la cuenta y debe validar su clasificación.

**DIAN deja de aprobar documentos ficticios.** Se encontraron dos servicios legados que simulaban éxito, una firma que era solo un SHA-256 y un CUFE calculado con datos incompletos/PIN fijo. Se conservaron sus puntos de entrada como fronteras que rechazan antes de mutar facturas, numeración, certificados o logs. El trigger legado ya no crea una factura/envía correo por esa ruta y el endpoint PDF deja de entregar un archivo ficticio. No se modifica la historia de documentos existentes automáticamente.

El diagnóstico privado por empresa comprueba la forma/vigencia/rango de una configuración pública de habilitación. Siempre distingue los controles que aún faltan: custodia del cliente, UBL/XAdES cualificados, transporte y validación auténtica del acuse. Una configuración válida no activa envíos, no retorna secretos y nunca equivale a aceptación. Véase `DIAN_HABILITACION.md`.

**Recibos aplicados protegidos en el motor común.** Cualquier llamada a `LedgerEngine.reverse_entry`, desde cualquiera de los sistemas, rechaza revertir un recibo con un reconocimiento vigente. Después de la contrapartida del reconocimiento puede revertirse el recibo. Ambas operaciones comparten el bloqueo por empresa con la aplicación del anticipo. No se acredita protección frente a un administrador que altere eventos o evada servicios mediante SQL.

## Seguridad del puente corporativo

- Dueño SQL, vínculo con revisión independiente, sesión ERP/actor/empresa coincidentes y MFA de sesión existente.
- Lista fija de consultas y comandos. El cliente no selecciona Tenant, provider, URL, actor o cabeceras ERP.
- JSON de 8 KiB, profundidad acotada, sin claves duplicadas ni constantes no finitas; confirmación booleana explícita.
- CSRF obtenido únicamente del origen ERP configurado, sin retransmitir el JWT corporativo. Origen HTTPS o loopback de pruebas, verificación TLS y sin redirecciones.
- Vínculo/rol revalidados en una sesión SQL independiente inmediatamente antes del despacho. La revocación antes de ese punto bloquea la operación.
- No se promete una transacción distribuida entre SQLAlchemy y Django. Una revocación posterior al despacho no cancela un asiento ya autorizado. Timeout/resultado incompatible queda incierto: se consulta/reintenta la misma revisión persistida, sin crear otra ni declarar que no hubo escritura.
- Respuestas privadas/no-store; errores ERP no exponen su contenido. La interfaz descarta aprobaciones al editar y limpia el contexto al salir/ocultarse.

## Avance y pendientes

Se acredita el primer incremento ejecutable y su verificación de **ACC-014**: conciliación interna de impuestos registrados. La aceptación completa sigue pendiente de reglas normativas/versionadas, retenciones, documentos/acuse oficiales y contraste fiscal autorizado. No se acredita ACC-009 por sustituir simulaciones o añadir un diagnóstico: XML, representación y firma cualificados siguen pendientes.

El denominador permanece en 72 hitos/24 tareas. El reporte generado en `PROGRESO.md` incluye porcentajes por frente sin duplicar tareas y `BLOQUEOS_POR_TAREA.md` detalla lo que falta. El corte anterior de 38,89 % se conserva en la implementación 47.

La evidencia final y el alcance exacto de cada prueba se registran en `evidencias/implementacion-48.json`. No se realizaron commits, despliegues ni acciones sobre cuentas reales.

## Pruebas y reportes entregados

- 262 pruebas Python aprobadas en el perfil contable completo, con las fuentes estables durante la corrida. Incluye seis pruebas HTTP de los dos backends corporativo/ERP y los contratos del puente.
- PostgreSQL real: posteo concurrente, aplicación única, bloqueo de reversión del recibo aplicado, atribución/contrapartida tributaria, integridad y recuperación. Todo sobre bases desechables.
- 22 comprobaciones del navegador corporativo: lectura, revisión, doble autorización, escritura, contrapartida, conciliación tributaria, sesión y móvil.
- 47 comprobaciones del navegador ERP: flujos previos y nuevo panel tributario/DIAN; edición descarta resultados y la vista móvil conserva texto blanco y desplazamiento horizontal de la tabla.
- TypeScript estricto de los dos componentes modificados sin errores; no sustituye la compilación Next completa, que sigue pendiente de las dependencias del proyecto.
- 14 pruebas del runner y siete del registro de avance aprobadas. Los frentes particionan las mismas 24 tareas/72 hitos y no duplican créditos.

Después de la corrida backend se corrigió únicamente el contraste/tabla móvil y su comprobación de navegador en dos archivos FRONTEND, que volvieron a verificarse mediante TypeScript y recorrido real. Las fuentes backend permanecieron sin cambios; esta diferencia queda explícita en la evidencia. Los hashes del artefacto de la corrida son verificables, no una firma independiente ni aceptación productiva.

Reportes actualizados: `PROGRESO.md`, `progreso.json`, `BLOQUEOS_POR_TAREA.md`, matriz CSV y pendientes de producción. Capturas de la sesión: `/tmp/sgacd-corporate-writing-48.png` y `/tmp/sgacd-erp-tax-final-48.png`.
