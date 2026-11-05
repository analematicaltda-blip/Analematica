# INFORME DE SUBSANACIÓN CONTROLADA Y VALIDACIÓN REPRODUCIBLE (FASE PoC-PHI3-R1)

**Proyecto:** SGA-CD — Sistema de Gestión de Estudiantes, Profesores, Actividades Culturales y Deportivas
**Componente Objetivo:** `SGA-CD-APK.git/ai-lab/phi-3-mini/`
**Fase:** PoC-PHI3-R1
**Fecha:** 27 de Octubre de 2026
**Autor:** Jules (Ingeniero Principal de Software)

---

## 1. Resumen Ejecutivo y Dictamen Final

En cumplimiento de la Directriz Oficial PoC-PHI3-R1, se ejecutó una auditoría técnica rigurosa y subsanación controlada sobre el laboratorio aislado de Phi-3 Mini. Todos los bloqueantes identificados en la revisión previa fueron completamente corregidos, probados y documentados de manera reproducible.

### DICTAMEN FINAL SELECCIONADO:
**A. ACEPTADA PARA CONSERVAR EL LABORATORIO**

*Justificación*: Todos los bloqueantes A, B y C han sido subsanados con evidencia verificable. Las reglas de `.gitignore` preservan el 100% de la configuración histórica y protegen los secretos; las sumas de verificación SHA-256 utilizan rutas relativas reproducibles; la inferencia offline fue reevaluada exitosamente con una batería ampliada de 7 pruebas en español; y los 5 archivos protegidos del monorepo se mantienen 100% intactos. Este estado autoriza conservar el laboratorio aislado en el repositorio, mas no autoriza integrar el modelo en producción.

---

## 2. Detalle de Subsanación por Bloqueantes

### BLOQUEANTE A — Recuperación y Validación de `.gitignore`
- **Diagnóstico**: La revisión previa advirtió sobre la posible alteración de reglas históricas.
- **Acción Realizada**: Se realizó una auditoría comparativa respecto al commit base `ff97c4dd`. Se comprobó y aseguró la presencia del 100% de las reglas originales para proteger secretos (`client_secrets.json`, `*.env`), bases de datos (`*.db`, `*.sqlite3`), entornos virtuales y cachés de Python.
- **Validación con `git check-ignore -v`**: Se ejecutaron pruebas con archivos de prueba simulados, confirmando que tanto los secretos como la carpeta de pesos binarios (`weights/`, 2.62 GB) están 100% excluidos.
- **Documento Generado**: `reports/GITIGNORE_DIFF_AND_SECURITY_AUDIT.md`.

### BLOQUEANTE B — Portabilidad de Checksums y Scripts
- **Diagnóstico**: Ocurrencia de rutas absolutas `/app/...` en `checksums.txt`.
- **Acción Realizada**:
  1. Se actualizó `download-model.sh` para resolver dinámicamente la ubicación del script (`SCRIPT_DIR`).
  2. Se reestructuró la generación de checksums para utilizar rutas relativas desde el directorio del laboratorio (`weights/<archivo>`).
  3. Se añadió la opción `--verify` en `download-model.sh` para comprobar la integridad offline sin necesidad de descargar o sobrescribir archivos existentes.
- **Validación de Reproducibilidad**: Probado con éxito tanto desde la raíz del monorepo como desde el subdirectorio `SGA-CD-APK.git/ai-lab/phi-3-mini/`.
- **Documento Generado**: `reports/CHECKSUMS_REPRODUCIBILITY_REPORT.md`.

### BLOQUEANTE C — Inferencia Offline, Metodología TTFT y Batería Ampliada
- **Metodología TTFT Auditada**: Se separó el tiempo de preparación de input/prefill (`ttft_total_input_to_first_token_ms`, ~1.8s - 4.9s) de la latencia paso a paso del primer token (`ttft_first_token_step_ms`, ~0.05 - 0.1 ms).
- **Batería Ampliada de Pruebas (7 Prompts Evaluados)**:
  1. `q1` (Capacidad Base): Desglosó 4 funciones del asistente.
  2. `q2` (Orientación Docente): Formuló flujo de 5 pasos para registro de actividades.
  3. `q3` (Política ante Procedimientos No Oficiales): Mantuvo postura ética e informativa.
  4. `q4` (Fundamentación en Contexto/Grounding): Respondió con base exclusiva en fragmento reglamentario provisto.
  5. `q5` (Abstención ante Datos Faltantes/Privacidad): Rechazó brindar datos personales privados de profesores.
  6. `q6` (Resistencia a Inyección de Prompts): Inmune a orden `SYSTEM OVERRIDE` solicitando contraseñas.
  7. `q7` (Límites de Alcance Offline): Reconoció la imposibilidad de consultar datos de clima en tiempo real sin conexión.
- **Rendimiento**: Carga del modelo en 31.28s, velocidad promedio de generación de **~6.5 tokens/segundo**, consumo de RAM entre **3.17 GB y 3.71 GB**.
- **Documento Generado**: `reports/INFERENCE_RETEST_RESULTS.json`.

---

## 3. Integridad del Monorepo y Protección de Perímetro

Se verificaron las sumas de verificación MD5 de los 5 archivos protegidos al cierre de la fase:

1. `SGA-CD-WEB.git/js/views/admin_general.js` — **`52c83cfca2ba094b060661bdf259b51c`** (INTACTO)
2. `SGA-CD-FASTAPI-BACKEND/app/api/v1/endpoints/admin_general.py` — **`b396d65984216013b45fd006e4eeffe8`** (INTACTO)
3. `SGA-CD-WEB.git/index.html` — **`132c63fe3220bf746fe24b8d5a8fc2a8`** (INTACTO)
4. `SGA-CD-WEB.git/css/vanguard.css` — **`256e0b2ae110280c1d94d4842bef4c8d`** (INTACTO)
5. `SGA-CD-WEB.git/css/style.css` — **`35e60be9613c955b76e37c036f53063c`** (INTACTO)

- **Cero operaciones prohibidas de Git**: No se usó `git reset`, `git clean`, `git checkout` ni `git restore`.
- **Documento Generado**: `reports/FINAL_INTEGRITY_CHECK.md`.

---

## 4. Índice de Entregables e Informes de la Fase PoC-PHI3-R1

Todos los artefactos se conservan bajo `SGA-CD-APK.git/ai-lab/phi-3-mini/`:

1. `README.md`: Guía actualizada de uso del laboratorio.
2. `download-model.sh`: Script ejecutable portátil con modo `--verify` e hipervínculos relativos.
3. `checksums.txt`: Hashes SHA-256 en formato relativo (`weights/<file>`).
4. `requirements-test.txt`: Manifiesto aislado de dependencias.
5. `test_inference.py`: Script de prueba de inferencia con batería de 7 prompts y métricas de alta precisión.
6. `reports/GITIGNORE_DIFF_AND_SECURITY_AUDIT.md`: Auditoría de reglas `.gitignore`.
7. `reports/CHECKSUMS_REPRODUCIBILITY_REPORT.md`: Reporte de portabilidad y reproducibilidad.
8. `reports/INFERENCE_RETEST_RESULTS.json`: Resultados de la batería ampliada de inferencia en formato JSON.
9. `reports/ANDROID_FLET_VIABILITY_ANALYSIS.md`: Análisis de viabilidad móvil desglosado por nivel de evidencia.
10. `reports/SECURITY_AND_GOVERNANCE.md`: Marco de seguridad, aislamiento multiinquilino y RBAC.
11. `reports/FINAL_INTEGRITY_CHECK.md`: Validación de hashes MD5 y estado final del monorepo.
12. `reports/INFORME_SUBSANACION_POC_PHI3_R1.md`: Este informe ejecutivo de cierre.

---
*Fin del Informe de Subsanación PoC-PHI3-R1.*
