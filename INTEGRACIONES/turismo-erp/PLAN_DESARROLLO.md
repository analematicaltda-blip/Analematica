# Plan incremental de verificación, desarrollo y optimización

No se considera aprobada una reescritura. Cada ticket debe referenciar IDs de la matriz funcional, archivos/dependencias, pruebas antes/después y evidencia. Antes de cambios de dominio se presentan hallazgos y plan; el diseño detallado se revisa con el propietario.

| Orden | Prioridad | Trabajo | Criterio de aceptación / prueba |
|---|---|---|---|
| 1 | Crítica | Cerrar escrituras institucionales públicas y jurisdicción (H-001/H-002). | GET público permitido solo para datos publicables; POST/PATCH/DELETE anónimos rechazados; funcionario de municipio A no modifica B; creación tampoco permite falsificar territorio; excepciones delegadas auditadas. |
| 2 | Crítica | Reconciliar grafo de migraciones y entidades (H-006/H-015). | Plan de migración trazable sobre copia restaurada; grafo válido; sin `--fake`, borrados o recreación de tablas para aparentar éxito; conteos e invariantes antes/después. |
| 3 | Alta | Levantamiento institucional por los diez módulos. | Cada INS tiene recorrido, rol/jurisdicción, fuente de datos y evidencia; actualizar NO VERIFICADA solo con prueba suficiente. |
| 4 | Alta | Contrato de registro, contraste oficial y publicación comercial. | Una suscripción no valida RNT; retiro/vencimiento comercial conserva registro institucional; consentimiento y campos autorizados trazables; deduplicación/idempotencia. |
| 5 | Alta | Roles funcionales e identidad. | Usuarios A/B y empresas A/B aislados; no equivalencia automática por nombres; revocación/baja y cambio de permisos efectivos; pruebas de exportación/documentos. |
| 6 | Alta | Portal ERP: catálogo → cotización/reserva → checkout → comprobante. | Precio/moneda y disponibilidad del servidor; reserva sin sobreventa; pago sandbox verificable/idempotente; fallo de red no duplica cobro ni confirma sin pago válido; cancelación respeta política. |
| 7 | Alta | Contabilidad y finanzas pendientes. | Contratos y esquema revisados; asientos balanceados, periodos/control de cambios, reconciliación; DIAN y proveedores solo con credenciales de prueba autorizadas; dejar 503 mientras no cumpla. |
| 8 | Media | UX y operación sectorial. | Responsive 320/390/1440, teclado, errores/estados vacíos honestos; especialización para hotel/restaurante/agencia/guía/transporte sin duplicar identidades. |
| 9 | Media | Documental, tareas, importaciones y offline. | Archivo privado no público por URL; tipos/tamaño seguros; importación valida y deduplica; sincronización detecta conflictos sin sobrescribir aprobaciones. |
| 10 | Media | Analítica, micrositios, pauta y canales. | Indicadores conciliables y con fecha; no confundir simulación con ventas; plantillas y publicación revisadas; consentimiento y bajas efectivos. |
| 11 | Media | Telemetría/AiSOC y asistencia supervisada. | Eventos reales recibidos y verificables, claves/tenants separados; sin respuestas automáticas ni inferencia ficticia; acciones del motor con autorizaciones exigidas. |
| 12 | Baja | Optimización basada en medidas. | Medir latencias, consultas, caché y carga con línea base; demostrar mejora sin alterar saldos, permisos ni privacidad. |

## Paquetes de entrega

**Institucional primero:** entidades/usuarios/jurisdicción → directorios/atractivos/eventos/artesanos → planificación/documental → analítica/consolidación → portal público y accesibilidad. Si un proceso requiere aprobación multinivel, definir estados/transiciones y quién puede aprobar cada versión.

**ERP después, desde el cliente:** identidad e historial → catálogo/tarifa/disponibilidad → cotización/reserva → checkout/pago sandbox → documentos/cambios/cancelación → atención/PQR/reseñas/fidelización. Luego profundizar en los cinco módulos internos y la especialización por actividad.

**Interoperabilidad:** contrato versionado, consentimiento, mapping de IDs, procedencia y auditoría. Nunca integrar leyendo directamente tablas ajenas ni publicando toda la ficha empresarial por defecto.

## Puertas antes de producción

Backups/restauración, migraciones, autorización/jurisdicción, privacidad, pruebas de negocio, carga, compilaciones frontend productivas, conectores sandbox y monitoreo real. Los dispositivos físicos Android/iOS y Xcode/firma siguen siendo dependencias externas de la cualificación móvil. No se prometen seguridad absoluta, cumplimiento legal automático ni gratuidad de proveedores.
