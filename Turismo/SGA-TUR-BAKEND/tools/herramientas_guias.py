from typing import List
from .herramientas_prestador import get_prestador_soldiers

def get_guias_soldiers() -> List:
    """
    Recluta y devuelve la Escuadra de Guías de Turismo.
    Por ahora, utiliza las herramientas genéricas de prestadores.
    En el futuro, se pueden añadir herramientas específicas para certificaciones o idiomas.
    """
    return get_prestador_soldiers()