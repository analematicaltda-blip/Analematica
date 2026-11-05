# domain/services/image_generation_service.py
from infrastructure.models import User, AIInteraction, ContentAsset
from ai.services.ai_manager.ai_manager import ai_manager

def generate_image_with_memory(user: User, prompt: str, model: str) -> ContentAsset:
    """
    Servicio de dominio para generar una imagen, persistirla como un Asset
    y registrar la interacción.
    """
    result_url = ""
    error_message = ""
    try:
        result_url = ai_manager.execute_image_generation(prompt=prompt, model=model)
        if not result_url:
            raise RuntimeError("AI provider did not return an image.")

        asset = ContentAsset.objects.create(
            tenant=user.tenant,
            asset_type='image',
            content=result_url
        )
        return asset
    except RuntimeError as e:
        error_message = str(e)
        raise
    finally:
        AIInteraction.objects.create(
            tenant=user.tenant,
            user=user,
            proveedor_usado='default_image',
            prompt_original=prompt,
            resultado=result_url or "",
            errores=error_message
        )
