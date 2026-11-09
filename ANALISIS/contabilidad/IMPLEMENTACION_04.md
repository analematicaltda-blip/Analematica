# Implementación 04 · Rentabilidad trazable del libro mayor

Estado: desarrollo local. Continúa el núcleo compartido de Analemática y ERP turístico sin reemplazar sus módulos. No habilita producción ni pagos y no realiza commits o push.

El servicio `ReportsEngine.get_profitability` calcula ingresos, gastos, resultado neto y margen neto de la empresa a partir de líneas contabilizadas. Usa importes Decimal en moneda base y devuelve las cuentas de origen, intervalo económico y fórmula. Consulta la base primaria bajo el bloqueo empresarial compartido con el posteo, para evitar mezclar lecturas con un posteo concurrente o depender del retraso de una réplica.

El margen es empresarial: no representa margen por paquete, GOP ni flujo de caja. Los ingresos no positivos devuelven valor nulo y motivo explícito. Se rechazan intervalos invertidos, saldos iniciales sin conciliar y asientos del intervalo con moneda base distinta de la actual. Los borradores, otras empresas y movimientos fuera del periodo quedan excluidos. Las contrapartidas contabilizadas afectan el resultado normalmente; no se cambia la historia.

## Consulta del ERP

`GET /api/v1/mi-negocio/contable/contabilidad/cuentas/rentabilidad/?provider_id=<UUID>&desde=2026-11-01&hasta=2026-11-08`

Reutiliza autenticación y vínculo empresarial verificado del catálogo. Sin fechas usa el primer día del mes actual y la fecha actual. Acceso solo al titular autorizado; no añade permisos por ser superusuario. El cálculo compartido queda disponible a los servicios de Analemática; no se ha añadido una pantalla nueva a su frontend.

Los indicadores RevPAR, GOPPAR, liquidez ácida y margen por paquete aparecen como pendientes con los datos necesarios. No se infieren habitaciones disponibles, cuentas corrientes ni atribuciones a paquetes a partir de totales generales. Requieren clasificación revisada e integración operativa posterior.

## Verificación

Ejecución local aislada del perfil `accounting`, con pruebas de permisos, cálculo, gastos, reversión, datos vacíos, fechas, moneda y saldos iniciales. La primera ejecución detectó un error en el auxiliar de una prueba nueva; se corrigió el auxiliar y se repitió el perfil completo. Evidencia final en `evidencias/implementacion-04.json` y `implementacion-04-verificacion.json`. No requiere migración ni modifica bases del usuario.

Pendientes: visualización en ambos frontends conservando la identidad azul, clasificación revisada de cuentas para otros ratios, atribución operativa por paquete y habitación, medición de rendimiento, validación con contabilidad real y todas las integraciones fiscales/BYOS aún abiertas en la matriz. Este avance no cierra el pool 5 ni el plan completo.
