from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.agents.corps.ventas_colonel import sales_agent_executor
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class SalesAgentInput(BaseModel):
    query: str
    # En el futuro, podríamos añadir un session_id para mantener el historial
    # session_id: str | None = None

class SalesAgentOutput(BaseModel):
    reply: str

@router.post("")
async def invoke_sales_agent(
    agent_in: SalesAgentInput
) -> SalesAgentOutput:
    """
    Public endpoint to interact with the AI Sales Agent.
    This endpoint is not protected by authentication to allow public access.
    """
    if not agent_in.query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La consulta (query) no puede estar vacía."
        )

    logger.info(f"Invocando al Agente de Ventas con la consulta: '{agent_in.query}'")

    try:
        # El executor es asíncrono si el LLM lo es.
        response_text = await sales_agent_executor.ainvoke(agent_in.query)
        logger.info(f"Respuesta generada por el agente: '{response_text}'")
        return SalesAgentOutput(reply=response_text)
    except Exception as e:
        logger.error(f"Error al invocar el agente de ventas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al procesar su solicitud."
        )
