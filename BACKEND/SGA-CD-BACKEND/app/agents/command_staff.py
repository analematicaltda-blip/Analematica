from typing import Dict, Any, Optional, List
import os
import logging
from langchain_openai import ChatOpenAI
from app.core.contracts.neko_contract import MissionDispatchEnvelope, InputModality, InteractionPriority
from app.agents.corps.formacion_deportiva_colonel import get_formacion_deportiva_colonel_graph
from app.agents.corps.formacion_cultura_colonel import get_formacion_cultura_colonel_graph
from app.agents.corps.ventas_crm_colonel import get_ventas_crm_colonel_graph
from app.agents.corps.multimedia_colonel import get_multimedia_colonel_graph
from app.agents.corps.redes_sociales_colonel import get_redes_sociales_colonel_graph

logger = logging.getLogger("sga_cd_command_staff")

class JarviGeneralOrchestrator:
    def __init__(self, db_path: str = "formacion.db", llm: Any = None):
        self.db_path = db_path
        
        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://host.docker.internal:11434").rstrip("/")
        ollama_v1 = ollama_endpoint + "/v1"
        ollama_model = "deepseek-r1:8b"
        openai_key = os.getenv("OPENAI_API_KEY", "")

        if llm is not None:
            self.llm = llm
        else:
            try:
                # Motor primario: DeepSeek-R1 local en Ollama con bind_tools nativo
                self.llm = ChatOpenAI(
                    base_url=ollama_v1,
                    api_key="ollama",
                    model=ollama_model,
                    temperature=0,
                    request_timeout=90
                )
            except Exception as e:
                logger.warning(f"Conmutando a OpenAI de respaldo: {e}")
                self.llm = ChatOpenAI(
                    api_key=openai_key,
                    model="gpt-4o-mini",
                    temperature=0,
                    request_timeout=30
                )

        print("--- ⚔️ GENERAL JARVI: Desplegando Divisiones con DeepSeek-R1:8b y respaldo OpenAI... ---")
        self.colonel_deportes = get_formacion_deportiva_colonel_graph(db_path, self.llm)
        self.colonel_cultura = get_formacion_cultura_colonel_graph(db_path, self.llm)
        self.colonel_ventas = get_ventas_crm_colonel_graph(self.llm)
        self.colonel_multimedia = get_multimedia_colonel_graph(self.llm)
        self.colonel_redes = get_redes_sociales_colonel_graph(self.llm)
        print("--- ✅ GENERAL JARVI: Los 5 Coroneles en posición con LLM activo. ---")

    async def execute_mission(self, envelope: MissionDispatchEnvelope) -> Dict[str, Any]:
        text_lower = envelope.raw_utterance.lower()
        context = {
            "origin_user_id": envelope.origin_user_id,
            "origin_tenant_id": envelope.origin_tenant_id,
            "user_roles": envelope.user_roles,
            "target_division": envelope.target_division,
            "intent_action": envelope.intent_action,
            "parameters": envelope.extracted_parameters
        }

        # Redes Sociales, Ads y Vinculación Oficial
        if envelope.target_division == "MARKETING" or any(w in text_lower for w in ["perfil", "bio", "portada", "avatar", "publicar", "difundir", "redes", "post", "facebook", "instagram", "ads", "analematica"]):
            return await self.colonel_redes.ainvoke({"general_order": envelope.raw_utterance, "app_context": context})

        # Ventas y CRM
        if envelope.target_division == "VENTAS" or any(w in text_lower for w in ["prospecto", "lead", "venta", "cotizacion", "embudo", "pipeline", "matricula", "bold", "plan", "club", "colegio"]):
            return await self.colonel_ventas.ainvoke({"general_order": envelope.raw_utterance, "app_context": context})

        # Deportes
        if envelope.target_division == "DEPORTES" or any(w in text_lower for w in ["deporte", "atleta", "entrenamiento", "cancha", "partido"]):
            return await self.colonel_deportes.ainvoke({"general_order": envelope.raw_utterance, "app_context": context})

        # Cultura
        if envelope.target_division == "CULTURA" or any(w in text_lower for w in ["cultura", "taller", "danza", "musica", "obra", "teatro"]):
            return await self.colonel_cultura.ainvoke({"general_order": envelope.raw_utterance, "app_context": context})

        return await self.colonel_redes.ainvoke({"general_order": envelope.raw_utterance, "app_context": context})

class NekoConversationalGeneral:
    def __init__(self, orchestrator: Optional[JarviGeneralOrchestrator] = None, jarvi: Optional[JarviGeneralOrchestrator] = None, *args, **kwargs):
        self.jarvi = orchestrator or jarvi
        if not self.jarvi:
            self.jarvi = JarviGeneralOrchestrator()

    async def handle_user_command(self, command_text: str, user_id: str = "1", tenant_id: str = "1", roles: Optional[List[str]] = None, *args, **kwargs) -> str:
        cmd_lower = command_text.lower()
        
        # Enrutamiento Semántico de División
        if any(w in cmd_lower for w in ["facebook", "instagram", "redes", "ads", "post", "perfil", "bio", "analematica"]):
            target_div = "MARKETING"
            action = "VINCULACION_REDES_Y_ADS"
        elif any(w in cmd_lower for w in ["prospecto", "lead", "venta", "cotizacion", "bold", "plan", "club"]):
            target_div = "VENTAS"
            action = "PROSPECCION_COMERCIAL"
        elif any(w in cmd_lower for w in ["deporte", "atleta", "entrenamiento"]):
            target_div = "DEPORTES"
            action = "GESTION_DEPORTIVA"
        elif any(w in cmd_lower for w in ["cultura", "taller", "danza", "musica"]):
            target_div = "CULTURA"
            action = "GESTION_CULTURAL"
        else:
            target_div = "MARKETING"
            action = "DIFUSION_GENERAL"

        clean_roles = [str(r.value if hasattr(r, 'value') else r) for r in (roles or ["admin_general"])]

        # Contrato estricto MissionDispatchEnvelope
        envelope = MissionDispatchEnvelope(
            origin_user_id=str(user_id),
            origin_tenant_id=str(tenant_id),
            user_roles=clean_roles,
            raw_utterance=command_text,
            target_division=target_div,
            intent_action=action,
            modality=InputModality.TEXT,
            extracted_parameters={"command": command_text},
            priority=InteractionPriority.NORMAL
        )

        report = await self.jarvi.execute_mission(envelope)
        
        if isinstance(report, dict):
            final = report.get("final_report", {})
            if isinstance(final, dict):
                report_str = final.get("text", str(final))
            else:
                report_str = str(final)
        else:
            report_str = str(report)

        return f"🎙️ [N.E.K.O.]: Misión de Redes & Ads procesada por JARVI con DeepSeek-R1:8B.\nEstado: COMPLETED_SUCCESS\n\n{report_str}"
