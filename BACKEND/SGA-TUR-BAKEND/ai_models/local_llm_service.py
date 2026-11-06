import httpx
import os
from typing import Dict, Any

# --- Configuración del Cliente Ollama ---
# Se asume que Ollama se ejecuta localmente.
# La URL se puede externalizar a variables de entorno si es necesario.
OLLAMA_API_BASE_URL = os.environ.get("OLLAMA_API_BASE_URL", "http://localhost:11434/api/chat")
DEFAULT_LOCAL_MODEL = "phi3:mini"

async def invoke_local_llm(
    prompt: str,
    model_name: str = None,
    conversation_history: list = None
) -> str:
    """
    Invoca un modelo de lenguaje local a través de la API de Ollama de forma asíncrona.

    Args:
        prompt (str): El prompt del usuario.
        model_name (str, optional): El nombre del modelo a utilizar (ej: 'phi3:mini', 'phi-4').
                                    Si es None, usa el modelo por defecto.
        conversation_history (list, optional): El historial de la conversación.

    Returns:
        str: La respuesta generada por el modelo o un mensaje de error.
    """
    if not model_name:
        model_name = DEFAULT_LOCAL_MODEL

    print(f"[Local LLM Service] Invocando modelo local: {model_name}")

    headers = {"Content-Type": "application/json"}

    messages = (conversation_history or []) + [{"role": "user", "content": prompt}]

    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "stream": False,  # No usar streaming para obtener una respuesta completa
        "options": {
            "temperature": 0.7,
            "num_ctx": 4096, # Ajustar el contexto si es necesario
        }
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(OLLAMA_API_BASE_URL, json=payload, headers=headers)
            response.raise_for_status()

            response_data = response.json()

            if "message" in response_data and "content" in response_data["message"]:
                return response_data["message"]["content"]
            else:
                return f"Error: Respuesta inesperada del servicio local. Formato no reconocido: {response_data}"

    except httpx.ConnectError:
        error_msg = (
            f"Error: No se pudo conectar al servicio local de LLM en {OLLAMA_API_BASE_URL}. "
            "Asegúrate de que Ollama esté en ejecución y sea accesible."
        )
        print(error_msg)
        return error_msg
    except httpx.HTTPStatusError as e:
        error_msg = f"Error: El servicio local devolvió un estado HTTP {e.response.status_code}. Respuesta: {e.response.text}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error inesperado al invocar el modelo local '{model_name}': {e}"
        print(error_msg)
        return error_msg

# --- Bloque de prueba para ejecución directa ---
if __name__ == '__main__':
    import asyncio

    async def test_service():
        print("--- Probando el Servicio de LLM Local Generalizado ---")

        # Prueba 1: Modelo por defecto (phi3:mini)
        print("\n--- Test 1: Invocando modelo por defecto (phi3:mini) ---")
        response_phi3 = await invoke_local_llm("Explica brevemente qué es un transformador en el contexto de la IA.")
        print(f"Respuesta de Phi-3: {response_phi3}")

        # Prueba 2: Especificando otro modelo (ej: phi-4, si está disponible en Ollama)
        # Nota: Esta prueba fallará si el modelo 'phi-4' no ha sido descargado (`ollama pull phi-4`)
        print("\n--- Test 2: Invocando modelo específico (phi-4) ---")
        response_phi4 = await invoke_local_llm("Escribe un poema corto sobre el código.", model_name="phi-4")
        print(f"Respuesta de Phi-4: {response_phi4}")

        print("\n--- Pruebas del Servicio LLM Local completadas ---")

    asyncio.run(test_service())