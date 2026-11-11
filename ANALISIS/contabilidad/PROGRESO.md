# Avance verificable del motor de contabilidad

**Implementación y optimización: 79.17 %** · 57/72 hitos.
**Alcance completo aceptado: 9/24 tareas. Producción: no habilitada.**

La base es la directriz de siete pools y las 24 tareas de `matriz-pools.csv`. Cada tarea tiene tres hitos de igual peso:

1. Existe un incremento funcional ejecutable de la tarea, aunque su alcance todavía sea parcial.
2. Ese incremento dispone de verificación automatizada reproducible.
3. Se cumplen todos los criterios de aceptación de la tarea, incluidos ambos sistemas y las validaciones reales requeridas.

El máximo antes de aceptación completa de una tarea es 2/3. El porcentaje mide estos hitos, no líneas de código, horas, porcentaje de pruebas cubiertas ni ausencia de vulnerabilidades. No se obtiene crédito por documentación o planificación solas. El registro es una evaluación explícita de evidencias, no una deducción automática por presencia de archivos.

24 tareas tienen incrementos verificados; 9 tienen aceptación completa registrada. Reforzar pruebas existentes no aumenta automáticamente el porcentaje. El 100 % significará cumplimiento comprobado de esta versión del alcance, no perfección absoluta ni inmunidad a ataques.

| Frente | Hitos | Implementación verificable |
|---|---:|---:|
| Núcleo y puente contable | 23/24 | 95.83 % |
| Comercial y fiscal | 7/9 | 77.78 % |
| Bóveda documental | 5/6 | 83.33 % |
| Operación y nómina | 4/6 | 66.67 % |
| Analítica financiera | 4/6 | 66.67 % |
| Sostenibilidad | 4/6 | 66.67 % |
| Asistencia y automatización | 4/6 | 66.67 % |
| Offline, rendimiento y operación | 6/9 | 66.67 % |

Los frentes agrupan las mismas 24 tareas sin duplicarlas ni cambiar el denominador. No son porcentajes de producción.

| Tarea | Hitos completados | Alcance completo aceptado |
|---|---:|---|
| ACC-001 | 3/3 | Sí |
| ACC-002 | 3/3 | Sí |
| ACC-003 | 3/3 | Sí |
| ACC-004 | 3/3 | Sí |
| ACC-005 | 3/3 | Sí |
| ACC-006 | 3/3 | Sí |
| ACC-007 | 3/3 | Sí |
| ACC-008 | 3/3 | Sí |
| ACC-009 | 2/3 | No |
| ACC-010 | 3/3 | Sí |
| ACC-011 | 2/3 | No |
| ACC-012 | 2/3 | No |
| ACC-013 | 2/3 | No |
| ACC-014 | 2/3 | No |
| ACC-015 | 2/3 | No |
| ACC-016 | 2/3 | No |
| ACC-017 | 2/3 | No |
| ACC-018 | 2/3 | No |
| ACC-019 | 2/3 | No |
| ACC-020 | 2/3 | No |
| ACC-021 | 2/3 | No |
| ACC-022 | 2/3 | No |
| ACC-023 | 2/3 | No |
| ACC-024 | 2/3 | No |

Registro: `progress-registry.json`. Resultado calculado: `progreso.json`.
Regenerar con `python ANALISIS/contabilidad/tools/update_progress.py`; comprobar coherencia con `--check`.

Antes de cambiar el alcance o las ponderaciones se debe documentar una nueva base y conservar la anterior. Las acreditaciones de producción no se deducen del porcentaje.

## Índice explícito de los72 hitos

La numeración conserva la base original: cada tarea tiene tres hitos consecutivos. ACREDITADO significa acreditación curada en el registro, no inferida por presencia de archivos ni nueva aceptación productiva. Los criterios, referencias y pendientes de cada hito están en `progreso.json`.

| Hito | Tarea | Etapa | Acreditación registrada |
|---|---|---|---|
| H001 | ACC-001 | Incremento funcional | Sí |
| H002 | ACC-001 | Verificación automatizada | Sí |
| H003 | ACC-001 | Aceptación completa | Sí |
| H004 | ACC-002 | Incremento funcional | Sí |
| H005 | ACC-002 | Verificación automatizada | Sí |
| H006 | ACC-002 | Aceptación completa | Sí |
| H007 | ACC-003 | Incremento funcional | Sí |
| H008 | ACC-003 | Verificación automatizada | Sí |
| H009 | ACC-003 | Aceptación completa | Sí |
| H010 | ACC-004 | Incremento funcional | Sí |
| H011 | ACC-004 | Verificación automatizada | Sí |
| H012 | ACC-004 | Aceptación completa | Sí |
| H013 | ACC-005 | Incremento funcional | Sí |
| H014 | ACC-005 | Verificación automatizada | Sí |
| H015 | ACC-005 | Aceptación completa | Sí |
| H016 | ACC-006 | Incremento funcional | Sí |
| H017 | ACC-006 | Verificación automatizada | Sí |
| H018 | ACC-006 | Aceptación completa | Sí |
| H019 | ACC-007 | Incremento funcional | Sí |
| H020 | ACC-007 | Verificación automatizada | Sí |
| H021 | ACC-007 | Aceptación completa | Sí |
| H022 | ACC-008 | Incremento funcional | Sí |
| H023 | ACC-008 | Verificación automatizada | Sí |
| H024 | ACC-008 | Aceptación completa | Sí |
| H025 | ACC-009 | Incremento funcional | Sí |
| H026 | ACC-009 | Verificación automatizada | Sí |
| H027 | ACC-009 | Aceptación completa | Pendiente |
| H028 | ACC-010 | Incremento funcional | Sí |
| H029 | ACC-010 | Verificación automatizada | Sí |
| H030 | ACC-010 | Aceptación completa | Sí |
| H031 | ACC-011 | Incremento funcional | Sí |
| H032 | ACC-011 | Verificación automatizada | Sí |
| H033 | ACC-011 | Aceptación completa | Pendiente |
| H034 | ACC-012 | Incremento funcional | Sí |
| H035 | ACC-012 | Verificación automatizada | Sí |
| H036 | ACC-012 | Aceptación completa | Pendiente |
| H037 | ACC-013 | Incremento funcional | Sí |
| H038 | ACC-013 | Verificación automatizada | Sí |
| H039 | ACC-013 | Aceptación completa | Pendiente |
| H040 | ACC-014 | Incremento funcional | Sí |
| H041 | ACC-014 | Verificación automatizada | Sí |
| H042 | ACC-014 | Aceptación completa | Pendiente |
| H043 | ACC-015 | Incremento funcional | Sí |
| H044 | ACC-015 | Verificación automatizada | Sí |
| H045 | ACC-015 | Aceptación completa | Pendiente |
| H046 | ACC-016 | Incremento funcional | Sí |
| H047 | ACC-016 | Verificación automatizada | Sí |
| H048 | ACC-016 | Aceptación completa | Pendiente |
| H049 | ACC-017 | Incremento funcional | Sí |
| H050 | ACC-017 | Verificación automatizada | Sí |
| H051 | ACC-017 | Aceptación completa | Pendiente |
| H052 | ACC-018 | Incremento funcional | Sí |
| H053 | ACC-018 | Verificación automatizada | Sí |
| H054 | ACC-018 | Aceptación completa | Pendiente |
| H055 | ACC-019 | Incremento funcional | Sí |
| H056 | ACC-019 | Verificación automatizada | Sí |
| H057 | ACC-019 | Aceptación completa | Pendiente |
| H058 | ACC-020 | Incremento funcional | Sí |
| H059 | ACC-020 | Verificación automatizada | Sí |
| H060 | ACC-020 | Aceptación completa | Pendiente |
| H061 | ACC-021 | Incremento funcional | Sí |
| H062 | ACC-021 | Verificación automatizada | Sí |
| H063 | ACC-021 | Aceptación completa | Pendiente |
| H064 | ACC-022 | Incremento funcional | Sí |
| H065 | ACC-022 | Verificación automatizada | Sí |
| H066 | ACC-022 | Aceptación completa | Pendiente |
| H067 | ACC-023 | Incremento funcional | Sí |
| H068 | ACC-023 | Verificación automatizada | Sí |
| H069 | ACC-023 | Aceptación completa | Pendiente |
| H070 | ACC-024 | Incremento funcional | Sí |
| H071 | ACC-024 | Verificación automatizada | Sí |
| H072 | ACC-024 | Aceptación completa | Pendiente |
