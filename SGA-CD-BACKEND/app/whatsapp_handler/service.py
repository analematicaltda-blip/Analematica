import requests
import json
import logging
import re

from app.core.config import settings
from app.agents.corps.ventas_colonel import sales_agent_executor  # Usamos el agente de ventas dedicado

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WHATSAPP_GRAPH_API_URL = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"


def _mask_phone_number(phone: str) -> str:
    """Enmascara números telefónicos para evitar la exposición en logs (ej. +57310***1234)."""
    if not phone or not isinstance(phone, str):
        return "***"
    clean = phone.strip()
    if len(clean) <= 6:
        return "***"
    return f"{clean[:5]}***{clean[-4:]}"


def _mask_bearer_token(token: str) -> str:
    """Enmascara tokens de acceso e identificadores confidenciales."""
    if not token or not isinstance(token, str):
        return "*****"
    if len(token) <= 8:
        return "*****"
    return f"{token[:4]}...{token[-4:]}"


def send_whatsapp_message(to: str, message: str):
    """
    Sends a text message to a WhatsApp user using enmascaramiento estricto de datos.
    """
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    masked_to = _mask_phone_number(to)
    masked_token = _mask_bearer_token(settings.WHATSAPP_API_TOKEN)

    # If using a placeholder token, log in test mode with masked sensitive parameters
    if "YOUR_WHATSAPP_API_TOKEN" in settings.WHATSAPP_API_TOKEN or settings.WHATSAPP_API_TOKEN == "test_token":
        logger.info("--- MODO DE PRUEBA WHATSAPP (DATOS ENMASCARADOS) ---")
        logger.info(f"Destino: {masked_to} | Token API: {masked_token}")
        logger.info(f"Longitud del mensaje: {len(message)} caracteres")
        return {"status": "success", "message": "Logged in test mode with masked payload."}

    try:
        response = requests.post(WHATSAPP_GRAPH_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Mensaje de WhatsApp enviado exitosamente a {masked_to}. HTTP Status: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        status_code = getattr(e.response, 'status_code', 503) if hasattr(e, 'response') and e.response else 503
        logger.error(f"[STD-ERR-{status_code}-WA-DISPATCH] Error al enviar mensaje de WhatsApp a {masked_to}: [Trazas de seguridad enmascaradas]")
        raise


async def process_whatsapp_message(payload: dict):
    """
    Processes an incoming WhatsApp message payload from a webhook with safe logging.
    """
    try:
        changes = payload.get("entry", [{}])[0].get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages or messages[0].get("type") != "text":
            logger.info("[WhatsApp Webhook] Mensaje recibido no es de texto o está vacío. Ignorando silenciosamente.")
            return

        message_object = messages[0]
        from_number = message_object.get("from")
        message_text = message_object.get("text", {}).get("body")

        if not from_number or not message_text:
            logger.error("[STD-ERR-400-WA-PAYLOAD] Payload de webhook inválido: Falta identificador 'from' o cuerpo 'text'.")
            return

        masked_sender = _mask_phone_number(from_number)
        logger.info(f"[WhatsApp Webhook] Consulta procesada desde {masked_sender} (Longitud de texto: {len(message_text)} caracteres)")

        # Invocar al agente de ventas de IA de forma segura
        reply_text = await sales_agent_executor.ainvoke(message_text)

        # Enviar la respuesta del agente de vuelta al usuario
        send_whatsapp_message(to=from_number, message=reply_text)

    except (IndexError, KeyError) as e:
        logger.error(f"[STD-ERR-422-WA-PARSE] Error de parseo en payload de webhook WhatsApp: {e}")
    except Exception as e:
        logger.error(f"[STD-ERR-500-WA-PROCESS] Error inesperado procesando mensaje de WhatsApp: [Excepción protegida]")
