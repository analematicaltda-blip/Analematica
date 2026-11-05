from typing import List
from .herramientas_prestador import get_prestador_soldiers

def get_transporte_soldiers() -> List:
    """
    Recluta y devuelve la Escuadra de Transporte.
    Por ahora, utiliza las herramientas genéricas de prestadores.
    En el futuro, se pueden añadir herramientas específicas para vehículos o rutas.
    """
    return get_prestador_soldiers()