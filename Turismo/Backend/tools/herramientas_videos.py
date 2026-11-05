# from langchain_core.tools import tool
from typing import List, Dict
from api.models import Video


@tool
def crear_video(titulo: str, descripcion: str, url_youtube: str) -> Dict:
    """
    (SOLDADO DE VIDEOS) Ejecuta la creación de un nuevo video en la plataforma.
    Requiere un título, una descripción y la URL completa de YouTube.
    """
    print(f"--- 💥 SOLDADO (Videos): ¡ACCIÓN! Creando video con título '{titulo}'. ---")
    try:
        # Validación simple de URL de YouTube
        if "v=" not in url_youtube:
            return {
                "status": "error",
                "message": "La URL de YouTube no parece válida. Debe contener 'v='."
            }

        video = Video.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            url_youtube=url_youtube,
            es_publicado=True  # mantenemos la mejora de la rama feat
        )
        return {
            "status": "success",
            "video_id": video.id,
            "message": f"El video '{titulo}' ha sido añadido a la plataforma."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ocurrió un error inesperado al crear el video: {str(e)}"
        }


def get_videos_soldiers() -> List:
    """ Recluta y devuelve la Escuadra de Videos completa. """
    return [
        crear_video,
    ]