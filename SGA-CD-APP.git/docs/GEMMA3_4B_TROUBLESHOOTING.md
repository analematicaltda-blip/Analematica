# GEMMA 3 4B EN SGA-CD DESKTOP — GUÍA DE RESOLUCIÓN DE PROBLEMAS (TROUBLESHOOTING)

Este documento detalla los problemas reproducibles identificados durante las fases de pruebas de integración con **Gemma 3 4B** y **Ollama**, sus causas raíz confirmadas y las soluciones verificadas.

---

## 1. Problema: Conexión rechazada (`[Errno 111] Connection refused`) / Estado `error_ollama_not_found`

### Causa Confirmada
El servicio local de Ollama no se encuentra en ejecución en `http://localhost:11434` al momento en que la aplicación SGA-CD Desktop inicializa `llm_service.py`.

### Comprobación Diagnóstica
Ejecutar en la consola:
```powershell
curl -s http://localhost:11434/api/tags
```
Si devuelve error de conexión o tiempo de espera agotado, el servicio está apagado.

### Solución Verificada
Inicie el servicio de Ollama mediante el script de inicio automatizado:
```cmd
start_desktop_ollama.bat
```
O de forma manual ejecutando:
```cmd
ollama serve
```

---

## 2. Problema: Modelo no encontrado (`model 'gemma3:4b' not found - status code 404`)

### Causa Confirmada
Ollama está ejecutándose correctamente, pero el modelo `gemma3:4b` no ha sido descargado en el almacenamiento local del equipo (`.ollama/models/`).

### Comprobación Diagnóstica
Ejecutar:
```cmd
ollama list
```
Verificar si `gemma3:4b` figura en el listado.

### Solución Verificada
Descargar el modelo directamente desde el catálogo oficial de Ollama:
```cmd
ollama pull gemma3:4b
```

---

## 3. Problema: Falso positivo de inicialización cuando Ollama falla

### Causa Confirmada
Anteriormente en `agent/llm_service.py`, si `ChatOllama` lanzaba una excepción durante `llm.invoke("test")`, el bloque `except` establecía `_llm_status = "error_ollama_not_found"`, pero el bloque subsiguiente `if llm:` asignaba erróneamente `_llm_status = "initialized"`.

### Solución Verificada
Se aplicó la corrección en `llm_service.py`:
```python
if llm and _llm_status != "error_ollama_not_found":
    _llm_instance = llm
    _llm_status = "initialized"
```
Esta corrección garantiza que cualquier fallo de conexión con Ollama impida la asignación del estado `"initialized"`, reportando adecuadamente `"error_ollama_not_found"` a la interfaz Flet para que muestre el diálogo de ayuda al usuario.

---

## 4. Problema: Conflicto de puertos o múltiples instancias de `ollama serve`

### Causa Confirmada
Intentar ejecutar `ollama serve` cuando el servicio en segundo plano de Ollama (ej. servicio de Windows o bandeja del sistema) ya está activo en el puerto 11434.

### Comprobación Diagnóstica
El log muestra:
```text
Error: listen tcp 127.0.0.1:11434: bind: address already in use
```

### Solución Verificada
No es necesario ejecutar `ollama serve` manualmente si el servicio de Ollama ya está activo. El script `start_desktop_ollama.bat` verifica mediante un ping HTTP previo (`curl -s http://localhost:11434/api/tags`) y omite el arranque de proceso si Ollama ya responde.
