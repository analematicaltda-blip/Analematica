from langchain_core.tools import tool

@tool
def tool_publicar_red_social(plataforma: str, video_url: str, copy_texto: str) -> str:
    """Publica simultaneamente un video o post en YouTube, TikTok, Instagram, Facebook o LinkedIn."""
    return f"Publicacion enviada exitosamente a la plataforma '{plataforma}'. URL de recurso: {video_url}. Estado: PUBLICADO."

@tool
def tool_responder_mensaje_whatsapp(numero_destino: str, mensaje_respuesta: str) -> str:
    """Contesta automaticamente a un usuario o acudiente a traves del canal oficial de WhatsApp."""
    return f"Mensaje oficial de WhatsApp transmitido al numero {numero_destino}: '{mensaje_respuesta[:40]}...'"