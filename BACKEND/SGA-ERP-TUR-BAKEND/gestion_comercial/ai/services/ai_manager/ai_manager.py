# ai/services/ai_manager/ai_manager.py
import os
import logging
from rest_framework.exceptions import APIException
from dotenv import load_dotenv
from typing import List, Optional
from .ai_base_provider import AIBaseProvider

logger=logging.getLogger(__name__)
class AIProviderUnavailable(APIException):
    status_code=503
    default_detail='No hay proveedor IA disponible; no se generó contenido.'
    default_code='ai_provider_unavailable'


class AIManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIManager, cls).__new__(cls)
            cls._instance.providers: List[AIBaseProvider] = []
            cls._instance._initialize_providers()
        return cls._instance

    def _initialize_providers(self):

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                from .providers.gemini_provider import GeminiProvider
                self.providers.append(GeminiProvider(api_key=gemini_api_key))

            except Exception:
                logger.warning("Configured Gemini unavailable; credentials not logged.")

        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
        if ollama_endpoint:
            try:
                from .providers.ollama_provider import OllamaProvider
                self.providers.append(OllamaProvider(endpoint=ollama_endpoint))

            except Exception:
                logger.warning("Configured Ollama unavailable; credentials not logged.")

        if not self.providers:
            logger.info("No provider configured; no synthetic fallback enabled.")

    def _find_provider_for_capability(self, capability: str) -> Optional[AIBaseProvider]:
        for provider in self.providers:
            if provider.has_capability(capability):
                return provider
        return None

    def execute_text_generation(self, prompt: str, model: str, **kwargs) -> (str, str):
        provider = self._find_provider_for_capability('text')
        if not provider:
            raise AIProviderUnavailable()
        generated_text = provider.generate_text(prompt=prompt, model=model, **kwargs)
        provider_name = provider.__class__.__name__
        return generated_text, provider_name

    def execute_image_generation(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        provider = self._find_provider_for_capability('image')
        if not provider:
            raise AIProviderUnavailable()
        return provider.generate_image(prompt=prompt, model=model, **kwargs)

ai_manager = AIManager()
