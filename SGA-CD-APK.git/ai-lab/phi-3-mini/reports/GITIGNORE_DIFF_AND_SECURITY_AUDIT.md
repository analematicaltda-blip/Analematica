# SGA-CD — Auditoría de Seguridad y Diff de .gitignore (Fase PoC-PHI3-R1)

**Fecha:** 27 de Octubre de 2026
**Componente:** `.gitignore` (Raíz) y `SGA-CD-APK.git/.gitignore`

---

## 1. Análisis Comparativo Línea por Línea

### A. `.gitignore` (Raíz del Monorepo)
- **Estado Base (HEAD `ff97c4dd`)**:
  Contenía las reglas históricas para proteger secretos (`client_secrets.json`, `*.env`), caché de Python (`__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`), entornos virtuales (`venv/`, `**/venv/`), herramientas locales (`tools/`) y bases de datos (`*.db`, `*.sqlite3`).
- **Inyección PoC-PHI3-R1**:
  Se preservaron el 100% de las reglas históricas y se agregaron únicamente al final del archivo las siguientes reglas de aislamiento de modelos de IA:
  ```gitignore
  # AI Models & Local Weights
  **/weights/
  *.onnx
  *.onnx.data
  ```

### B. `SGA-CD-APK.git/.gitignore`
- **Estado Base (HEAD `ff97c4dd`)**:
  Contenía las reglas para ignorar archivos de configuración (`config.json`, `*.env`), bases de datos (`*.db`, `*.sqlite3`), caché de Python y entornos virtuales.
- **Inyección PoC-PHI3-R1**:
  Se preservaron el 100% de las reglas históricas y se agregaron únicamente al final del archivo las siguientes reglas locales:
  ```gitignore
  # Local AI Lab Weights
  /ai-lab/phi-3-mini/weights/
  *.onnx
  *.onnx.data
  ```

---

## 2. Matriz de Pruebas con `git check-ignore -v`

Se ejecutaron pruebas de verificación sobre archivos de prueba sensibles y de artefactos para confirmar que las reglas activas excluyen correctamente los elementos requeridos:

| Patrón Evaluado | Archivo de Prueba Evaluado | Regla que lo Excluye | Estado de Exclusión (`git check-ignore`) | Dictamen de Seguridad |
| :--- | :--- | :--- | :--- | :--- |
| `client_secrets.json` | `client_secrets.json` | `.gitignore:2:client_secrets.json` | **EXCLUIDO** | **SEGURO** |
| `*.env` | `test.env` | `.gitignore:3:*.env` | **EXCLUIDO** | **SEGURO** |
| `*.db` | `test.db` | `.gitignore:17:*.db` | **EXCLUIDO** | **SEGURO** |
| `*.sqlite3` | `test.sqlite3` | `.gitignore:18:*.sqlite3` | **EXCLUIDO** | **SEGURO** |
| `__pycache__/` | `__pycache__/test.pyc` | `.gitignore:6:__pycache__/` | **EXCLUIDO** | **SEGURO** |
| `**/venv/` | `venv/test.py` | `.gitignore:11:**/venv/` | **EXCLUIDO** | **SEGURO** |
| `/ai-lab/phi-3-mini/weights/` | `.../weights/phi3...onnx.data` | `SGA-CD-APK.git/.gitignore:18` | **EXCLUIDO** | **SEGURO** |
| `*.onnx` | `.../weights/phi3...onnx` | `.gitignore:22:*.onnx` | **EXCLUIDO** | **SEGURO** |

---

## 3. Estado de Seguimiento en Git

- **Archivos Sensibles de Configuración**: Cero archivos `.env`, `client_secrets.json` o bases de datos SQLite están rastreados.
- **Pesos y Binarios del Modelo ONNX (2.62 GB)**: Se ejecutó `git rm --cached -r` sobre cualquier metadato previamente en la caché del índice de la carpeta `weights/`.
- **Confirmación Final**: `git status` acredita que la carpeta `SGA-CD-APK.git/ai-lab/phi-3-mini/weights/` está totalmente ignorada por Git y no se incluirá en ningún commit o push.
