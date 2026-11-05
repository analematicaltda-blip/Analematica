import os
import httpx
import tiktoken
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
from asgiref.sync import sync_to_async

# --- Importaciones de Django y del proyecto ---
from api.models import SiteConfiguration, CustomUser, UserLLMConfig
from .local_llm_service import invoke_local_llm

# Cargar variables de entorno
load_dotenv()

# --- Configuración de Modelos y Palabras Clave ---
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama3-8b-8192"
DEEP_REASONING_KEYWORDS = ["analiza", "resume", "explica", "corrige", "evalúa", "genera un reporte", "crea un plan", "redacta"]

def count_tokens(text: str) -> int:
    """Calcula el número de tokens en un texto usando tiktoken."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return len(text.split())

def requires_deep_reasoning(prompt: str) -> bool:
    """Verifica si el prompt contiene palabras clave que sugieren una tarea compleja."""
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in DEEP_REASONING_KEYWORDS)

async def invoke_groq_api(prompt: str, api_key: str, conversation_history: List[Dict[str, str]]) -> str:
    """Envía un prompt y el historial a la API de Groq de forma asíncrona."""
    if not api_key:
        return "Error: No se ha proporcionado una clave API para Groq."

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = conversation_history + [{"role": "user", "content": prompt}]
    data = {"model": GROQ_MODEL_NAME, "messages": messages, "temperature": 0.7}

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
    except httpx.RequestError as e:
        return f"Error de conexión a la API de Groq: {e}"
    except (KeyError, IndexError, TypeError) as e:
        return f"Respuesta inesperada de la API de Groq. Error: {e}"

@sync_to_async
def get_user_llm_config(user: Optional[CustomUser]) -> Optional[UserLLMConfig]:
    """Obtiene la configuración LLM de un usuario de forma asíncrona."""
    if user and user.is_authenticated and hasattr(user, 'llm_config'):
        return user.llm_config
    return None

@sync_to_async
def get_system_llm_config() -> Dict[str, Any]:
    """Obtiene la configuración LLM del sistema (claves y umbrales) de forma asíncrona."""
    config = SiteConfiguration.load()
    return {
        "groq_api_key": config.groq_api_key,
        "token_threshold": config.llm_routing_token_threshold
    }

async def route_llm_request(
    prompt: str,
    conversation_history: List[Dict[str, str]],
    user: Optional[CustomUser]
) -> str:
    """
    Enruta una solicitud al LLM apropiado de forma asíncrona, priorizando la configuración del usuario.
    """
    # 1. Verificar la configuración personalizada del usuario
    user_config = await get_user_llm_config(user)

    if user_config and user_config.provider != 'SYSTEM_DEFAULT':
        provider = user_config.provider
        print(f"[LLM Router] Usando configuración personalizada del usuario: {provider}")

        if provider == 'GROQ' and user_config.api_key:
            return await invoke_groq_api(prompt, user_config.api_key, conversation_history)

        if provider == 'PHI3_LOCAL':
            return await invoke_local_llm(prompt, model_name="phi3:mini", conversation_history=conversation_history)

        if provider == 'PHI4_LOCAL':
            # Asumiendo que el modelo 'phi-4' está disponible en Ollama
            return await invoke_local_llm(prompt, model_name="phi-4", conversation_history=conversation_history)

    # 2. Si no hay configuración de usuario, usar el router híbrido del sistema
    print("[LLM Router] Usando router híbrido del sistema.")
    system_config = await get_system_llm_config()
    system_groq_key = system_config.get("groq_api_key")
    token_threshold = system_config.get("token_threshold", 1500)

    # 3. Lógica de enrutamiento híbrido
    history_text = " ".join([msg["content"] for msg in conversation_history])
    total_tokens = count_tokens(history_text + prompt)
    is_complex_task = requires_deep_reasoning(prompt)

    use_cloud_model = total_tokens > token_threshold or is_complex_task

    if use_cloud_model:
        if system_groq_key:
            print(f"[LLM Router] Tarea compleja o historial largo ({total_tokens} tokens). Usando Groq del sistema.")
            return await invoke_groq_api(prompt, system_groq_key, conversation_history)
        else:
            print(f"[LLM Router] Advertencia: Se necesita modelo avanzado pero no hay clave Groq del sistema. Usando modelo local.")
            return await invoke_local_llm(prompt, conversation_history=conversation_history)
    else:
        print(f"[LLM Router] Tarea simple ({total_tokens} tokens). Usando modelo local por defecto (Phi-3).")
        return await invoke_local_llm(prompt, conversation_history=conversation_history)

# --- Bloque de prueba (requiere un entorno Django asíncrono para ejecutarse) ---
# Para probar, puedes crear un comando de gestión en Django que llame a esta función.
# Ejemplo: python manage.py test_llm_router
if __name__ == '__main__':
    # La ejecución directa de este script es limitada porque necesita el entorno de Django
    # para las llamadas a la base de datos.
    print("Este script debe ejecutarse dentro de un contexto de Django para funcionar correctamente.")
    print("Ejemplo: python manage.py shell -c 'from ai_models.llm_router import route_llm_request; import asyncio; asyncio.run(route_llm_request(...))'")