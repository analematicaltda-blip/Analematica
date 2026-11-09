# Implementación 08 · Revisión de clasificación desde el ERP

**Avance verificable: 22,22 % (16/72 hitos).** Se conserva la base de 24 tareas. Este formulario amplía ACC-016, que ya tenía incremento y pruebas; no acredita todavía su aceptación completa y no suma puntos artificiales.

## Funcionalidad

La consulta contable del ERP incorpora un formulario de clasificación de liquidez. Carga la política vigente y el catálogo autorizado, recorre paginación del mismo catálogo y empresa con límites explícitos y rechaza catálogos incompletos, repetidos, enlaces externos y cuentas seleccionadas ausentes o inactivas. No infiere cuentas a partir de nombres.

El titular selecciona cuatro grupos, aporta el SHA-256 de la evidencia revisada, examina un resumen y confirma que revisó cuentas, cobertura y evidencia. El guardado usa la sesión y el CSRF existentes, así como la revisión esperada del backend. No modifica políticas anteriores ni permite introducir saldos o identidades contables desde el navegador.

Se impiden duplicados entre grupos y se exigen cuentas de activo y pasivo. El backend vuelve a comprobar las reglas y la titularidad. Ante error, conflicto o respuesta no confirmada no se reintenta automáticamente: se exige recarga y nueva revisión. Después del guardado se actualizan los indicadores y se bloquea otro guardado hasta recargar.

Cambiar empresa o identidad oculta inmediatamente la configuración anterior; las respuestas tardías de otro contexto no rellenan el contexto actual. El formulario conserva azul metálico, acentos celestes, texto blanco y etiquetas accesibles. Esta revisión configura un informe: no sustituye las autorizaciones financieras y no ejecuta pagos ni asientos.

## Evidencia

- 13 comprobaciones del recorrido Chromium → sesión/CSRF real Django → ORM aislado: incluye duplicados, resumen y confirmación, actualización concurrente que invalida la revisión cargada, recarga, nueva revisión y actualización de indicadores.
- La clasificación no altera importes del ledger: la prueba confirma débitos y créditos de 15,00 antes de cerrar el recorrido con los mismos asientos sintéticos de partida.
- 11 comprobaciones de regresión de la interfaz de consulta con respuestas controladas.
- Tipado estricto sin errores de la ruta y sus imports, incluido el formulario.
- 68 métodos contables aprobados; verificación local de hashes de evidencia. No se repitieron carreras PostgreSQL porque este corte no modifica su código backend ni esquema.
- Registro de progreso y documento canónico de pendientes de billetera comprobados.

Detalle: `evidencias/implementacion-08.json`. Las identidades y datos son sintéticos y aislados; no acreditan cobertura contable real ni una instalación productiva.

## Pendientes

Integración contable autenticada de la consola de Analemática, políticas por vigencia, revisión profesional de cobertura/evidencia, interfaz de historial completo, accesibilidad y uso móvil integral del formulario, recuperación ante fallos de red y pruebas de cargas grandes. Continúan pendientes ratios operativos por habitación/paquete y los demás pools. Sin cambios de base de datos, commits o push.
