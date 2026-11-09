# Implementación 72 · Compras persistentes operables desde ambos paneles

Se conectó el motor tributario a los modelos reales de proveedores y facturas de compra. Ahora es posible capturar metadatos, revisar recepción y desglose, dar una segunda confirmación, contabilizar una sola vez y recuperar/ajustar el asiento desde ERP y Analemática. Las capturas por sí solas no contabilizan ni pagan.

## Hallazgos subsanados

- Señal de alta rota: usaba un atributo inexistente y cuentas elegidas implícitamente. Se retiró la contabilización automática y se mantiene la vía explícita revisada.
- Catálogo de cuentas inadecuado: el de ventas excluía gastos. Se añadió un catálogo propio de compras sin ampliar el de ventas.
- Fuente manual desconectada: la revisión ahora verifica proveedor, factura, importes, fechas y estado persistidos. Los cambios entre confirmaciones impiden avanzar.
- Posible elusión por otra ruta: se reservan documento y huella, y las rutas genéricas exigen el adaptador nativo para esas fuentes. Los permisos internos no se reciben del cliente.
- Falta de interfaz: formularios compartidos para ambos paneles, huellas locales sin subir soportes, dos confirmaciones, recuperación tras recarga y contrapartida. Se conserva la identidad visual.

## Verificación

35 casos nuevos de ORM/API nativa y6 del contrato corporativo; dos recorridos HTTP nuevos. El navegador completa captura, revisión, posteo, recarga, recuperación y contrapartida en ambas versiones. **724 pruebas Python aprobadas en 42 suites**, sin omisiones, incluidas58 de la suite corporativa; **107 comprobaciones Chromium** (26 del flujo nuevo y81 de regresión). Tipos estrictos aprobados y medición de100 documentos ligada al mismo manifiesto de fuentes. Máximos ORM: revisión16.235ms, posteo139.005ms, recuperación14.042ms y consulta166.293ms; sin precisión IA evaluada ni SLA productiva.

[Operación y contratos](OPERACION_COMPRAS_NATIVAS.md) · [Evidencia72](evidencias/implementacion-72.json).

## Alcance pendiente y porcentaje

La interfaz cubre un concepto; faltan formularios multicomponente, conciliación histórica, modificaciones controladas de capturas, devoluciones parciales, responsabilidades fiscales completas, cualificación PostgreSQL y revisión profesional/productiva. Las rutas heredadas y pagos permanecen deshabilitados. No se acredita autenticidad por una huella ni recepción física por una declaración.

**63,89 % (46/72), aceptación completa0/24.** Se amplían ACC-008/ACC-014 ya acreditadas, sin créditos duplicados. Los20 hitos aún no están cerrados; este reporte no sustituye sus criterios de aceptación.

Sin commits, push, despliegue, datos reales, pagos ni envíos DIAN. Todo queda en el árbol de trabajo existente y en ANALISIS/.

Capturas móviles: [ERP](evidencias/implementacion-72-erp.png) · [Analemática](evidencias/implementacion-72-corporate.png).
