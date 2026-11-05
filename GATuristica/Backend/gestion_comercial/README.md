 
# Backend - Sistema Operativo de IA para Marketing

Este backend está construido con Python y Django para servir como un sistema operativo de IA proveedor-agnóstico, escalable y autónomo.

## 1. Arquitectura del Módulo de IA

El núcleo es un **Orquestador de Tareas** (`AIManager`) que recibe solicitudes de tareas (ej. "generar texto") y las enruta dinámicamente al proveedor de IA compatible más adecuado (Gemini, Ollama, etc.).

- **Capas:** `bff` -> `domain` -> `ai` -> `infrastructure`
- **Flujo de Datos:** El frontend solicita una tarea, no un proveedor. El `AIManager` selecciona el proveedor y ejecuta. El `domain` service registra cada interacción en la base de datos.

## 2. Configuración e Instalación
(Instrucciones de `venv`, `pip install`, `.env` y `migrate` se mantienen como antes)

...

## 3. API del Estudio de IA (`/api/ai/`)

Requiere autenticación.

### Asistente de Redacción
---
#### `POST /api/ai/text`
Genera texto sanitizado y registra la interacción.
- **Body:** `{"prompt": "Un prompt para generar texto."}`
- **Respuesta:** `{"result": "Texto generado y limpio."}`

### Generador de Campañas
---
#### `POST /api/ai/campaign`
Genera una estructura de campaña en JSON, validada y corregida por el backend.
- **Body:** `{"business_goal": "Lanzar un nuevo producto ecológico."}`
- **Respuesta:** Un array JSON con la estructura de la campaña.

### Generador de Video (Asíncrono)
---
#### `POST /api/ai/video`
Inicia un trabajo de generación de video.
- **Body:** `{"prompt": "Un video de un gato volando."}`
- **Respuesta:** `{"job_id": "some-unique-task-id"}`

#### `GET /api/ai/video/status/{job_id}`
Consulta el estado de un trabajo de generación de video.
- **Respuesta:** `{"status": "processing"}`

... (Otros endpoints de Creative Suite como `/api/ai/image` seguirían un patrón similar) ...
 