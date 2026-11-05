# backend/apps/sadi_agent/translation_service.py
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Servicio para manejar la traducción de texto.
    Fallback a Dummy Service debido a incompatibilidades de versiones entre googletrans, httpx y httpcore.
    """
    def __init__(self, base_language='es'):
        self.base_language = base_language

    def normalize_to_base_language(self, text: str, source_language: str) -> str:
        """
        Traduce el texto al idioma base del sistema (español).
        """
        return text

    def translate_response(self, text: str, target_language: str) -> str:
        """
        Traduce la respuesta del sistema al idioma de destino del usuario.
        """
        return text
