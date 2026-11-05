# ai/services/ai_manager/ai_manager.py
import os
from dotenv import load_dotenv
from typing import List, Optional
from .providers.gemini_provider import GeminiProvider
from .providers.ollama_provider import OllamaProvider
from .providers.dummy_provider import DummyProvider
from .ai_base_provider import AIBaseProvider

load_dotenv()

class AIManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIManager, cls).__new__(cls)
            cls._instance.providers: List[AIBaseProvider] = []
            cls._instance._initialize_providers()
        return cls._instance

    def _initialize_providers(self):
        print("Initializing AI providers...")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                self.providers.append(GeminiProvider(api_key=gemini_api_key))
                print("Gemini provider initialized.")
            except Exception as e:
                print(f"Failed to initialize Gemini provider: {e}")

        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
        if ollama_endpoint:
            try:
                self.providers.append(OllamaProvider(endpoint=ollama_endpoint))
                print("Ollama provider initialized.")
            except Exception as e:
                print(f"Failed to initialize Ollama provider: {e}")

        if not self.providers:
            print("Warning: No AI providers initialized. Falling back to DummyProvider.")
            self.providers.append(DummyProvider())

    def _find_provider_for_capability(self, capability: str) -> Optional[AIBaseProvider]:
        for provider in self.providers:
            if provider.has_capability(capability):
                return provider
        return None

    def execute_text_generation(self, prompt: str, model: str, **kwargs) -> (str, str):
        provider = self._find_provider_for_capability('text')
        if not provider:
            raise RuntimeError("No provider available for text generation.")
        generated_text = provider.generate_text(prompt=prompt, model=model, **kwargs)
        provider_name = provider.__class__.__name__
        return generated_text, provider_name

    def execute_image_generation(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        provider = self._find_provider_for_capability('image')
        if not provider:
            raise RuntimeError("No provider available for image generation.")
        return provider.generate_image(prompt=prompt, model=model, **kwargs)

ai_manager = AIManager()
