# Implementación 43 · Agregación focalizada de rentabilidad

**Avance: 38,89 % (28/72 hitos).** Optimiza ACC-016 ya puntuado; no agrega hitos ni certifica rendimiento productivo.

## Cambio funcional

La rentabilidad agregaba cuentas de todos los tipos y después descartaba en Python las que no son ingresos/costos/gastos. `_totals` admite ahora una proyección interna explícita de tipos; get_profitability limita su GROUP BY a REVENUE, EXPENSE, COST_OF_SALES y PRODUCTION_COST. El catálogo de tipos aceptados es acotado y usa parámetros del ORM, no SQL construido con texto del usuario.

El filtro se aplica después de las comprobaciones generales de saldos iniciales y valoración extranjera. Una cuenta de activo con un saldo legado o valoración pendiente sigue bloqueando el reporte, aunque no vaya a aparecer en sus fuentes. Se conserva empresa explícita, fuente primaria, bloqueo empresarial y verificación de moneda base. Balance de prueba, balance general y otros llamadores que no pasan filtro conservan su comportamiento.

No se altera la fórmula ni se eliminan cuentas del catálogo. La mejora reduce los grupos devueltos al proceso; no elimina el coste de las comprobaciones generales ni prueba una latencia determinada.

## Verificación

182 métodos Python aprobados en trece suites. Cuatro nuevos verifican una fixture que pasa de siete grupos generales a un grupo de ingreso en la proyección, igualdad de la fila agregada y del resultado financiero, filtro presente en el SQL capturado y ausencia de consultas por cada cuenta. También prueban rechazo de una valoración inválida en activos excluidos, saldo inicial pendiente e intento de proyección no admitida.

24 escenarios contables PostgreSQL y 33 comprobaciones integradas del panel/sesión/API aprobados como regresión. La comprobación específica del SQL filtrado y número de grupos usa ORM/SQLite; no se presenta como benchmark PostgreSQL bajo carga.

Evidencia: `evidencias/implementacion-43.json`. Fuente estable en el perfil contable. No se crean índices, tablas o migraciones.

## Pendientes

EXPLAIN y mediciones con distribución real de datos en PostgreSQL, índices revisados, comparación de tiempos/memoria, concurrencia de reportes y objetivo de 250 ms de la directriz. No se declara mejora porcentual de latencia a partir del número de grupos de esta fixture. Continúan pendientes integración corporativa Analemática, métricas operativas por paquete/habitación y fuentes verificadas.

Sin datos del usuario modificados, commit, push o despliegue.
