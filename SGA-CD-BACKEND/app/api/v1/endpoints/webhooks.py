from fastapi import APIRouter, Request, HTTPException, status, Query, BackgroundTasks
from app.core.config import settings
from app.whatsapp_handler.service import process_whatsapp_message
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/whatsapp")
def verify_webhook(
    request: Request,
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: int = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):
    """
    Verifies the webhook subscription with Meta.
    """
    logger.info("Recibida solicitud de verificación de webhook...")
    if hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN and hub_mode == "subscribe":
        logger.info("Verificación de webhook exitosa.")
        return hub_challenge

    logger.warning("Fallo en la verificación del webhook. Token no coincide.")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid verification token.",
    )


@router.post("/whatsapp")
async def receive_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming messages from WhatsApp users.
    """
    payload = await request.json()
    logger.info("Recibido payload de mensaje de WhatsApp.")

    # El procesamiento se realiza en segundo plano para responder a Meta rápidamente.
    # Esto evita timeouts si el agente de IA tarda en responder.
    background_tasks.add_task(process_whatsapp_message, payload)

    return {"status": "ok"}
