# Implementación 11 · Simulador de caja reproducible

**Avance verificable: 25,00 % (18/72 hitos).** ACC-017 obtiene incremento funcional y verificación automatizada. No obtiene aceptación completa: sensibilidad, backtesting y cualificación con datos reales siguen pendientes. La base permanece en 24 tareas.

## Cambios

Se sustituyó el simulador legado sin consumidores identificados: importaba un modelo inexistente y devolvía utilidad e impuestos fijos. La entrada compatible `SimulationEngine.simulate_scenario` ahora exige parámetros válidos, delega en un cálculo real y no persiste resultados sin empresa ni autor verificados. No se eliminaron datos ni modelos existentes.

El motor compartido `core_erp/intelligence/cash_simulation.py` implementa remuestreo diario con reemplazo a 30, 90 y 365 días. Usa enteros en centavos, semilla explícita y generador aleatorio privado. Devuelve percentiles empíricos p05/p50/p95 de caja final, media y frecuencia de trayectorias que entraron en déficit hasta cada horizonte. El digest identifica los supuestos normalizados; no es firma digital.

Entrada estricta: caja inicial no negativa, 7–366 observaciones diarias consecutivas y ordenadas (incluidos días cero), semilla entera de 32 bits y 100–2000 trayectorias. Rechaza floats, importes no finitos/fracciones de centavo, representaciones excesivas, fechas no canónicas, desbordamientos, duplicados, huecos y campos desconocidos. La misma entrada y runtime declarado produce la misma salida, sin alterar el generador aleatorio global.

El ERP expone `POST /api/v1/mi-negocio/contable/contabilidad/cuentas/simulacion-caja/?provider_id=<UUID>`. Reutiliza sesión/JWT y autorización empresarial existentes. El cuerpo contiene exclusivamente `opening_cash`, `observations` (objetos `date`, `net_cash_flow`), `seed` y `paths`. La moneda y empresa se derivan del vínculo verificado, no del cuerpo.

Son escenarios declarados por el operador; no se presentan como movimientos extraídos del ledger, bancos o fuentes oficiales. Los percentiles son distribuciones de escenarios, no intervalos de confianza calibrados. El modelo IID no incorpora automáticamente temporadas, FX, impuestos, nómina, deuda ni eventos climáticos. No ofrece recomendaciones de inversión, ejecuta pagos, escribe asientos ni guarda documentos.

## Evidencia y límites

83 métodos Python aprobados en cinco grupos: 74 contables existentes/ampliados y nueve del simulador. Incluyen resultados analíticos conocidos para flujo constante, déficit continuo, reproducibilidad, aislamiento del RNG, orden de percentiles, límites y entradas monetarias/fechas inválidas. La API verifica titularidad, rechazo de empresa suministrada en cuerpo y ausencia de nuevos asientos. Perfil contable y workflow ampliados con estas pruebas; el workflow no se ejecutó remotamente.

Ver `evidencias/implementacion-11.json`. Sin migraciones, credenciales externas, datos del usuario, commits o push.

Pendientes: interfaz, sensibilidad y backtesting temporal fuera de muestra; contraste con series reales, factores estacionales, escenarios económicos revisados, calidad/procedencia de datos y rendimiento. Tampoco cierra integración contable corporativa de Analemática ni los restantes pools. Este corte no acredita latencia máxima de 250 ms ni exactitud predictiva.
