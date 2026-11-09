# Implementación 37 · Panel de cola comercial en el ERP

**Avance: 36,11 % (26/72 hitos).** Extiende ACC-008, ya puntuado. No acredita aceptación fiscal o integración corporativa Analemática.

## Implementación web

Se integra `CommercialQueue` en la página existente de indicadores contables. Reutiliza la sesión del ERP, la selección de empresas autorizadas y la API de solo lectura del titular. Consulta cantidades de solicitudes de factura y confirmaciones de reserva, separadas por estado de transporte, con acción explícita de consulta. No habilita publicación, emisión, pago o modificación de eventos.

Conserva superficies azules, acento azul claro y texto blanco. Adapta las cantidades a columnas flexibles. Muestra que el consumidor fiscal sigue pendiente y que un estado de transporte no certifica factura, pago o asiento. Valida cantidades enteras no negativas y las banderas conservadoras del contrato; rechaza respuestas incompatibles y no conserva resultados anteriores ante error.

Los datos se vinculan al contexto sesión/empresa; se ocultan inmediatamente al cambiarlo y se abortan peticiones pendientes. La página usa una key específica para evitar colisiones con los demás paneles. Los resultados también desaparecen al cerrar sesión.

## Hallazgo corregido durante integración

La primera prueba con Django detectó que el componente no desenvolvía `{success:true,data:...}`, usado por la API. Se corrigió la lectura y se repitieron las pruebas; el caso sintético también usa ahora esa envoltura. No se dio por completado el panel con la prueba sintética inicial.

## Evidencia final

- 29 comprobaciones del recorrido integrado real Chromium → contraseña/cookie/CSRF → Django/ORM aislado, incluyendo la nueva consulta empresarial desde el panel completo.
- Nueve comprobaciones sintéticas de interfaz: cantidades, pendiente fiscal, rechazo de contrato incoherente, cambio de empresa, permiso denegado, cierre de sesión, identidad azul/blanco, móvil sin desbordamiento y solo GET.
- TypeScript estricto del componente sin errores. No equivale a build Next.js completo.

Evidencia: `evidencias/implementacion-37.json`, con hashes de fuentes. Se añadieron pasos al workflow; no se ejecutó CI remoto. No se repitieron las 160 pruebas Python o PostgreSQL porque no cambió backend, esquema o concurrencia.

## Pendientes

Consumidor fiscal con recibos idempotentes y acuses reales, origen tributario revisado, recorrido corporativo Analemática, build completo con dependencias del proyecto y validación visual/funcional en dispositivos reales. Las respuestas sintéticas y los datos aislados no acreditan producción ni aceptación DIAN. La cola vacía no significa ciclo comercial completo.

Sin cambios de datos del usuario, commit, push o despliegue.
