# Implementación68 · Nuevo plan restante y política tributaria conectada al ledger

**Base preservada:61,11 % (44/72), sin créditos duplicados; aceptación completa0/24.** Se recuperó el entorno y se ejecutó el primer bloque del nuevo [plan de20 hitos restantes](PLAN_REMANENTE_20_HITOS.md). El plan no sustituye el porcentaje original ni declara completadas las20 tareas por documentarlas.

## Hallazgos de recuperación

La fuente de integración tributaria y sus rutas sobrevivieron a la interrupción. El archivo de pruebas no llegó a crearse. Se recuperó, amplió y ejecutó, y se añadió el recorrido corporativo HTTP. El manifiesto de la entrega67 conserva sus hashes; dentro del ámbito de fuentes medido no se eliminó ningún archivo: se identificaron tres fuentes nuevas y cinco modificadas, correspondientes al trabajo de esta integración y su runner. Esto no es una afirmación de respaldo completo de todo el sistema de archivos.

## Cambio funcional comprobado

Una reserva puede obtener su desglose desde políticas tributarias versionadas, con importe decimal exacto. La evidencia liga empresa, reserva, actor, fuente, selección y cotizaciones a su revisión. Solicitud y reconocimiento contable vuelven a validarla; eliminarla o alterarla impide avanzar. El fallo de persistencia de evidencia revierte la revisión entera.

Se probó el recorrido Analemática→HTTP autenticado→ERP→política→reserva→ledger. El mismo posteo recupera el mismo asiento; las cuentas por cobrar, ingreso y pasivo tributario quedan balanceados. Esto sí escribe el ledger de prueba mediante su servicio canónico, y no equivale a emitir/aceptar una factura o pagar.

El nuevo flujo rechaza retenciones positivas y múltiples códigos de impuesto positivo, pues requieren cuentas/tratamientos todavía no implementados. También exige que la fecha tributaria revisada coincida con la fecha del reconocimiento en este alcance. Los flujos manuales anteriores se conservan identificados; no se convierten en reglas fiscales verificadas.

## Nuevo plan ejecutable

Los20 hitos enumeran hallazgo, corrección, prioridad, dependencias, criterio de cierre y validaciones externas. Se prioriza recuperar la base y conectar impuestos; después despacho positivo, contabilidad por componente, nómina/legados/banca y demás frentes según el orden explícito. Los bloqueos externos permiten trabajo local independiente.

R01 tiene cierre local acotado verificado. R02 tiene incremento verificado por API/ORM y entre backends; su aceptación tributaria completa sigue pendiente. R03–R20 permanecen por ejecutar. Las tareas originales H06/H07 continúan abiertas por el alcance que falta; no se acreditó aceptación profesional a partir de fixtures.

[Registro de ejecución](PLAN_REMANENTE_20_HITOS.json), [contratos y límites](OPERACION_RESERVAS_POLITICA.md) y [evidencia68](evidencias/implementacion-68.json).

## Verificación final

- **576 pruebas Python aprobadas, sin omisiones, en37 suites**, incluidas14 nuevas del vínculo política/reserva y40 del puente corporativo (2 nuevas).
- Se verifican exactitud, asiento real balanceado/reintento, fuente cambiada, vínculo revocado, prueba tributaria ausente/alterada, referencia reservada sin prueba, rollback y rechazo de tratamientos fuera del alcance.
- Manifiesto estable y hashes de evidencia comparados con las fuentes actuales; evidencia histórica67 verificada. Dependencias compatibles y `git diff --check` comprobados.
- No se reejecutaron las suites históricas Chromium44/PostgreSQL52. No se añadieron formularios ni se acreditó concurrencia PostgreSQL del nuevo flujo, SQL inmutable del vínculo o aceptación normativa/productiva.

No se hicieron commits, push, modificaciones de referencias Git, despliegues, envíos DIAN, pagos ni acciones sobre cuentas reales. Los cambios permanecen en el árbol de trabajo.
