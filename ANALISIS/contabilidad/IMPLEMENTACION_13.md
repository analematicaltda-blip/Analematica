# Implementación 13 · Sensibilidad de escenarios de caja

**Avance: 25,00 % (18/72 hitos).** Se amplía ACC-017 sin acreditar aún su alcance completo.

El motor compartido incorpora `sensitivity`: compara una base con uno a cuatro escenarios nombrados, con cambios explícitos en caja inicial y flujo neto diario. Usa la misma semilla, número de trayectorias, fechas y remuestreo en cada escenario. De este modo el diferencial se debe al cambio declarado y no a distintos sorteos aleatorios.

Los ajustes se expresan en importes exactos, admiten signo y pasan nuevamente las reglas del simulador. No se aceptan nombres vacíos/duplicados, trabajo sin límites, floats ni escenarios con caja inicial negativa o importes fuera de rango. Los datos originales no se modifican. El resultado muestra cada simulación, diferencia de la mediana de caja y cambio en frecuencia de trayectorias deficitarias para 30/90/365 días.

Endpoint ERP: `POST /api/v1/mi-negocio/contable/contabilidad/cuentas/sensibilidad-caja/?provider_id=<UUID>`. Cuerpo: `scenario` (contrato existente) y `shocks`, lista de objetos `name`, `opening_cash_delta`, `daily_net_flow_delta`. Reutiliza autenticación/autorización empresarial; empresa y moneda se derivan del servidor. No escribe asientos ni ejecuta pagos.

## Evidencia

93 métodos Python aprobados. Casos nuevos: diferencial exacto por horizonte; series variables con remuestreo común; reproducibilidad y ausencia de mutación; cambio nulo idéntico a la base; límites, nombres duplicados, importes inválidos y caja negativa; aislamiento API y ausencia de nuevos asientos. Ver `evidencias/implementacion-13.json`. Hashes de evidencia local comprobados; no se repitieron pruebas PostgreSQL al no modificar esquema ni bloqueos.

## Límites

Los ajustes son aditivos y declarados: no constituyen elasticidades estimadas, reglas fiscales, efectos macroeconómicos calibrados ni recomendaciones de inversión. La frecuencia de déficit no es una probabilidad certificada. Faltan interfaz, múltiples ventanas de backtesting, datos reales/procedencia, modelo estacional y cualificación profesional/rendimiento. También sigue pendiente la integración de la consola corporativa Analemática y los restantes pools. No se modifican datos del usuario, migraciones ni servicios productivos; sin commit ni push.
