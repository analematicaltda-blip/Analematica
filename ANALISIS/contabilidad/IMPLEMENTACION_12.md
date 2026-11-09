# Implementación 12 · Backtesting temporal sin información futura

**Avance: 25,00 % (18/72 hitos).** Se amplía ACC-017, ya puntuado por incremento y pruebas. No se acredita aceptación completa.

El motor compartido incorpora `backtest`: recibe un escenario de entrenamiento y, por separado, exactamente 365 resultados diarios posteriores. Valida orden, continuidad, fechas e importes; los resultados deben empezar al día siguiente del entrenamiento. Rechaza solapamientos, huecos, duplicados y campos adicionales. Los datos posteriores nunca se usan para construir la simulación ni para seleccionar su semilla.

Para cada horizonte 30/90/365 devuelve caja observada, mediana simulada, error observado menos predicho, error absoluto, inclusión en el intervalo empírico p05–p95 y si la trayectoria observada entró en déficit. Resume el error absoluto medio de los tres horizontes, que son correlacionados. Mantiene separados el digest de los supuestos de entrenamiento y el digest de los resultados posteriores.

Endpoint ERP: `POST /api/v1/mi-negocio/contable/contabilidad/cuentas/backtest-caja/?provider_id=<UUID>`. Cuerpo: `scenario` (el contrato existente del simulador) y `actuals` (365 objetos con `date` y `net_cash_flow`). Usa la identidad y moneda empresariales verificadas, sin escribir asientos, persistir proyecciones ni ejecutar movimientos financieros.

## Verificación

88 métodos Python aprobados en el perfil contable. Casos nuevos: serie constante con error cero; cambio de resultados futuros sin alterar la simulación; signo/magnitud del error; déficit observado; ausencia de cobertura del intervalo; rechazo de fechas incompatibles, series incompletas y floats. La API prueba titularidad y ausencia de nuevos asientos. Evidencia: `evidencias/implementacion-12.json`; hashes locales comprobados.

## Límites

Es un único holdout cronológico declarado por el operador, no una fuente bancaria contrastada ni múltiples ventanas de validación. La inclusión de un resultado en el intervalo no acredita cobertura estadística calibrada ni precisión predictiva. La validación con series reales, sensibilidad, interfaz, procedencia de datos, análisis estacional y rendimiento sigue pendiente. No cierra ACC-017, la integración corporativa contable de Analemática ni los demás pools.

Sin migraciones, datos del usuario, credenciales externas, commits o push.
