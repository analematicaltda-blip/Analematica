from typing import List
from .herramientas_prestador import get_prestador_soldiers

def get_restaurantes_soldiers() -> List:
    """
    Recluta y devuelve la Escuadra de Restaurantes completa.
    Por ahora, utiliza las herramientas genéricas de prestadores.
    En el futuro, se pueden añadir herramientas específicas para menús, etc.
    """
    return get_prestador_soldiers()