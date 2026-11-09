# Implementación 10 · Liquidez con revisión histórica explícita

**Avance verificable: 22,22 % (16/72 hitos).** Se amplía un incremento ya puntuado de ACC-016; no se da por completada su aceptación.

El núcleo compartido permite solicitar una revisión concreta de la clasificación de liquidez mediante `quick_ratio(..., policy_revision=n)`. El endpoint ERP existente acepta `revision=<entero positivo>`. Si no se indica, conserva el uso de la revisión más reciente. Una revisión inexistente o perteneciente a otra empresa no se sustituye silenciosamente por la actual: rechaza la consulta.

La interfaz incorpora un campo opcional para elegir revisión, confirma que la respuesta usa la solicitada y muestra la versión aplicada. Cambiar la selección oculta el resultado anterior hasta recibir una respuesta válida. No se modifican políticas, asientos ni importes. Se conservan los controles de permisos, clasificación y conciliación.

El resultado indica explícitamente que se recalcula con los asientos contabilizados actuales hasta el corte económico. No es una reconstrucción de qué información se conocía originalmente ni una copia del estado financiero publicado en aquella fecha. Se puede aplicar una clasificación revisada después del corte, de forma explícita. Cuentas históricas hoy inactivas o reclasificadas siguen requiriendo conciliación para poder calcular; no se relajan las validaciones para producir cifras.

## Pruebas

- 73 métodos contables aprobados: incluye dos clasificaciones diferentes para el mismo corte que producen 3,0000 y 0,0000, selección de revisión anterior sin sobrescritura, empresa ajena y revisiones inválidas/inexistentes.
- 15 comprobaciones integradas de Chromium, sesión/CSRF real de Django y ORM aislado: selección de revisión 1 y regreso a la revisión reciente.
- Tipado TypeScript estricto sin errores; hashes de evidencia local comprobados.

Datos y usuarios sintéticos aislados; no se modificaron bases del usuario, migraciones ni servicios de producción. No se repitió PostgreSQL porque se conserva el bloqueo existente y no hay cambios de esquema ni algoritmos concurrentes.

Evidencia: `evidencias/implementacion-10.json`.

Pendientes: conexión contable autenticada de la consola Analemática, políticas por vigencia y reconocimiento bitemporal si se requiere reproducir estados publicados, revisión profesional y datos reales, métricas operativas y restantes pools. Las revisiones históricas explícitas no equivalen a todos esos requisitos. Sin commit ni push.
