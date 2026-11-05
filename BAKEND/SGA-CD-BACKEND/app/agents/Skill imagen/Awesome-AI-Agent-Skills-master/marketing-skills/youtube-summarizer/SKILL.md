---
name: youtube-summarizer
description: Extract, transcribe, cache, and summarize YouTube videos locally using yt-dlp, Faster-Whisper, and Ollama-based summaries.
---

# YouTube Summarizer (Turbo Local Edition)

Extrae transcripciones y resume videos de YouTube de forma 100% local, ahorrando tokens y evitando bloqueos.

## Capacidades
- **Detección Automática**: Reconoce URLs de YouTube (`watch`, `youtu.be`, `shorts`).
- **Extracción de Audio**: Utiliza `yt-dlp` para bajar solo el flujo de audio (rápido y ligero).
- **Transcripción Local**: Usa **Faster-Whisper** para transcribir el audio sin salir de tu máquina.
- **Resumen Local**: Utiliza **Ollama** (Llama 3/Qwen) para generar resúmenes y responder dudas específicas.
- **Memoria Eterna**: Guarda las transcripciones en una carpeta de caché local (`transcripts/`) para acceso instantáneo futuro.

## Activación
Se activa automáticamente cuando el usuario proporciona un enlace de YouTube o pide:
- "Resume este video: [URL]"
- "Pregunta sobre el video [ID]: [Duda]"

## Flujo de Trabajo (Soberanía Digital)
1. **Identificación**: Extrae el ID del video.
2. **Caché Check**: Si ya existe en `transcripts/`, salta directo al resumen.
3. **Extracción Nuclear**: Si no existe:
   - Descarga audio ligero con `yt-dlp`.
   - Transcribe con Whisper local.
   - Guarda el resultado en un archivo JSON.
4. **Inteligencia Local**: Envía el texto a Ollama para procesar el resumen o la respuesta final.

## Instrucciones para el Agente
- Prioriza siempre el uso de los recursos locales (Ollama y Whisper).
- Si el usuario tiene dudas específicas, usa el comando `summarizer.py [ID] "[Pregunta]"` para obtener respuestas de la base de datos local.
- No ganes tokens de contexto leyendo transcripciones largas; deja que Ollama haga el trabajo pesado.
