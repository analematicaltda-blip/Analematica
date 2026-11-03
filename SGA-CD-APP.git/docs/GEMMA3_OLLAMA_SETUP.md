# Guía de Inicio Rápido: SGA-CD Desktop con Gemma 3 4B (Ollama)

Esta guía explica cómo ejecutar la aplicación de escritorio SGA-CD conectada localmente al modelo **Gemma 3 4B** utilizando Ollama en Windows y entornos Linux compatibles.

---

## 1. Requisitos del Entorno

- **Sistema Operativo:** Windows 10 / 11 (64-bit) o Ubuntu / Debian Linux.
- **Servidor LLM:** Ollama (versión v0.40.11 o superior) instalado desde [https://ollama.com](https://ollama.com).
- **Entorno Python:** Python 3.10+ con dependencias de `SGA-CD-APP.git/requirements.txt` (incluyendo `flet`, `langchain-ollama`).
- **RAM Recomendada:** Mínimo 8 GB RAM (3.4 GB requeridos para pesos de `gemma3:4b`).

---

## 2. Instalación y Verificación del Modelo Gemma 3 4B

Para verificar la presencia del modelo en Ollama:

```cmd
ollama list
```

Si el modelo no está instalado, descargarlo con el identificador exacto:

```cmd
ollama pull gemma3:4b
```

Para verificar que el servicio responde en la API local (`http://localhost:11434`):

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

---

## 3. Configuración de Variables de Entorno

La aplicación SGA-CD Desktop permite configurar la conexión a Ollama mediante variables de entorno:

- `OLLAMA_BASE_URL`: Dirección del servicio Ollama (Predeterminado: `http://localhost:11434`).
- `OLLAMA_MODEL`: Identificador exacto del modelo (Predeterminado: `gemma3:4b`).

---

## 4. Métodos de Inicio

### Método 1: Script Automatizado para Windows (Recomendado)
En la carpeta `SGA-CD-APP.git/`, ejecute:

```cmd
start_desktop_ollama.bat
```

Este script realiza automáticamente:
1. Verificación del servicio Ollama en `http://localhost:11434` (lo inicia en segundo plano con `ollama serve` si está detenido).
2. Verificación del modelo `gemma3:4b` mediante `ollama list` (avisa si falta).
3. Exportación de `OLLAMA_BASE_URL` y `OLLAMA_MODEL`.
4. Ejecución de la aplicación de escritorio (`python main.py`).

### Método 2: Inicio Manual
1. Iniciar Ollama:
   ```cmd
   ollama serve
   ```
2. Ejecutar la aplicación:
   ```cmd
   set OLLAMA_BASE_URL=http://localhost:11434
   set OLLAMA_MODEL=gemma3:4b
   python main.py
   ```

---

## 5. Inferencia de Comprobación y Prueba con `llm_service.py`

Puede realizar una consulta REST directa de prueba:

```powershell
$body = @{
    model = "gemma3:4b"
    messages = @(@{role = "user"; content = "Responde en español: escribe exactamente la frase Modelo local operativo."})
    stream = $false
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://localhost:11434/api/chat" -Method Post -ContentType "application/json" -Body $body
```

---

## 6. Diagnóstico y Manejo de Errores

| Escenario | Síntoma en App / Log | Solución |
| :--- | :--- | :--- |
| **Servicio Detenido** | `[Errno 111] Connection refused` / Estado: `error_ollama_not_found` | Iniciar el servicio ejecutando `ollama serve` o `start_desktop_ollama.bat`. |
| **Modelo Ausente** | `model 'gemma3:4b' not found (status code 404)` | Ejecutar `ollama pull gemma3:4b`. |
| **Puerto Ocupado** | `bind: address already in use` | El servicio ya está corriendo. No abrir instancias redundantes. |

---

## 7. Ejecución de Pruebas Automatizadas

Navegue a `SGA-CD-APP.git/` y ejecute:

```bash
PYTHONPATH=.:../SGA-CD-FASTAPI-BACKEND python3 test_gemma3_ollama_integration.py
```

La suite valida:
- Inicialización correcta de `ChatOllama` con `gemma3:4b`.
- Respuesta a consultas en vivo.
- Sobreescrituras mediante `OLLAMA_BASE_URL` y `OLLAMA_MODEL`.
- Captura limpia de errores cuando el servicio está fuera de línea o el modelo no existe.

---

## 8. Ubicación Física del Modelo

- **Windows:** `C:\Users\<Usuario>\.ollama\models\` (`blobs/` y `manifests/`).
- **Linux:** `~/.ollama/models/` (`blobs/` y `manifests/`).
