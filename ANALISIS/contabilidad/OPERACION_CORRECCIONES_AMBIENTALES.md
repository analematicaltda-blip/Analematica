# Correcciones ambientales conservando el original

El código reside en `BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/environmental_corrections.py`. Se apoya en el registro ambiental y Outbox existentes. No crea un segundo libro ni modifica saldos contables, pasivos, pagos o créditos de carbono.

## Recorrido

Requiere una observación previamente registrada, titular personal activo, proveedor/empresa activos y vínculo vigente. Cada llamada vuelve a comprobar identidad. La corrección conserva todos los identificadores, fechas económicas y unidades de las actividades originales; puede rectificar cantidades, reparto por pasajeros y factores explícitos. Una versión existente de un factor no puede cambiar sus valores ni su soporte: declarar una versión nueva no equivale a validar científicamente su procedencia.

En el router contable ERP:

1. GET `historia-correccion-ambiental/?observation_id=<UUID>` devuelve revisión vigente, digest de cabecera, original, estimación efectiva e historia. No restaura confirmaciones.
2. POST `revisar-correccion-ambiental/` recibe exactamente `observation_id`, `expected_revision`, `activities`, `factors`, `evidence_digest`, `reason_code`, `confirmed:true`. La revisión inicial es0. Los motivos admitidos son QUANTITY_ERROR, FACTOR_VERSION, ALLOCATION_ERROR y DATA_CORRECTION. Una corrección sin cambios de valores se rechaza.
3. POST `registrar-correccion-ambiental/` recibe exactamente `observation_id`, `review_id`, `confirmed:true`. Es la segunda confirmación del mismo titular. Una revisión competidora que ya no enlaza la cabecera actual se rechaza.

En Analemática, el puente de comandos ofrece `review_environmental_correction` y `record_environmental_correction`. La fuente `environmental_corrections` recibe únicamente `observation_id`. Conserva origen fijo, sesión del titular, CSRF, identidad corporativa/ERP y ausencia de efectos contables. No acepta destinos o empresas arbitrarios.

El reintento devuelve la misma corrección, incluso cuando existe una revisión posterior, siempre que la cadena y el vínculo sigan válidos. No restaura permisos. La operación exige una nueva revisión cuando otra corrección avanzó la cabecera. Un fallo durante la escritura revierte los factores nuevos y el registro de corrección de esa transacción.

## Presentación e integridad

La recuperación ambiental existente conserva `preview` como revisión original y añade `corrections` con la estimación vigente. Ambos paneles muestran esta última y señalan el número de corrección, que el original se conserva y que el total corregido **sustituye** al original. No se suman ambas mediciones. El soporte original no se rellena como si fuera el soporte de la corrección; las autorizaciones quedan desmarcadas.

Las revisiones y registros enlazan digests, identidad, fecha de conocimiento y factores inmutables. La comprobación detecta inconsistencias de contenido, saltos en revisiones conservadas, fuentes alteradas y ramas obsoletas. Las reclamaciones de actividad originales se mantienen: corregir no libera una actividad para volver a registrarla. Máximo100 revisiones por observación; superar el límite requiere una migración revisada, no truncamiento silencioso.

Esta cadena interna no es una blockchain pública ni almacenamiento WORM. Un operador SQL privilegiado capaz de borrar el tramo final o reescribir coherentemente toda la historia no queda neutralizado por hashes internos. Faltan controles SQL/retención, anclaje o respaldo externo y validación independiente adecuados al despliegue.

## Pendientes

No se incorporaron formularios visuales de creación de correcciones: las rutas permiten integración y el panel existente ya recupera el valor efectivo. Faltan búsqueda/cortes históricos/exportación, incertidumbre y fuentes legítimas, detección de duplicados semánticos, vínculo con operaciones reales, factores aceptados profesionalmente y reportes ESG normativos. La carrera específica con PostgreSQL y las garantías de infraestructura requieren pruebas adicionales.

No se emiten compensaciones, certificaciones GRI/SASB, asientos ni obligaciones fiscales por corregir una estimación. `independently_verified`, `esg_certified`, `liability_recognized`, `carbon_credit_issued`, `money_transferred` y `ledger_written` siguen falsos. H16 permanece EN_EJECUCION.
