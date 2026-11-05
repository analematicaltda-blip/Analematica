# Definimos algunas "reglas" de validación para redes sociales
SOCIAL_MEDIA_RULES = {
    'twitter': {'char_limit': 280},
    'instagram': {'char_limit': 2200},
    'facebook': {'char_limit': 63206},
}

def validate_social_post(platform: str, content: str) -> dict:
    """
    Valida el contenido de una publicación para una red social específica.
    Devuelve un diccionario con el resultado y posibles advertencias.
    """
    rules = SOCIAL_MEDIA_RULES.get(platform)
    if not rules:
        return {"error": f"Plataforma '{platform}' no soportada."}

    char_count = len(content)
    warnings = []

    # Simulación de truncamiento
    preview = content
    if char_count > rules['char_limit']:
        preview = content[:rules['char_limit']] + "..."
        warnings.append(f"El contenido excede el límite de {rules['char_limit']} caracteres y será truncado.")

    return {
        "platform": platform,
        "char_count": char_count,
        "limit": rules['char_limit'],
        "is_valid": char_count <= rules['char_limit'],
        "preview": preview,
        "warnings": warnings,
    }
