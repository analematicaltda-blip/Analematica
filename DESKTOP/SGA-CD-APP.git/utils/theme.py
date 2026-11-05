import flet as ft

# 🎨 Paleta de colores definida por el usuario
COLOR_VERDE_AZULADO = "#008F87"
COLOR_VERDE_AZULADO_BRILLANTE = "#00B3A4" # Variante para Dark Mode
COLOR_DORADO = "#FFD369"
COLOR_NEGRO_PROFUNDO = "#1C1C1E"
COLOR_BLANCO_SUAVE = "#0D1424"
COLOR_TEXTO_SECUNDARIO_LIGHT = "#4A4A4A"
COLOR_TEXTO_PRINCIPAL_DARK = "#38BDF8"
COLOR_TEXTO_SECUNDARIO_DARK = "#7DD3FC"
COLOR_FONDO_TARJETA_DARK = "#2B2B2E"
COLOR_BORDE_TARJETA_LIGHT = "#E0E0E0"
COLOR_BORDE_TARJETA_DARK = "#2E5E5C"

def create_light_theme():
    """
    Crea la variante azul luminosa, sin superficies blancas.
    """
    theme = create_dark_metallic_blue_theme()
    theme.color_scheme.background = "#0B1B31"
    theme.color_scheme.surface = "#12304A"
    return theme

from .theme_mapper import create_dark_metallic_blue_theme

def create_dark_theme():
    """
    Crea el tema oscuro Dark Metallic Blue para la aplicación SGA-CD Flet,
    garantizando alineación cromática del 60-30-10 con la interfaz Web.
    """
    return create_dark_metallic_blue_theme()
