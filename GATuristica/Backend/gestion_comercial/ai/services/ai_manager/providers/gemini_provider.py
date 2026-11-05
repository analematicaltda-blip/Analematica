# ai/services/ai_manager/providers/gemini_provider.py
import google.generativeai as genai
from ..ai_base_provider import AIBaseProvider
from typing import Optional, Literal

class GeminiProvider(AIBaseProvider):
    """
    Proveedor de IA para Google Gemini.
    """
 
    _capabilities = ["text", "image"] # Asumiendo que Gemini puede hacer ambas

    @property
    def capabilities(self) -> list[str]:
        return self._capabilities

 
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Google Gemini API key is required.")
        genai.configure(api_key=api_key)

    def generate_text(self, prompt: str, model: str, **kwargs) -> str:
        try:
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating text with Gemini: {e}")
            raise RuntimeError("Failed to generate text using Gemini.") from e

    def generate_image(
        self,
        prompt: str,
        model: str,
        size: Optional[Literal['256x256', '512x512', '1024x1024']] = None,
        **kwargs
    ) -> Optional[str]:
        print("Conceptual implementation for Gemini image generation.")
        try:
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(f"Generate an image of: {prompt}")
            if response.text.startswith("data:image"):
                return response.text
            return None
        except Exception as e:
            print(f"Error generating image with Gemini: {e}")
            raise RuntimeError("Failed to generate image using Gemini.") from e
