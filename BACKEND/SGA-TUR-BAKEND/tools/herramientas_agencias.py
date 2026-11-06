from typing import List
from .herramientas_prestador import get_prestador_soldiers

def get_agencias_soldiers() -> List:
    """
    Recluta y devuelve la Escuadra de Agencias de Viajes.
    Por ahora, utiliza las herramientas genéricas de prestadores.
    En el futuro, se pueden añadir herramientas específicas para paquetes turísticos.
    """
    return get_prestador_soldiers()