@echo off
REM ===================================================================
REM SGA-CD Desktop App & Gemma 3 4B Launcher for Windows
REM ===================================================================

echo [1/3] Verificando servicio Ollama en localhost:11434...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Ollama no esta respondiendo. Iniciando servicio Ollama en segundo plano...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
) else (
    echo [+] Servicio Ollama detectado y activo.
)

echo [2/3] Verificando disponibilidad del modelo Gemma 3 4B...
ollama list | findstr "gemma3:4b" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Descargando e instalando gemma3:4b desde el catalogo oficial de Ollama...
    ollama pull deepseek-r1:8b
) else (
    echo [+] Modelo Gemma 3 4B (gemma3:4b) verificado y disponible.
)

echo [3/3] Iniciando aplicacion de escritorio SGA-CD...
set OLLAMA_BASE_URL=http://localhost:11434
set OLLAMA_MODEL=deepseek-r1:8b
python main.py

pause

