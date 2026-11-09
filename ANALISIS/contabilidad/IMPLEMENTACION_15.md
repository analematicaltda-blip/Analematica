# Implementación 15 · Backtesting desde la interfaz ERP

**Avance: 25,00 % (18/72 hitos).** Se amplía ACC-017; el alcance completo sigue pendiente de validación con series reales, múltiples ventanas y cualificación profesional.

El formulario de escenarios incorpora la opción «Evaluar resultados posteriores». Mantiene separados los flujos de entrenamiento y los 365 días posteriores declarados. Valida estructura, importes y tamaño en el cliente; el motor vuelve a comprobar continuidad, separación cronológica y ausencia de solapamientos. Usa la sesión/CSRF y autorización empresarial existentes, sin movimientos financieros ni cambios del ledger.

La pantalla muestra la simulación generada solo con entrenamiento y, por horizonte, caja posterior, mediana simulada, diferencia con signo, error absoluto e inclusión del resultado en el intervalo empírico. Añade error absoluto medio y digest de resultados posteriores, separado del digest de entrenamiento. No presenta esos indicadores como precisión certificada ni cobertura estadística calibrada.

Editar cualquier conjunto de datos oculta la evaluación anterior y cancela solicitudes pendientes. El aislamiento por empresa/identidad sigue remontando el formulario, sin persistir los datos en almacenamiento del navegador. Se conserva la identidad azul metálico, acentos celestes y texto blanco.

## Pruebas

- 22 comprobaciones integradas de Chromium → sesión/CSRF Django → ORM aislado. Se agregan error cero en serie conocida, error negativo ante resultados menores y ocultamiento de la evaluación al editar resultados posteriores.
- 93 métodos de regresión contable aprobados.
- Tipado TypeScript estricto de la ruta y sus imports sin errores.
- Evidencia local y hashes en `evidencias/implementacion-15.json`.

Se usan datos sintéticos controlados. No hay cambios de modelo, migraciones o algoritmos backend en este corte; no se repitió PostgreSQL.

## Pendientes

Múltiples ventanas temporales, series verificadas, calibración/procedencia, revisión profesional y rendimiento. La interfaz actual compara un periodo posterior por solicitud; no agrega ventanas automáticamente. También faltan pruebas integrales de accesibilidad/móvil y fallos de red, compilación completa y conexión contable autenticada de la consola Analemática, además de los demás pools. Sin cambios en bases del usuario, habilitación productiva, commits o push.
