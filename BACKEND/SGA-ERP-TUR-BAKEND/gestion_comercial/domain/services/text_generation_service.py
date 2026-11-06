# domain/services/text_generation_service.py
import re
from infrastructure.models import User, AIInteraction
from ai.services.ai_manager.ai_manager import ai_manager

def _sanitize_ai_output(text: str) -> str:
    """Limpia la salida de texto de la IA, removiendo bloques de código y espacios."""
    text = re.sub(r'```(json|markdown)?', '', text)
    text = text.strip()
    return text

def generate_text_with_memory(
    user: User,
    prompt: str,
    model: str,
    task: str = "text" # Placeholder para el futuro
) -> str:
    """
    Servicio de dominio para generar texto, sanitizarlo y registrar la interacción.
    """
    result = ""
    error_message = ""
    interaction = None
    try:
        # 1. Llamar al orquestador de IA
        result = ai_manager.execute_text_generation(prompt=prompt, model=model)
        result = _sanitize_ai_output(result)
        return result
    except RuntimeError as e:
        error_message = str(e)
        raise
    finally:
        # 2. Registrar la interacción (siempre)
        interaction = AIInteraction.objects.create(
            tenant=user.tenant,
            user=user,
            proveedor_usado='default', # El AIManager podría exponer esto
            prompt_original=prompt,
            resultado=result,
            errores=error_message
        )
