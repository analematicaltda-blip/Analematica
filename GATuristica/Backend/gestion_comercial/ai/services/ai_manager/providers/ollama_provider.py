# ai/services/ai_manager/providers/ollama_provider.py
import requests
from ..ai_base_provider import AIBaseProvider
from typing import Optional, Literal

class OllamaProvider(AIBaseProvider):
    """
    Proveedor de IA para un servidor local de Ollama.
    """
 
    _capabilities = ["text"]

    @property
    def capabilities(self) -> list[str]:
        return self._capabilities

 
    def __init__(self, endpoint: str):
        if not endpoint:
            raise ValueError("Ollama endpoint is required.")
        self.endpoint = f"{endpoint}/api"

    def generate_text(self, prompt: str, model: str, **kwargs) -> str:
        try:
            response = requests.post(
                f"{self.endpoint}/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"Error generating text with Ollama: {e}")
            raise RuntimeError("Failed to generate text using Ollama.") from e

    def generate_image(
        self,
        prompt: str,
        model: str,
        size: Optional[Literal['256x256', '512x512', '1024x1024']] = None,
        **kwargs
    ) -> Optional[str]:
        print(f"Conceptual implementation for Ollama image generation with model {model}.")
        try:
            response = requests.post(
                f"{self.endpoint}/generate",
                json={"model": model, "prompt": f"Generate an image of: {prompt}", "stream": False},
            )
            response.raise_for_status()
            images = response.json().get("images")
            if images and isinstance(images, list) and len(images) > 0:
                return f"data:image/jpeg;base64,{images[0]}"
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error generating image with Ollama: {e}")
            raise RuntimeError("Failed to generate image using Ollama.") from e
