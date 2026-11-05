# ai/services/ai_manager/providers/dummy_provider.py
from ..ai_base_provider import AIBaseProvider
from typing import List, Optional

class DummyProvider(AIBaseProvider):
    @property
    def capabilities(self) -> List[str]:
        return ["text", "image"]

    def generate_text(self, prompt: str, model: str, **kwargs) -> str:
        return f"Dummy text for prompt: {prompt}"

    def generate_image(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        # This provider doesn't generate real images, so it returns None.
        return None
