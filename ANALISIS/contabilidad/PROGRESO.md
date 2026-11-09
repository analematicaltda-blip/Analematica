# Avance verificable del motor de contabilidad

**Implementación y optimización: 63.89 %** · 46/72 hitos.
**Alcance completo aceptado: 0/24 tareas. Producción: no habilitada.**

La base es la directriz de siete pools y las 24 tareas de `matriz-pools.csv`. Cada tarea tiene tres hitos de igual peso:

1. Existe un incremento funcional ejecutable de la tarea, aunque su alcance todavía sea parcial.
2. Ese incremento dispone de verificación automatizada reproducible.
3. Se cumplen todos los criterios de aceptación de la tarea, incluidos ambos sistemas y las validaciones reales requeridas.

El máximo antes de aceptación completa de una tarea es 2/3. El porcentaje mide estos hitos, no líneas de código, horas, porcentaje de pruebas cubiertas ni ausencia de vulnerabilidades. No se obtiene crédito por documentación o planificación solas. El registro es una evaluación explícita de evidencias, no una deducción automática por presencia de archivos.

23 tareas tienen incrementos verificados; ninguna acredita aún su alcance completo. Reforzar pruebas existentes no aumenta automáticamente el porcentaje. El 100 % significará cumplimiento comprobado de esta versión del alcance, no perfección absoluta ni inmunidad a ataques.

| Frente | Hitos | Implementación verificable |
|---|---:|---:|
| Núcleo y puente contable | 16/24 | 66.67 % |
| Comercial y fiscal | 6/9 | 66.67 % |
| Bóveda documental | 4/6 | 66.67 % |
| Operación y nómina | 4/6 | 66.67 % |
| Analítica financiera | 4/6 | 66.67 % |
| Sostenibilidad | 2/6 | 33.33 % |
| Asistencia y automatización | 4/6 | 66.67 % |
| Offline, rendimiento y operación | 6/9 | 66.67 % |

Los frentes agrupan las mismas 24 tareas sin duplicarlas ni cambiar el denominador. No son porcentajes de producción.

| Tarea | Hitos completados | Alcance completo aceptado |
|---|---:|---|
| ACC-001 | 2/3 | No |
| ACC-002 | 2/3 | No |
| ACC-003 | 2/3 | No |
| ACC-004 | 2/3 | No |
| ACC-005 | 2/3 | No |
| ACC-006 | 2/3 | No |
| ACC-007 | 2/3 | No |
| ACC-008 | 2/3 | No |
| ACC-009 | 2/3 | No |
| ACC-010 | 2/3 | No |
| ACC-011 | 2/3 | No |
| ACC-012 | 2/3 | No |
| ACC-013 | 2/3 | No |
| ACC-014 | 2/3 | No |
| ACC-015 | 2/3 | No |
| ACC-016 | 2/3 | No |
| ACC-017 | 2/3 | No |
| ACC-018 | 2/3 | No |
| ACC-019 | 0/3 | No |
| ACC-020 | 2/3 | No |
| ACC-021 | 2/3 | No |
| ACC-022 | 2/3 | No |
| ACC-023 | 2/3 | No |
| ACC-024 | 2/3 | No |

Registro: `progress-registry.json`. Resultado calculado: `progreso.json`.
Regenerar con `python ANALISIS/contabilidad/tools/update_progress.py`; comprobar coherencia con `--check`.

Antes de cambiar el alcance o las ponderaciones se debe documentar una nueva base y conservar la anterior. Las acreditaciones de producción no se deducen del porcentaje.
