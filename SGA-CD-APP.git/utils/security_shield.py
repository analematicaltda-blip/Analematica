"""
Security Shield & Input Sanitization Engine for SGA-CD Python Flet Applications
(Desktop & Mobile distributions)
SGA-CD System Architecture - Dark Metallic Blue
"""

import re
import html
from typing import Any, Dict, List, Union


def sanitize_input_for_flet(text: Any) -> str:
    """
    Sanitiza de forma estricta cualquier parámetro o cadena ingresada por usuarios
    (Estudiantes, Profesores, Entidades Públicas/Privadas) antes de procesarlo en
    elementos gráficos de Flet o enviarlo a FastAPI.

    Previene inyecciones HTML/XSS, scripts maliciosos y caracteres nulos.
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    # 1. Eliminar etiquetas de script e iframe explícitas y protocolos javascript:
    text = re.sub(r'(?i)<script\b[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)<iframe\b[^>]*>.*?</iframe>', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)javascript:', '', text)
    text = re.sub(r'(?i)on\w+\s*=', '', text)  # Eliminar event handlers inline tipo onload=, onclick=

    # 2. Escapar caracteres HTML potencialmente peligrosos (<, >, &, ", ')
    escaped = html.escape(text, quote=True)

    # 3. Eliminar caracteres de control y nulos que puedan corromper hilos o SQL
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', escaped)

    return cleaned.strip()


def sanitize_dict_inputs(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recorre recursivamente un diccionario sanitizando todas las cadenas contenidas.
    """
    sanitized = {}
    for key, value in data.items():
        clean_key = sanitize_input_for_flet(key)
        if isinstance(value, str):
            sanitized[clean_key] = sanitize_input_for_flet(value)
        elif isinstance(value, dict):
            sanitized[clean_key] = sanitize_dict_inputs(value)
        elif isinstance(value, list):
            sanitized[clean_key] = [
                sanitize_input_for_flet(v) if isinstance(v, str)
                else sanitize_dict_inputs(v) if isinstance(v, dict)
                else v
                for v in value
            ]
        else:
            sanitized[clean_key] = value
    return sanitized


def mask_sensitive_token(token: str) -> str:
    """
    Enmascara un token JWT o secreto conservando solo los primeros y últimos 4 caracteres.
    """
    if not token or not isinstance(token, str):
        return "*****"
    if len(token) <= 10:
        return "*****"
    return f"{token[:4]}...{token[-4:]}"


def format_masked_error_code(status_code: int, detail: str = "") -> str:
    """
    Formatea el código de error estandarizado para visualización segura en Flet.
    Ejemplo: STD-ERR-401-UNAUTHORIZED
    """
    code_map = {
        400: "STD-ERR-400-BAD-REQUEST",
        401: "STD-ERR-401-UNAUTHORIZED",
        403: "STD-ERR-403-FORBIDDEN",
        404: "STD-ERR-404-NOT-FOUND",
        405: "STD-ERR-405-METHOD-NOT-ALLOWED",
        408: "STD-ERR-408-REQUEST-TIMEOUT",
        429: "STD-ERR-429-RATE-LIMITED",
        500: "STD-ERR-500-INTERNAL-ERROR",
        502: "STD-ERR-502-BAD-GATEWAY",
        503: "STD-ERR-503-SERVICE-UNAVAILABLE",
        504: "STD-ERR-504-GATEWAY-TIMEOUT"
    }
    return code_map.get(status_code, f"STD-ERR-{status_code}-UNKNOWN")
