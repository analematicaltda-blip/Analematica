# Implementación 05 · Clasificación revisada y liquidez ácida

Estado: desarrollo local del núcleo contable compartido de Analemática y ERP turístico. No activa producción ni movimientos de dinero. No se hicieron commits ni push.

## Funcionalidad

La liquidez ácida se calcula exclusivamente con cuentas seleccionadas y revisadas por el titular empresarial. No se deduce que una cuenta sea corriente, efectivo disponible o cartera inmediata por su código o nombre. La política exige cuatro grupos explícitos: efectivo/equivalentes, inversiones temporales, cuentas por cobrar inmediatas y pasivos corrientes. Se pueden declarar vacíos inversiones y cartera, pero deben existir cuentas de activo y pasivo seleccionadas.

Cada revisión conserva empresa, número de revisión, responsable, clasificación, fecha y hash de la evidencia declarada. El hash del registro permite detectar alteraciones accidentales o cambios sin actualizarlo; no es firma digital, prueba independiente ni garantía contra un operador SQL privilegiado. La evidencia y la completitud de la clasificación son declaradas por el revisor: deben validarse con el contador antes de uso productivo.

Las cuentas deben ser activas, pertenecer a la misma empresa y plan de esa empresa y tener el tipo contable correcto. Se impide usar una cuenta en dos grupos, incluyendo duplicados dentro de un grupo. La revisión esperada evita sobrescribir una actualización concurrente: el segundo solicitante debe recargar y revisar. Cambiar una política crea otra revisión, sin actualizar la anterior.

El cálculo acumula movimientos contabilizados hasta el corte, no solo movimientos del mes. Usa moneda base y base primaria bajo el bloqueo empresarial compartido con el posteo. Incluye fuentes e importes por cuenta, totales, fórmula, unidad y revisión aplicada. Los saldos sin conciliar, moneda base histórica diferente y clasificación inválida bloquean el informe. Un denominador cero o saldo individual negativo devuelve valor no calculable con motivo explícito, sin valor absoluto, reclasificación ni importes inventados.

Se aplica explícitamente la clasificación más reciente al corte solicitado; no constituye reconstrucción automática de la política vigente en una fecha histórica. Los datos no contabilizados y las cuentas omitidas por el revisor no se incorporan. No es una certificación de liquidez disponible ni una autorización de pago.

## API del ERP

Bajo `/api/v1/mi-negocio/contable/contabilidad/cuentas/`:

- `GET clasificacion-liquidez/?provider_id=<UUID>`: última revisión o nulo si no existe.
- `POST clasificacion-liquidez/?provider_id=<UUID>`: revisión con `mapping`, `evidence_digest` SHA-256 hexadecimal, `expected_revision` entero desde 0 y `confirmed: true`.
- `GET liquidez-acida/?provider_id=<UUID>&fecha_corte=2026-11-08`: cálculo o motivo de indisponibilidad.

`mapping` contiene listas de UUID de cuentas con las claves `cash_equivalents`, `temporary_investments`, `immediate_receivables` y `current_liabilities`. No acepta saldos suministrados por el cliente ni campos adicionales. Reutiliza autenticación y vínculo empresarial verificado del catálogo; un superusuario sin titularidad no obtiene acceso. El servicio compartido puede ser consumido por Analemática; su pantalla aún debe integrarse.

Las revisiones configuran una consulta analítica. No son las autorizaciones financieras del motor de pagos y no permiten ejecutarlos ni eludir sus controles.

## Migración y pruebas

Migración aditiva `core_erp.0004_accounting_ratio_policy` en ambos árboles de migraciones. No precarga clasificaciones ni modifica asientos. Solo se aplicó en el fixture privado de pruebas, sin bases del usuario. El grafo nativo histórico requiere ensayo independiente antes de aplicarlo a producción.

Ver evidencias finales en `evidencias/implementacion-05.json` y `implementacion-05-verificacion.json`. Incluyen regresión contable, carrera PostgreSQL entre dos revisiones esperadas iguales y regresión de instalación ERP migrada. Las pruebas usan datos sintéticos aislados, no certifican saldos reales.

## Pendientes

Pantallas de Analemática y ERP con la identidad azul vigente, revisión profesional de cobertura y evidencia, políticas históricas por vigencia, controles SQL contra operadores privilegiados, prueba con datos reales y medición de rendimiento. RevPAR, GOPPAR y margen por paquete siguen necesitando integración operativa y clasificación específica. No se cierra el pool 5 ni el plan maestro.
