# Implementación77 · Saldos y cobertura de período bancario

El flujo existente de conciliación en ERP y Analemática ahora admite revisar un período declarado completo, contrastando saldo inicial/final del extracto con los del libro y comprobando que ningún movimiento contable quede omitido. Mantiene revisión y segunda autorización, recuperación y liberación. No genera ajustes ni pagos.

## Resultado operativo

En el caso verificado: apertura declarada0,00, entradas10,00 +5,00, cierre declarado15,00. El libro contiene esas mismas dos entradas; apertura/cierre y cobertura coinciden. Después de la segunda autorización `period_reconciled` es verdadero y se recupera el mismo resultado sin restaurar autorizaciones. `bank_verified` permanece falso: el cotejo no autentica al banco.

## Hallazgos subsanados

- Las coincidencias por fila no verificaban saldos: ahora la apertura más entradas menos salidas debe igualar el cierre declarado y se contrasta con los saldos contables reales.
- Un mismo saldo final podía ocultar omisiones compensadas: se comprueban también todos los identificadores de movimientos del período; dos movimientos omitidos opuestos impiden calificar el período aunque sumen cero.
- Faltaba revisar el origen del saldo inicial: se calcula desde la historia contable de la cuenta, incluyendo contrapartidas, y se rechazan aperturas heredadas no conciliadas.
- Un movimiento retroactivo podía dejar vigente una aprobación antigua: antes de confirmar se recalculan fuente/cobertura; después, una modificación hace que `period_source_current` y `period_reconciled` sean falsos.
- Se podían confundir filas asociadas con período conciliado: los indicadores son distintos y la interfaz muestra el resultado de período y sus diferencias.
- Faltaban controles: fechas, saldos y huella se declaran expresamente, con confirmación de que el CSV contiene el período completo. Editar descarta la revisión y sus autorizaciones.

## Verificación

**820 pruebas Python aprobadas en46 suites, sin omisiones**, incluidas84 del puente corporativo. Fuentes actuales estables y hashes de registros comprobados.14 pruebas ORM nuevas, un recorrido HTTP corporativo nuevo y cuatro pruebas nuevas de contrato. Casos de aritmética inválida, declaración/evidencia ausentes, fechas, diferencias inicial/final, omisiones compensadas, cambios entre autorizaciones, movimientos retroactivos, cuenta inactiva, recuperación, liberación y números firmados exactos.

**78 comprobaciones Chromium**:40 de período y38 de regresión parcial en ambos paneles. Tipos estrictos de componentes seleccionados aprobados; capturas inspeccionadas conservan azul y blanco. No sustituye build completa ni validación en dispositivos físicos.

Capturas: [ERP](evidencias/implementacion-77-erp.png) · [Analemática](evidencias/implementacion-77-corporate.png).

[Evidencia77](evidencias/implementacion-77.json) · [Contrato operativo](OPERACION_PERIODO_BANCARIO.md).

## Alcance y pendientes

Se coteja el extracto que el propietario declara completo contra el libro COP. Sin conexión/autenticación bancaria independiente no se acredita que el archivo corresponda a todo el extracto legítimo. No se incorporan datos reales ni se declara aceptación profesional.

Límites explícitos actuales:30 filas importadas por revisión,200 movimientos del período y2000 líneas históricas de caja por evaluación. Rechaza excedentes; no los trunca silenciosamente. Faltan períodos sin movimientos, snapshots históricos para mayor volumen, pagos divididos/agrupados, FX, reglas/archivos de proveedores y cualificación PostgreSQL/productiva.

El verificador corporativo aumenta su tiempo máximo de120 a150 segundos: la suite anterior ya tardaba116,347 segundos y se añadió el recorrido de período. Los fallos y el límite permanecen obligatorios; no es una promesa de latencia productiva.

**63,89% (46/72), aceptación completa0/24.** Se amplía ACC-015 ya acreditada; los20 hitos no están cerrados. Sin commits, push, despliegues ni movimientos de dinero.
