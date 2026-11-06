"""
Templates canónicos de la Doctrina DEAA-V2.1 para el sistema de agentes.
"""
from .soldado_template import SoldadoBase
from .sargento_template import SargentoBase
from .teniente_template import TenienteBase
from .capitan_template import CapitánBase
from .coronel_template import CoronelBase

__all__ = [
    "SoldadoBase",
    "SargentoBase",
    "TenienteBase",
    "CapitánBase",
    "CoronelBase"
]
