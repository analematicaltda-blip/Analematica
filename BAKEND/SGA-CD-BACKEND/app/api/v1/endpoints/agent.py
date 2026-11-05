import re
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.core.rate_limiter import rate_limit
import speech_recognition as sr
from pydub import AudioSegment
import io
from app.agents.corps.formacion_cultura_colonel import get_formacion_cultura_colonel_graph
from langchain_openai import ChatOpenAI
from app.core.config import settings

router = APIRouter()

# --- Agent Initialization ---
db_path = "formacion.db"
# Ensure API key is available
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no está configurada en el archivo .env")
llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY)
cultura_colonel_agent = get_formacion_cultura_colonel_graph(db_path, llm)


def sanitize_prompt_for_ai(prompt: str) -> str:
    """
    Sanitizes prompts before sending to LLM providers by redacting sensitive data
    such as credit card numbers, passwords, Bearer tokens.
    """
    if not prompt:
        return prompt
    prompt = re.sub(r"\b(?:\d[ -]*?){13,19}\b", "[TARJETA_CREDITO_REDACTADA]", prompt)
    prompt = re.sub(r"Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", "[TOKEN_REDACTADO]", prompt)
    prompt = re.sub(r"(?i)(password|clave|contraseña)\s*[:=]\s*\S+", r"\1: [PASSWORD_REDACTADO]", prompt)
    return prompt


def build_scoped_thread_id(user_inquilino_id: int, user_id: int, client_thread_id: str | None) -> str:
    """
    Constructs an isolated, server-scoped thread_id that prevents cross-tenant and cross-user session access.
    Format: tenant_{inquilino_id}:user_{user_id}:session_{sanitized_session_id}
    """
    sanitized = "default"
    if client_thread_id:
        cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", str(client_thread_id))
        if cleaned:
            sanitized = cleaned[:64]
    return f"tenant_{user_inquilino_id}:user_{user_id}:session_{sanitized}"


async def run_agent(prompt: str, thread_id: str, area: str):
    """Helper function to run the appropriate agent with sanitized prompt."""
    if area != "Cultura":
        return {"text": f"El agente para el área '{area}' no está disponible.", "image_url": None}

    clean_prompt = sanitize_prompt_for_ai(prompt)
    config = {"configurable": {"thread_id": thread_id}}
    app_context = {"api": None}

    final_state = await cultura_colonel_agent.ainvoke(
        {"general_order": clean_prompt, "app_context": app_context},
        config=config
    )
    return final_state.get("final_report", {"text": "El agente no produjo un reporte.", "image_url": None})


@router.post("/invoke-voice", response_model=schemas.AgentOutput)
async def invoke_agent_by_voice(
    *,
    db: Session = Depends(deps.get_db),
    audio_file: UploadFile = File(...),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Invokes the AI agent by transcribing an audio file first.
    """
    recognizer = sr.Recognizer()
    try:
        audio_data = await audio_file.read()
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
        wav_data = io.BytesIO()
        audio_segment.export(wav_data, format="wav")
        wav_data.seek(0)

        with sr.AudioFile(wav_data) as source:
            audio = recognizer.record(source)

        transcribed_text = recognizer.recognize_google(audio, language="es-ES")
        print(f"Texto Transcrito: {transcribed_text}")

        # Always build server-scoped thread_id derived from authenticated JWT identity
        scoped_thread_id = build_scoped_thread_id(
            user_inquilino_id=current_user.inquilino_id,
            user_id=current_user.id,
            client_thread_id="voice_session"
        )
        area = "Cultura"

        report = await run_agent(transcribed_text, scoped_thread_id, area)
        return report

    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="No se pudo entender el audio.")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error en el servicio de reconocimiento de voz: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo de audio: {e}")


@router.post("/invoke", response_model=schemas.AgentOutput, dependencies=[Depends(rate_limit("ai_agent_invoke", max_requests=15, window_seconds=60))])
async def invoke_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_in: schemas.AgentInput,
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Invokes the appropriate AI agent based on the user's area.
    """
    if agent_in.area not in ["Cultura", "Deportes"]:
        raise HTTPException(status_code=400, detail="Area must be 'Cultura' or 'Deportes'.")

    # Construct secure server-enforced thread_id
    scoped_thread_id = build_scoped_thread_id(
        user_inquilino_id=current_user.inquilino_id,
        user_id=current_user.id,
        client_thread_id=agent_in.thread_id
    )

    print(f"Agent invoked for tenant {current_user.inquilino_id}, user {current_user.id}, scoped thread {scoped_thread_id}")

    report = await run_agent(agent_in.prompt, scoped_thread_id, agent_in.area)

    return report
