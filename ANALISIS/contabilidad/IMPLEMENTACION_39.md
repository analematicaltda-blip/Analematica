# Implementación 39 · Interfaz de consulta contable asistida

**Avance: 38,89 % (28/72 hitos).** Amplía ACC-020 ya puntuado; no agrega hitos ni aceptación completa.

## Implementación

El panel contable ERP incorpora `AccountingQuery`, conectado a la sesión y empresa autorizada existentes. Un selector ofrece las dos preguntas soportadas: rentabilidad empresarial y estado de la cola de facturación. Es un vocabulario seleccionado y determinista; no se anuncia como chat abierto ni utiliza un modelo de IA.

Para rentabilidad solicita fechas explícitas y muestra ingresos, gastos y resultado neto con moneda y fuente `ReportsEngine.get_profitability`. Para cola conserva la advertencia de aceptación fiscal no verificada. No ofrece acciones financieras. El POST corresponde a una consulta de solo lectura, no a una autorización.

Antes de mostrar resultados valida el contrato conservador, fuente/intención esperadas, UUID empresarial, coincidencia del Tenant de datos y empresa de respuesta, fechas consultadas y cadenas monetarias exactas. No convierte dinero a float. Los resultados se vinculan a sesión, prestador, pregunta y fechas; se ocultan al editar cualquier contexto, se abortan peticiones antiguas y se limpia la vista al cerrar sesión. La empresa real sigue siendo resuelta por el backend; el componente no equipara provider_id con Tenant.

Conserva fondo azul, acento azul claro y texto blanco. El formulario se ajusta a móvil y tiene etiquetas accesibles explícitas. Se corrigió el nombre accesible del selector tras detectarlo en el primer recorrido integrado.

## Verificación final

- 31 comprobaciones del recorrido completo Chromium → sesión contraseña/cookie/CSRF → Django/ORM aislado. Dos nuevas consultan rentabilidad y cola desde el panel, con herramientas reales y fuentes visibles.
- Nueve comprobaciones sintéticas: importe/fuente, paleta, móvil sin desbordamiento, edición de fechas, rechazo de contrato con SQL generado, cambio de empresa, permiso denegado, cierre de sesión y uso de POST de consulta.
- TypeScript estricto del componente sin errores. No se ejecutó build Next.js completo ni workflow remoto.

Evidencia: `evidencias/implementacion-39.json`, con hashes de fuentes. No se repitió backend/PostgreSQL: no cambiaron servicios, modelos o concurrencia.

## Pendientes

Comprensión abierta evaluada, voz, más preguntas/fuentes/roles, interfaz corporativa de Analemática, build completo y pruebas en dispositivos reales. Ampliar pruebas de respuestas tardías, fallos de red y sesiones revocadas en este panel específico. La evidencia de dos preguntas deterministas no acredita precisión IA, asesoría tributaria, aceptación fiscal o permisos para movimientos financieros.

Sin datos del usuario modificados, commit, push o despliegue.
