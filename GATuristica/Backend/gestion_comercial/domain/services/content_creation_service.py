# domain/services/content_creation_service.py
from infrastructure.models import User, AIInteraction
from ai.services.ai_manager.ai_manager import ai_manager

def generate_text_with_memory(
    user: User,
    provider_name: str,
    prompt: str,
    model: str
) -> str:
    """
    Servicio de dominio para generar texto y registrar la interacción.
    """
    # 1. Obtener el proveedor de IA
    provider = ai_manager.get_provider(provider_name)

    result = ""
    error_message = ""
    try:
        # 2. Generar el resultado
        result = provider.generate_text(prompt=prompt, model=model)
        return result
    except RuntimeError as e:
        error_message = str(e)
        raise  # Re-lanzar la excepción para que la capa BFF la maneje
    finally:
        # 3. Registrar la interacción en la base de datos (siempre)
        AIInteraction.objects.create(
            tenant=user.tenant,
            user=user,
            provider=provider_name,
            prompt=prompt,
            result=result or error_message  # Guarda el resultado o el mensaje de error
        )

# La función para generar imágenes seguiría un patrón idéntico.
# Se puede añadir aquí cuando sea necesario.
