# Implementación 14 · Interfaz ERP de escenarios de caja

**Avance: 25,00 % (18/72 hitos).** ACC-017 ya tenía incremento y pruebas; la interfaz no acredita por sí sola su aceptación completa.

La consulta contable del ERP incorpora el formulario de escenarios del motor compartido. Permite introducir caja inicial, serie diaria explícita, semilla y número de trayectorias; seleccionar solo base o comparar con un cambio declarado de caja inicial y flujo neto diario. No precarga saldos o flujos de ejemplo como si fueran reales.

Cada línea usa `AAAA-MM-DD;importe` con dos decimales. La interfaz limita tamaño, número de días, trayectorias y semilla. El backend vuelve a validar importes, continuidad de fechas y reglas. Usa sesión y CSRF existentes, empresa autorizada y moneda resuelta por el servidor. No hay almacenamiento local de estos datos ni ejecución financiera.

Presenta p05, mediana p50, p95 y fracción de trayectorias con déficit para 30/90/365 días, junto con moneda, modelo, semilla, fechas y digest de supuestos. Los avisos distinguen escenario declarado de saldos bancarios, recomendaciones e intervalos de confianza calibrados. Conserva azul metálico, acentos celestes y texto blanco.

Editar los supuestos oculta inmediatamente la salida anterior y cancela la petición pendiente. Cambiar empresa/identidad remonta el formulario y borra sus entradas. Las respuestas de una petición abandonada no rellenan el contexto nuevo. Las solicitudes tienen plazo máximo; no se reintenta automáticamente.

## Verificación

- 19 comprobaciones integradas de Chromium → sesión/CSRF Django → ORM aislado: añade simulación base, sensibilidad, ocultamiento al editar y borrado de entradas al cambiar de empresa.
- Valores conocidos: flujo diario 1,00 y caja inicial 10,00 producen mediana 375,00 a 365 días; el cambio declarado probado produce -15,00 a 30 días.
- 93 métodos contables aprobados; tipado estricto de la ruta y sus imports sin errores.
- Evidencia y hashes locales en `evidencias/implementacion-14.json`.

Las pruebas usan datos sintéticos y no sustituyen una serie financiera verificada. No se repitió PostgreSQL ni se cambiaron modelos, migraciones o algoritmos backend en este corte.

## Pendientes

Interfaz de backtesting, comparación de múltiples cambios desde la web, validación móvil/accesibilidad integral, fallos de red y carga; múltiples ventanas temporales, procedencia de datos, calibración y revisión profesional con series reales. El bloqueo de compilación completa heredado y la conexión contable corporativa de Analemática siguen pendientes, junto con los demás pools. No se publica ni habilita producción; sin commit ni push.
