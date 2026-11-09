# Implementación 16 · Validación de múltiples ventanas temporales

**Avance: 25,00 % (18/72 hitos).** Se amplía ACC-017 sin acreditar todavía su aceptación completa.

El motor compartido incorpora `backtest_windows` para dos a cuatro ventanas declaradas, cada una con entrenamiento y 365 días posteriores separados. Exige orígenes de pronóstico distintos y estrictamente crecientes. Dentro de cada ventana siguen vigentes las validaciones de continuidad, importes y ausencia de solapamiento entre su entrenamiento y sus resultados.

El informe conserva cada evaluación e incorpora, por horizonte 30/90/365, error absoluto medio y cantidad/fracción de ventanas cuyo resultado quedó dentro de p05–p95. Declara si los periodos posteriores de distintas ventanas se solapan. No trata esos periodos ni sus horizontes correlacionados como muestras independientes o cobertura estadística calibrada. Una ventana posterior puede entrenarse con información ya disponible entonces, aunque hubiera sido resultado posterior de una ventana anterior.

API ERP: `POST /api/v1/mi-negocio/contable/contabilidad/cuentas/backtest-ventanas-caja/?provider_id=<UUID>`. Cuerpo: `windows`, lista de dos a cuatro contratos `{scenario, actuals}` del backtesting existente. Cada escenario conserva sus parámetros explícitos; no se ajustan semillas ni se escogen automáticamente las mejores ventanas. Se reutiliza autenticación/titularidad empresarial y moneda del servidor. Sin persistencia de simulaciones, asientos o pagos.

## Evidencia

98 métodos Python aprobados. Incluyen agregado de errores con resultado analítico conocido, declaración de solapamiento, ventanas disjuntas, reproducibilidad, rechazo de ventanas duplicadas/desordenadas y límites, invariancia de todas las simulaciones al cambiar resultados posteriores, API empresarial y ausencia de nuevos asientos. Ver `evidencias/implementacion-16.json` y hashes locales verificados.

No se modificaron esquema, bloqueos ni interfaz; no se repitieron PostgreSQL o navegador en este corte. No se usan bases ni datos del usuario.

## Pendientes

Interfaz para varias ventanas, fuentes y series reales contrastadas, revisión profesional, calibración y medición de carga/rendimiento. Las dos a cuatro ventanas declaradas no bastan para acreditar precisión productiva. Continúan integración corporativa contable de Analemática y demás pools. Sin migraciones, publicación, commit o push.
