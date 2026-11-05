# ai/services/ai_manager/ai_base_provider.py
from abc import ABC, abstractmethod
 
from typing import List, Optional, Literal

class AIBaseProvider(ABC):
    """
    Clase base abstracta para un proveedor de IA.
    Cada proveedor debe declarar sus capacidades.
    """
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Lista de capacidades, ej. ['text', 'image', 'video']"""
        pass

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities

    @abstractmethod
    def generate_text(self, prompt: str, model: str, **kwargs) -> str:
        pass

    @abstractmethod
    def generate_image(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        pass

    # Se pueden añadir más métodos abstractos para otras capacidades (video, etc.)
 
