# Implementación 24 · Interfaz de diagnóstico de conciliación

**Avance: 27,78 % (20/72 hitos).** Amplía los incrementos ya acreditados; no cierra la conciliación de datos reales.

La consulta contable ERP incorpora un panel de diagnóstico solicitado manualmente. Muestra conteos de asientos/versiones previas, cuentas con saldo inicial pendiente y hallazgos por asiento/fecha económica. Identifica las cuentas de la muestra sin divulgar sus importes; avisa si esa muestra está truncada. Los códigos se explican en lenguaje de revisión contable, con el código técnico disponible para trazabilidad.

Consulta diez asientos por página, permite volver al inicio o seguir el cursor y declara que las páginas no comparten una instantánea estable. Una página sin hallazgos no se presenta como libro certificado. No ofrece botones para reparar, rehashar o borrar saldos.

La interfaz valida forma y alcance de la respuesta, incluidas las marcas de solo lectura, ausencia de reparación y falta de certificación global. Rechaza respuestas incompatibles en lugar de mostrar conclusiones. Cambiar identidad/empresa oculta el diagnóstico y cancela solicitudes pendientes. Conserva azul metálico, acentos celestes y texto blanco; tablas contenidas y ajuste de identificadores largos en móvil.

Se corrigió una clave React duplicada entre componentes hermanos que la primera prueba detectó por duplicación de un formulario. Se añadió un espacio de claves propio para el nuevo panel y se repitieron los recorridos.

## Verificación

- 24 comprobaciones integradas de Chromium → sesión/CSRF Django → ORM aislado: consulta limpia de dos asientos, alcance visible y ocultamiento al cambiar empresa, junto con regresiones anteriores.
- 15 comprobaciones de contrato UI con respuestas controladas: incluye hallazgo de hash, cuentas de apertura, página posterior, rechazo de respuesta que indica reparaciones, cierre de sesión y vista móvil sin desbordamiento con cuenta pendiente visible. Estas comprobaciones no son integración con datos reales.
- 119 métodos Python contables aprobados; tipado TypeScript estricto de la ruta y sus imports sin errores.
- Evidencia local y hashes: `evidencias/implementacion-24.json`.

No hay cambios backend, esquema o bloqueos en este corte; no se repitió PostgreSQL. Las pruebas son locales y sintéticas, no una certificación de libros del usuario ni una compilación completa del proyecto Next.

Pendientes: snapshot estable del recorrido, interfaz corporativa contable Analemática y su identidad verificada, revisión de empresas inactivas, conciliación profesional con soportes y ajustes aprobados, accesibilidad integral, fallos de red/carga y compilación completa heredada. Continúan los demás pools. Sin cambios de bases del usuario, commit o push.
