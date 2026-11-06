# domain/services/campaign_generation_service.py
import json
from infrastructure.models import User, AIInteraction
from ai.services.ai_manager.ai_manager import ai_manager

def _is_valid_campaign_json(data: str) -> bool:
    """Valida si el string es un JSON con la estructura de campaña esperada."""
    try:
        campaign = json.loads(data)
        # Aquí se añadirían validaciones más estrictas sobre la estructura del JSON
        return isinstance(campaign, list) and all('day' in post for post in campaign)
    except (json.JSONDecodeError, TypeError):
        return False

def generate_automatic_campaign(user: User, business_goal: str, max_retries: int = 3) -> dict:
    """
    Genera un plan de campaña en JSON a partir de una intención de negocio,
    con validación y reintentos.
    """
    prompt = f"""
    Actúa como un estratega de marketing digital. Crea un plan de contenido para una campaña de una semana sobre el siguiente objetivo: '{business_goal}'.
    Devuelve un calendario de 7 publicaciones en formato JSON. Cada publicación debe tener 'day', 'platform', 'content', y 'media_suggestion'.
    Responde ÚNICAMENTE con el array JSON, sin texto adicional ni markdown.
    """

    for attempt in range(max_retries):
        raw_result = ""
        error_message = ""
        try:
            # 1. Generar el resultado
            raw_result = ai_manager.execute_text_generation(prompt=prompt, model='gemini-1.5-flash') # Modelo puede ser dinámico

            # 2. Validar
            if _is_valid_campaign_json(raw_result):
                return json.loads(raw_result)
            else:
                error_message = "Invalid JSON structure received from AI."
                print(f"Attempt {attempt + 1} failed: {error_message}")

        except RuntimeError as e:
            error_message = str(e)
            print(f"Attempt {attempt + 1} failed with runtime error: {e}")
        finally:
            # 3. Registrar cada intento
            AIInteraction.objects.create(
                tenant=user.tenant,
                user=user,
                proveedor_usado='default',
                prompt_original=prompt,
                resultado=raw_result,
                errores=error_message
            )

    raise RuntimeError(f"Failed to generate a valid campaign after {max_retries} attempts.")
