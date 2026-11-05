import json
import re

def clean_markdown_json(raw_json: str) -> str:
    """
    Limpia una cadena que se espera que sea JSON pero que puede estar envuelta
    en un bloque de código Markdown (```json ... ```).
    """
    # Expresión regular para encontrar ```json ... ``` y capturar el contenido
    match = re.search(r'```json\s*([\s\S]+?)\s*```', raw_json, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_json.strip()

def validate_and_sanitize_json(raw_text: str) -> dict:
    """
    Toma una cadena de texto, la limpia de Markdown, e intenta parsearla como JSON.
    Si falla, devuelve un diccionario de error.
    """
    cleaned_text = clean_markdown_json(raw_text)
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # En el futuro, podría intentar corregir errores comunes de JSON.
        # Por ahora, si no es válido después de limpiar, se rechaza.
        raise ValueError("La salida de la IA no es un JSON válido después de la sanitización.")

def sanitize_plain_text(raw_text: str) -> str:
    """
    Sanitiza una salida de texto plano de la IA.
    Por ahora, simplemente elimina espacios en blanco al inicio y al final.
    """
    return raw_text.strip()
